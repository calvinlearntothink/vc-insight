
from dotenv import load_dotenv
load_dotenv(override=True)

import os
import subprocess
import requests
import time

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send(text):
    requests.post(f"{BASE_URL}/sendMessage", json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    })

def run_agent(mode="all"):
    """agent.py 실행"""
    env = os.environ.copy()
    agent_path = os.path.join(os.path.dirname(__file__), "agent.py")
    env["AGENT_MODE"] = mode
    result = subprocess.Popen(
        ["python3", agent_path],
        env=env,
        cwd=os.path.dirname(__file__),
    )
    return result

def get_updates(offset=None):
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    resp = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=35)
    return resp.json()

def handle_command(text):
    text = text.strip().lower()
    if text == "/today":
        send("⏳ 오늘 브리핑 시작합니다...")
        run_agent("all")
    elif text == "/blog":
        send("⏳ 블로그 수집 시작합니다...")
        run_agent("blog")
    elif text == "/tweets":
        send("⏳ 트윗 브리핑 시작합니다...")
        run_agent("tweets")
    elif text == "/status":
        log_path = os.path.join(os.path.dirname(__file__), "../agent.log")
        try:
            with open(log_path) as f:
                lines = f.readlines()
            last = [l for l in lines if "완료" in l or "시작" in l][-3:]
            send("📋 *최근 실행 로그*\n" + "".join(last))
        except:
            send("로그 없음")
    elif text == "/help":
        send("""*VC Intel Bot 명령어*

/today — 지금 바로 전체 실행 (블로그 + 트윗)
/blog — 블로그만 수집
/tweets — 트윗 브리핑만
/status — 마지막 실행 상태
/help — 도움말""")

def main():
    send("🤖 VC Intel Bot 시작됨")
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                text = msg.get("text", "")
                chat_id = str(msg.get("chat", {}).get("id", ""))
                if chat_id == TELEGRAM_CHAT_ID and text.startswith("/"):
                    handle_command(text)
        except Exception as e:
            print(f"오류: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
