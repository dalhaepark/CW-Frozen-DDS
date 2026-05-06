import os
from playwright.sync_api import sync_playwright
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def capture_and_send():
    # 1. 환경변수에서 보안 값 가져오기
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    channel_id = os.environ.get("SLACK_CHANNEL_ID")
    
    # 캡처할 구글 앱스 스크립트 웹앱 주소
    target_url = "https://script.google.com/a/macros/kurlycorp.com/s/AKfycbxOQI41Teb26q4mCQUprTiGCJcymdJl5EM3nBLyRmIRJ0PPVILMoENqYvGoETyceilarA/exec"
    screenshot_path = "screenshot.png"

    print("웹페이지 접속 및 캡처를 시작합니다...")
    
    with sync_playwright() as p:
        # 브라우저 실행
        browser = p.chromium.launch(headless=True)
        
        # [수정] 화면 배율을 1920x1080(FHD)으로 고정 설정
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # [수정] 페이지 로딩 대기 시간 및 기준 변경 (60초 타임아웃)
        try:
            page.goto(target_url, wait_until="load", timeout=60000)
            
            # [수정] 데이터 로딩을 위해 추가로 5초간 더 대기
            print("데이터 로딩을 위해 5초간 대기 중...")
            page.wait_for_timeout(5000)
            
            # [추가] 상단 구글 배너(iframe) 제거 스크립트 실행
            print("상단 배너 제거 중...")
            page.evaluate("""
                const banners = document.querySelectorAll('iframe');
                banners.forEach(b => {
                    if (b.src.includes('user_content')) {
                        b.style.display = 'none';
                    }
                });
                document.body.style.top = '0';
            """)
            
            # 스크린샷 저장 (1920 너비 기준 전체 페이지)
            page.screenshot(path=screenshot_path, full_page=True)
            print("캡처 완료!")
            
        except Exception as e:
            print(f"캡처 중 에러 발생: {e}")
        
        browser.close()

    # 2. 슬랙으로 이미지 전송
    print("슬랙으로 이미지를 전송합니다...")
    client = WebClient(token=slack_token)
    try:
        response = client.files_upload_v2(
            channel=channel_id,
            file=screenshot_path,
            title="웹앱 모니터링 캡처 (1920x1080)",
            initial_comment="현재 웹앱의 화면입니다. 📸 (배너 제거 및 해상도 최적화 완료)"
        )
        print("전송 성공!")
    except SlackApiError as e:
        print(f"전송 실패: {e.response['error']}")

if __name__ == "__main__":
    capture_and_send()
