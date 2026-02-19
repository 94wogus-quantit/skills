import queue
import subprocess
import threading
import time
import urllib.request

from mcp.server.fastmcp import FastMCP
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout

mcp = FastMCP("youtube-ask")

# macOS/Linux/Windows Chrome 실행 경로 후보
_CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
    "/Applications/Chromium.app/Contents/MacOS/Chromium",             # macOS Chromium
    "/usr/bin/google-chrome",                                          # Linux
    "/usr/bin/chromium-browser",                                       # Linux Chromium
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",         # Windows
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",   # Windows 32bit
]

# ─── Playwright 전용 스레드 ────────────────────────────────────────────────
# FastMCP는 asyncio 루프에서 실행되므로 Playwright Sync API를 직접 호출 불가.
# 전용 스레드에서 모든 Playwright 작업을 처리한다.

_task_queue: queue.Queue = queue.Queue()
_pw_thread: threading.Thread | None = None

# 세션 상태 — Playwright 전용 스레드 내에서만 접근
_pw = None
_page: Page | None = None


def _playwright_worker() -> None:
    """Playwright 전용 스레드: 큐에서 작업을 꺼내 실행한다."""
    while True:
        item = _task_queue.get()
        if item is None:  # 종료 신호
            break
        fn, result_q = item
        try:
            result_q.put(("ok", fn()))
        except Exception as exc:
            result_q.put(("err", exc))


def _ensure_pw_thread() -> None:
    global _pw_thread
    if _pw_thread is None or not _pw_thread.is_alive():
        _pw_thread = threading.Thread(target=_playwright_worker, daemon=True)
        _pw_thread.start()


def _run(fn):
    """fn()을 Playwright 전용 스레드에서 실행하고 결과를 반환한다."""
    _ensure_pw_thread()
    result_q: queue.SimpleQueue = queue.SimpleQueue()
    _task_queue.put((fn, result_q))
    status, value = result_q.get()
    if status == "err":
        raise value
    return value


# ─── 내부 헬퍼 (Playwright 전용 스레드 내에서만 호출) ─────────────────────

def _is_cdp_running(cdp_port: int) -> bool:
    try:
        urllib.request.urlopen(f"http://localhost:{cdp_port}/json/version", timeout=2)
        return True
    except Exception:
        return False


def _find_chrome() -> str | None:
    import os
    for path in _CHROME_PATHS:
        if os.path.isfile(path):
            return path
    return None


def _launch_chrome(cdp_port: int) -> None:
    chrome = _find_chrome()
    if not chrome:
        raise ValueError(
            "Chrome을 찾을 수 없습니다. Chrome을 직접 실행해주세요:\n"
            f"  chrome --remote-debugging-port={cdp_port}"
        )
    subprocess.Popen(
        [chrome, f"--remote-debugging-port={cdp_port}", "--no-first-run"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(20):
        if _is_cdp_running(cdp_port):
            return
        time.sleep(0.5)
    raise ValueError(f"Chrome을 실행했지만 CDP 포트 {cdp_port}가 열리지 않았습니다")


def _get_or_init_page(cdp_port: int) -> Page:
    global _pw, _page

    if _page is not None:
        try:
            _page.title()
            return _page
        except Exception:
            _page = None
            if _pw:
                try:
                    _pw.stop()
                except Exception:
                    pass
            _pw = None

    if not _is_cdp_running(cdp_port):
        _launch_chrome(cdp_port)

    try:
        _pw = sync_playwright().start()
        browser = _pw.chromium.connect_over_cdp(f"http://localhost:{cdp_port}")
    except Exception as e:
        _pw = None
        raise ValueError(f"Chrome CDP 연결에 실패했습니다 (포트: {cdp_port}): {e}")

    _page = None
    if browser.contexts:
        for ctx in browser.contexts:
            for pg in ctx.pages:
                try:
                    u = pg.url
                    if not u.startswith("chrome") and not u.startswith("devtools"):
                        _page = pg
                        break
                except Exception:
                    pass
            if _page:
                break

    if _page is None:
        if browser.contexts:
            _page = browser.contexts[0].new_page()
        else:
            _page = browser.new_context().new_page()

    return _page


# ─── MCP 도구 ─────────────────────────────────────────────────────────────

@mcp.tool()
def open_ask_panel(url: str, cdp_port: int = 9222, timeout_ms: int = 30000) -> dict:
    """
    YouTube 영상 페이지로 이동하고 Ask(질문하기) 패널을 엽니다.
    한 번 호출 후 ask_video()로 여러 번 질문할 수 있습니다.

    Args:
        url: YouTube 영상 URL (예: https://www.youtube.com/watch?v=xxxxx)
        cdp_port: Chrome CDP 포트 (기본: 9222)
        timeout_ms: 패널 로드 대기 최대 시간 ms (기본: 30000)

    Returns:
        {"status": "ok", "url": "...", "message": "Ask 패널이 열렸습니다"}
    """
    def work():
        global _page
        page = _get_or_init_page(cdp_port)
        page.goto(url, wait_until="domcontentloaded")

        try:
            page.wait_for_selector(
                'button[aria-label="질문하기"], button[aria-label="Ask"], button[aria-label="추가 작업"]',
                timeout=15000,
            )
        except PlaywrightTimeout:
            raise ValueError(f"이 영상에서 Ask 기능이 지원되지 않습니다: {url}")

        ask_button = page.query_selector('button[aria-label="질문하기"], button[aria-label="Ask"]')
        if ask_button and ask_button.is_visible():
            ask_button.click()
        else:
            more_button = page.query_selector('button[aria-label="추가 작업"]')
            if not more_button:
                raise ValueError(f"이 영상에서 Ask 기능이 지원되지 않습니다: {url}")
            more_button.click()
            try:
                page.wait_for_selector("ytd-menu-popup-renderer", timeout=5000)
            except PlaywrightTimeout:
                raise ValueError(f"이 영상에서 Ask 기능이 지원되지 않습니다: {url}")
            menu_item = page.query_selector("ytd-menu-service-item-renderer.iron-selected")
            if not menu_item:
                menu_item = page.query_selector(
                    'xpath=//yt-formatted-string[contains(text(),"질문하기") or contains(text(),"Ask")]'
                )
            if not menu_item:
                raise ValueError(f"이 영상에서 Ask 기능이 지원되지 않습니다: {url}")
            menu_item.click()

        try:
            page.wait_for_selector(
                'ytd-engagement-panel-section-list-renderer'
                '[target-id="PAyouchat"]'
                '[visibility="ENGAGEMENT_PANEL_VISIBILITY_EXPANDED"]',
                timeout=timeout_ms,
            )
        except PlaywrightTimeout:
            raise ValueError(f"Ask 패널이 열리지 않았습니다: {url}")

        _page = page
        return {"status": "ok", "url": url, "message": "Ask 패널이 열렸습니다"}

    return _run(work)


@mcp.tool()
def ask_video(question: str, timeout_ms: int = 30000) -> dict:
    """
    열린 Ask 패널에서 YouTube AI에게 질문합니다.
    먼저 open_ask_panel()로 패널을 열어야 합니다.

    Args:
        question: AI에게 할 질문
        timeout_ms: 응답 대기 최대 시간 ms (기본: 30000)

    Returns:
        {"answer": "...", "chips": ["추천질문1", "추천질문2"]}
    """
    def work():
        global _page
        if _page is None:
            raise ValueError("open_ask_panel()을 먼저 호출해주세요")
        try:
            _page.title()
        except Exception:
            _page = None
            raise ValueError("페이지 연결이 끊겼습니다. open_ask_panel()을 다시 호출해주세요")

        page = _page

        input_el = page.query_selector("textarea.chatInputViewModelChatInput")
        if not input_el:
            raise ValueError("Ask 패널이 열려있지 않습니다. open_ask_panel()을 먼저 호출해주세요")

        textarea = page.wait_for_selector("textarea.chatInputViewModelChatInput", timeout=10000)
        textarea.click()
        page.keyboard.type(question, delay=30)

        initial_md_count = len(page.query_selector_all("markdown-div"))
        initial_chips_count = len(page.query_selector_all("button.ytwYouChatChipsDataChip"))

        page.keyboard.press("Enter")

        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            if len(page.query_selector_all("markdown-div")) > initial_md_count:
                break
            time.sleep(0.5)
        else:
            raise ValueError(f"AI 응답 대기 시간 초과 ({timeout_ms}ms)")

        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            if len(page.query_selector_all("button.ytwYouChatChipsDataChip")) > initial_chips_count:
                break
            time.sleep(0.5)
        else:
            raise ValueError(f"AI 응답 완성 대기 시간 초과 ({timeout_ms}ms)")

        responses = page.query_selector_all("markdown-div")
        if not responses:
            raise ValueError("AI 응답을 찾을 수 없습니다")
        answer_text = responses[-1].inner_text()

        chips = [
            c.inner_text()
            for c in page.query_selector_all('button.ytwYouChatChipsDataChip[data-disabled="false"]')
        ]

        return {"answer": answer_text, "chips": chips}

    return _run(work)


@mcp.tool()
def close_session() -> dict:
    """
    현재 Playwright 세션을 종료합니다.
    더 이상 질문하지 않을 때 호출하세요.

    Returns:
        {"status": "ok", "message": "세션이 종료되었습니다"}
    """
    def work():
        global _pw, _page
        _page = None
        if _pw:
            try:
                _pw.stop()
            except Exception:
                pass
            _pw = None
        return {"status": "ok", "message": "세션이 종료되었습니다"}

    return _run(work)


if __name__ == "__main__":
    mcp.run()
