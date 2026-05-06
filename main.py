import os
from playwright.sync_api import sync_playwright
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def capture_and_send():
    # 환경변수에서 값 가져오기
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    channel_id = os.environ.get("SLACK_CHANNEL_ID")
    target_url = "https://script.google.com/a/macros/kurlycorp.com/s/AKfycbxOQI41Teb26q4mCQUprTiGCJcymdJl5EM3nBLyRmIRJ0PPVILMoENqYvGoETyceilarA/exec" # 캡처할 웹앱 URL 입력
    screenshot_path = "screenshot.png"

    # 1. 웹 화면 캡처 (Playwright 사용)
    print("웹페이지 캡처를 시작합니다...")
    with sync_playwright() as p:
        # headless=True로 설정하면 브라우저 창을 띄우지 않고 백그라운드에서 실행됩니다.
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 웹페이지 로딩 대기 (필요시 wait_until 옵션 조정 가능)
        page.goto(target_url, wait_until="load", timeout=60000)
        page.wait_for_timeout(5000) 
        page.screenshot(path=screenshot_path, full_page=True)
        # 스크린샷 저장
        page.screenshot(path=screenshot_path, full_page=True)
        browser.close()
    print("캡처 완료!")

    # 2. 슬랙으로 전송
    print("슬랙으로 이미지를 전송합니다...")
    client = WebClient(token=slack_token)
    try:
        response = client.files_upload_v2(
            channel=channel_id,
            file=screenshot_path,
            title="웹앱 모니터링 캡처",
            initial_comment="현재 웹앱의 화면입니다. :camera_with_flash:"
        )
        print("전송 성공!")
    except SlackApiError as e:
        print(f"전송 실패: {e.response['error']}")

if __name__ == "__main__":
    capture_and_send()
