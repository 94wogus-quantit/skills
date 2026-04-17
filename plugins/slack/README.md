# Slack MCP Plugin

Slack 메시지 검색, 히스토리, 스레드 조회를 위한 MCP 서버 플러그인.

## 설치

```bash
/plugin install wogus-plugins:slack
```

## 환경변수

```bash
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
```

[Slack Bot Token 발급 방법](https://api.slack.com/authentication/token-types#bot)

## MCP 서버

- **slack**: Slack MCP Server (korotovsky)
  - 패키지: `slack-mcp-server`
  - 기능: conversations_history, conversations_replies, conversations_search_messages, channels_list
