import network
import time
import urequests  
from wlan_config import WLANConfig  # 2. (필수) wlan_config.py 파일이 기기에 있어야 함


# 1. 설치할 라이브러리 목록 (파일명: 깃허브 주소)
# 이 목록만 수정하시면 됩니다.
libraries_to_install = {
    'DHT11.py': 'https://github.com/SeoMinKey/Pico_edu/blob/main/lib/DHT11.py',
    'ahtx0.py': 'https://github.com/SeoMinKey/Pico_edu/blob/main/lib/ahtx0.py',
    'bh1750.py': 'https://github.com/SeoMinKey/Pico_edu/blob/main/lib/bh1750.py',
    'ds3231_port.py': 'https://github.com/SeoMinKey/Pico_edu/blob/main/lib/ds3231_port.py',
    'notes.py': 'https://github.com/SeoMinKey/Pico_edu/blob/main/lib/notes.py',
    # 여기에 계속 추가...
}
# --- 4. 깃허브 URL 변환 함수 ---
def get_raw_url(github_url):
    """일반 GitHub URL을 Raw 콘텐츠 URL로 변환합니다."""
    return github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

# --- 5. 개별 라이브러리 설치 함수 ---
def install_library(filename, url):
    """지정된 URL에서 파일을 다운로드하여 저장합니다."""
    raw_url = get_raw_url(url)
    print(f"-> '{filename}' 다운로드 시도...")
    
    try:
        response = urequests.get(raw_url)
        if response.status_code == 200:
            with open('/lib/'+filename, 'w') as f:
                f.write(response.text)
            print(f"   [성공] '{filename}' 저장 완료.")
        else:
            # -6 오류는 보통 여기서 발생 (DNS 조회 실패)
            print(f"   [실패] HTTP 상태: {response.status_code}")
        
        response.close() # 리소스 정리
        
    except Exception as e:
        # 또는 여기서 -6 오류 발생 (네트워크 연결 오류)
        print(f"   [오류] 처리 중 에러 발생: {e}")

# --- 6. Wi-Fi 연결 시도 ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

ssid, password = WLANConfig.get_wlan()
print(f"Wi-Fi 연결 시도: {ssid}...")
wlan.connect(ssid, password)

# 연결될 때까지 최대 10초 대기
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('  ...연결 중...')
    time.sleep(1)

# --- 7. Wi-Fi 연결 결과에 따라 작업 수행 ---
if wlan.status() != 3:
    print(f'--- Wi-Fi 연결 실패! (상태 코드: {wlan.status()}) ---')
    print('라이브러리 설치를 진행할 수 없습니다.')
else:
    print('--- Wi-Fi 연결 성공! ---')
    status = wlan.ifconfig()
    print(f'IP 주소: {status[0]}')
    print('--- 라이브러리 일괄 설치를 시작합니다. ---')
    
    # Wi-Fi 연결이 성공했으므로, 라이브러리 설치 루프 실행
    for file_name, github_link in libraries_to_install.items():
        install_library(file_name, github_link)
        
    print("--- 모든 작업 완료 ---")