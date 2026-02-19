import subprocess
import sys
import time
import urllib.request

from mcp.server.fastmcp import FastMCP
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout

mcp = FastMCP("youtube-ask")

# 세션 상태 - MCP 서버가 살아있는 동안 유지
_pw = None
_page: Page | None = None

# macOS/Linux/Windows Chrome 실행 경로 후보
_CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
    "/Applications/Chromium.app/Contents/MacOS/Chromium",             # macOS Chromium
    "/usr/bin/google-chrome",                                          # Linux
    "/usr/bin/chromium-browser",                                       # Linux Chromium
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",         # Windows
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",   # Windows 32bit
]


def _is_cdp_running(cdp_port: int) -> bool:
    """CDP 포트가 이미 열려있는지 확인."""
    try:
        urllib.request.urlopen(f"http://localhost:{cdp_port}/json/version", timeout=2)
        return True
    except Exception:
        return False


def _find_chrome() -> str | None:
    """시스템에 설치된 Chrome 실행 파일 경로 반환."""
    import os
    for path in _CHROME_PATHS:
        if os.path.isfile(path):
            return path
    return None


def _launch_chrome(cdp_port: int) -> None:
    """Chrome을 CDP 모드로 백그라운드 실행."""
    chrome = _find_chrome()
    if not chrome:
        raise ValueError(
            "Chrome을 찾을 수 없습니다. Chrome을 설치하거나 직접 실행해주세요:\n"
            f"  chrome --remote-debugging-port={cdp_port}"
        )
    subprocess.Popen(
        [chrome, f"--remote-debugging-port={cdp_port}", "--no-first-run"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # 포트 열릴 때까지 최대 10초 대기
    for _ in range(20):
        if _is_cdp_running(cdp_port):
            return
        time.sleep(0.5)
    raise ValueError(
        f"Chrome을 실행했지만 CDP 포트 {cdp_port}가 열리지 않았습니다"
    )


def _get_or_init_page(cdp_port: int) -> Page:
    """기존 CDP 연결 페이지를 반환하거나, 없으면 새로 연결한다."""
    global _pw, _page

    # 이미 연결된 페이지가 유효한지 확인
    if _page is not None:
        try:
            _page.title()  # 살아있는지 ping
            return _page
        except Exception:
            _page = None
            if _pw:
                try:
                    _pw.stop()
                except Exception:
                    pass
            _pw = None

    # CDP 포트가 열려있지 않으면 Chrome 자동 실행
    cdp_check = _is_cdp_running(cdp_port)
    if not cdp_check:
        _launch_chrome(cdp_port)

    # 새 연결
    try:
        _pw = sync_playwright().start()
        browser = _pw.chromium.connect_over_cdp(f"http://localhost:{cdp_port}")
    except Exception as e:
        _pw = None
        raise ValueError(
            f"Chrome CDP 연결에 실패했습니다 (포트: {cdp_port}, cdp_check={cdp_check}): {type(e).__name__}: {e}"
        )

    # 일반 웹 페이지 찾기 (chrome-error://, chrome://, devtools:// 등 특수 페이지 제외)
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
        # 일반 페이지가 없으면 새로 생성
        if browser.contexts:
            _page = browser.contexts[0].new_page()
        else:
            context = browser.new_context()
            _page = context.new_page()

    return _page


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
    global _page

    page = _get_or_init_page(cdp_port)

    # 영상 페이지로 이동
    page.goto(url, wait_until="domcontentloaded")

    # Ask 버튼 로드 대기 (SPA 특성상 필수)
    try:
        page.wait_for_selector(
            'button[aria-label="질문하기"], button[aria-label="Ask"], button[aria-label="추가 작업"]',
            timeout=15000
        )
    except PlaywrightTimeout:
        raise ValueError(f"이 영상에서 Ask 기능이 지원되지 않습니다: {url}")

    # 버튼 탐지 및 클릭 (2분기)
    ask_button = page.query_selector(
        'button[aria-label="질문하기"], button[aria-label="Ask"]'
    )
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

    # 패널 로드 대기
    try:
        page.wait_for_selector(
            'ytd-engagement-panel-section-list-renderer'
            '[target-id="PAyouchat"]'
            '[visibility="ENGAGEMENT_PANEL_VISIBILITY_EXPANDED"]',
            timeout=timeout_ms
        )
    except PlaywrightTimeout:
        raise ValueError(f"Ask 패널이 열리지 않았습니다: {url}")

    _page = page
    return {"status": "ok", "url": url, "message": "Ask 패널이 열렸습니다"}


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
    global _page

    if _page is None:
        raise ValueError("open_ask_panel()을 먼저 호출해주세요")

    try:
        _page.title()  # 페이지가 살아있는지 확인
    except Exception:
        _page = None
        raise ValueError("페이지 연결이 끊겼습니다. open_ask_panel()을 다시 호출해주세요")

    page = _page

    # 입력창 확인 (패널이 열려있는지)
    input_el = page.query_selector("textarea.chatInputViewModelChatInput")
    if not input_el:
        raise ValueError("Ask 패널이 열려있지 않습니다. open_ask_panel()을 먼저 호출해주세요")

    # 질문 입력 (keyboard.type으로 Polymer 이벤트 정상 트리거)
    textarea = page.wait_for_selector("textarea.chatInputViewModelChatInput", timeout=10000)
    textarea.click()
    page.keyboard.type(question, delay=30)

    # 전송 전 초기 개수 기억 (반드시 Enter 전에 기록)
    import time as _time
    initial_md_count = len(page.query_selector_all('markdown-div'))
    initial_chips_count = len(page.query_selector_all("button.ytwYouChatChipsDataChip"))

    # Enter 키로 전송
    page.keyboard.press('Enter')

    # 새 markdown-div(AI 답변) 등장 대기 (Trusted Types CSP 우회: polling)
    deadline = _time.time() + timeout_ms / 1000
    while _time.time() < deadline:
        if len(page.query_selector_all('markdown-div')) > initial_md_count:
            break
        _time.sleep(0.5)
    else:
        raise ValueError(f"AI 응답 대기 시간 초과 ({timeout_ms}ms)")

    # AI 응답 완성 대기 (streaming: chips 개수 증가로 완성 감지)
    deadline = _time.time() + timeout_ms / 1000
    while _time.time() < deadline:
        if len(page.query_selector_all("button.ytwYouChatChipsDataChip")) > initial_chips_count:
            break
        _time.sleep(0.5)
    else:
        raise ValueError(f"AI 응답 완성 대기 시간 초과 ({timeout_ms}ms)")

    # 마지막 markdown-div = 방금 받은 AI 답변
    responses = page.query_selector_all('markdown-div')
    if not responses:
        raise ValueError("AI 응답을 찾을 수 없습니다")
    answer_text = responses[-1].inner_text()

    # follow-up chips 추출
    chips = [
        c.inner_text()
        for c in page.query_selector_all(
            'button.ytwYouChatChipsDataChip[data-disabled="false"]'
        )
    ]

    return {"answer": answer_text, "chips": chips}


@mcp.tool()
def close_session() -> dict:
    """
    현재 Playwright 세션을 종료합니다.
    더 이상 질문하지 않을 때 호출하세요.

    Returns:
        {"status": "ok", "message": "세션이 종료되었습니다"}
    """
    global _pw, _page

    _page = None
    if _pw:
        try:
            _pw.stop()
        except Exception:
            pass
        _pw = None

    return {"status": "ok", "message": "세션이 종료되었습니다"}


if __name__ == "__main__":
    mcp.run()
