import os
import subprocess
from datetime import datetime
import pytz
from playwright.sync_api import sync_playwright
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def capture_and_send():
    # 1. 현재 시간 계산 (한국 시간 기준)
    korea_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(korea_tz)
    current_hour = now.strftime("%H") # 24시간 형식의 시간 (예: 20)
    
    # 전송할 메시지 문구 설정
    slack_message = f"{current_hour}시 기준 창원 냉동OB팀, 생산현황입니다."

    # [추가] 깃허브 서버에 한글 폰트 강제 설치
    print("한글 폰트 설치 중...")
    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "fonts-nanum"], check=True)
        print("한글 폰트 설치 완료!")
    except Exception as e:
        print(f"폰트 설치 중 알림: {e}")

    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    channel_id = os.environ.get("SLACK_CHANNEL_ID")
    target_url = "https://script.google.com/a/macros/kurlycorp.com/s/AKfycbxOQI41Teb26q4mCQUprTiGCJcymdJl5EM3nBLyRmIRJ0PPVILMoENqYvGoETyceilarA/exec"
    screenshot_path = "screenshot.png"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        try:
            print("웹페이지 접속 중...")
            page.goto(target_url, wait_until="load", timeout=60000)
            page.wait_for_timeout(7000) 

            print("상단 배너 및 장애 요소 제거 중...")
            page.evaluate("""
                () => {
                    const iframes = document.querySelectorAll('iframe');
                    iframes.forEach(f => {
                        if (f.src.includes('googlegroups.com') || f.src.includes('static') || f.offsetHeight < 100) {
                            f.style.display = 'none';
                        }
                    });
                    const bannerSelectors = ['.docs-ml-header-item', '.script-application-sidebar', 'table.goog-ws-fixed-header'];
                    bannerSelectors.forEach(s => {
                        const el = document.querySelector(s);
                        if (el) el.style.display = 'none';
                    });
                    document.body.style.paddingTop = '0';
                    document.body.style.marginTop = '0';
                }
            """)
            
            page.screenshot(path=screenshot_path, full_page=False)
            print("캡처 완료!")
            
        except Exception as e:
            print(f"에러 발생: {e}")
        
        browser.close()

    # 2. 슬랙 전송
    client = WebClient(token=slack_token)
    try:
        client.files_upload_v2(
            channel=channel_id,
            file=screenshot_path,
            title=f"생산현황_{now.strftime('%Y%m%d_%H%M')}",
            initial_comment=slack_message  # <-- 요청하신 시간 메시지가 여기 들어갑니다!
        )
        print(f"전송 성공: {slack_message}")
    except SlackApiError as e:
        print(f"전송 실패: {e.response['error']}")

if __name__ == "__main__":
    capture_and_send()
