import os
import subprocess
from playwright.sync_api import sync_playwright
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def capture_and_send():
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
        # 1920x1080 설정 유지
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        try:
            print("웹페이지 접속 중...")
            page.goto(target_url, wait_until="load", timeout=60000)
            page.wait_for_timeout(7000) # 로딩 시간을 조금 더 늘렸습니다(7초)

            # [강화] 배너 제거 및 화면 정리 스크립트
            print("상단 배너 및 장애 요소 제거 중...")
            page.evaluate("""
                () => {
                    // 1. 모든 iframe(배너 포함)을 찾아 숨김
                    const iframes = document.querySelectorAll('iframe');
                    iframes.forEach(f => {
                        if (f.src.includes('googlegroups.com') || f.src.includes('static') || f.offsetHeight < 100) {
                            f.style.display = 'none';
                        }
                    });
                    
                    // 2. 구글 앱스 스크립트 특유의 배너 컨테이너 제거
                    const bannerSelectors = [
                        '.docs-ml-header-item', 
                        '.script-application-sidebar',
                        'table.goog-ws-fixed-header'
                    ];
                    bannerSelectors.forEach(s => {
                        const el = document.querySelector(s);
                        if (el) el.style.display = 'none';
                    });

                    // 3. 페이지 상단 여백 강제 제거
                    document.body.style.paddingTop = '0';
                    document.body.style.marginTop = '0';
                }
            """)
            
            # 스크린샷 저장
            page.screenshot(path=screenshot_path, full_page=False) # 한 화면만 깔끔하게 찍기 위해 False 권장
            print("캡처 완료!")
            
        except Exception as e:
            print(f"에러 발생: {e}")
        
        browser.close()

    # 슬랙 전송
    client = WebClient(token=slack_token)
    try:
        client.files_upload_v2(
            channel=channel_id,
            file=screenshot_path,
            title="최종 최적화 대시보드",
            initial_comment="✅ 한글 폰트 적용 및 배너 제거가 완료된 화면입니다."
        )
        print("슬랙 전송 성공!")
    except SlackApiError as e:
        print(f"전송 실패: {e.response['error']}")

if __name__ == "__main__":
    capture_and_send()
