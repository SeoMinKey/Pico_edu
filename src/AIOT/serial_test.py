import machine
import time
import sys
import select
from neopixel import NeoPixel  # (주의) neopixel.py 라이브러리 파일이 필요합니다.

# --- 1. 설정 ---
NEOPIXEL_PIN = 21  # 네오픽셀 DIN 핀 번호
NUM_PIXELS = 1     # 네오픽셀 개수
LOG_FILE = 'serial_log.txt' # (추가) 로그 파일 이름

# --- 2. 네오픽셀 설정 ---
np = NeoPixel(machine.Pin(NEOPIXEL_PIN), NUM_PIXELS)

# --- 3. 색상 정의 ---
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_OFF = (0, 0, 0)
COLOR_WHITE_DIM = (50, 50, 50)     # 부팅 확인용
COLOR_ERROR = (255, 0, 255)    # 오류 발생 시: 보라색

# --- 4. 네오픽셀 제어 함수 ---
def set_neopixel(color):
    for i in range(np.n):
        np[i] = color
    np.write()

# --- 5. 시리얼 입력(REPL) 감지기 설정 ---
poller = select.poll()
poller.register(sys.stdin, select.POLLIN)

# --- 6. (추가) 로그 파일에 부팅 메시지 저장 ---
print(f"Pico Logger Ready. Logging to {LOG_FILE}")
print("Viper IDE 연결을 끊고, USB 케이블을 재연결하세요.")
try:
    # 'a' 모드: 파일이 있으면 이어쓰기, 없으면 새로 만들기
    with open(LOG_FILE, 'a') as f:
        f.write(f"---- SCRIPT STARTED at {time.ticks_ms()} ----\n")
except Exception as e:
    print(f"로그 파일 쓰기 실패: {e}")
    # 파일 쓰기 실패 시 보라색으로 3번 깜빡임
    for _ in range(3):
        set_neopixel(COLOR_ERROR); time.sleep_ms(100); set_neopixel(COLOR_OFF); time.sleep_ms(100)

# --- 7. 부팅 완료 신호 (LED) ---
for _ in range(3):
    set_neopixel(COLOR_WHITE_DIM); time.sleep_ms(70); set_neopixel(COLOR_OFF); time.sleep_ms(70)

# --- 8. 메인 루프 ---
while True:
    try:
        events = poller.poll(10) 
        
        if events:
            line_data = sys.stdin.readline()
            
            if line_data:
                # ----------------------------------------------------
                # (수정) .decode('utf-8') 부분을 삭제했습니다.
                # line_data가 이미 str 타입이므로 .strip()만 사용합니다.
                # ----------------------------------------------------
                class_name = line_data.strip() 
                
                # (추가) 수신된 데이터를 로그 파일에 즉시 저장
                with open(LOG_FILE, 'a') as f:
                    f.write(f"{time.ticks_ms()}: Received: {class_name}\n")
                
                # 네오픽셀 색상 변경
                if class_name == "Class 1":
                    set_neopixel(COLOR_RED)
                elif class_name == "Class 2":
                    set_neopixel(COLOR_BLUE)
                elif class_name == "Class 3":
                    set_neopixel(COLOR_GREEN)
                elif class_name == "Class 0": 
                    set_neopixel(COLOR_OFF)
                else:
                    # (추가) "Class 1" 등이 아닌, 예상치 못한 값이 들어온 경우
                    # 0.5초간 흰색으로 켜서 "알 수 없는 값"임을 표시
                    set_neopixel(COLOR_WHITE_DIM)
                    time.sleep_ms(500)
                    set_neopixel(COLOR_OFF) # 다시 끄기 (또는 이전 색상으로 복구)
                
    except Exception as e:
        # (수정) 오류 발생 시, 오류 내용도 로그 파일에 저장
        try:
            with open(LOG_FILE, 'a') as f:
                f.write(f"{time.ticks_ms()}: ERROR: {str(e)}\n")
        except Exception as log_e:
            print(f"Failed to write error log: {log_e}") # 이건 어쩔 수 없음
            
        # 오류 발생 시 보라색으로 5번 깜빡임
        for _ in range(5):
            set_neopixel(COLOR_ERROR); time.sleep_ms(50); set_neopixel(COLOR_OFF); time.sleep_ms(50)
