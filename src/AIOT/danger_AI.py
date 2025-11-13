import machine
import time
import sys
import select
from neopixel import NeoPixel

# --- 1. 학습된 핀 번호 설정 ---
NEOPIXEL_PIN = 21  # 네오픽셀 (GP21)
BUZZER_PIN = 22    # 부저 (GP22)
LOG_FILE = 'serial_log.txt' # 로그 파일

# --- 2. 하드웨어 초기화 ---
# 네오픽셀
np = NeoPixel(machine.Pin(NEOPIXEL_PIN), 1)

# 부저 (PWM)
buzzer = machine.PWM(machine.Pin(BUZZER_PIN))
buzzer.freq(440)     # '라' 음 (440Hz)
buzzer.duty_u16(0)   # 볼륨 0으로 시작

# 시리얼 입력 감지기
poller = select.poll()
poller.register(sys.stdin, select.POLLIN)

# --- 3. 색상 정의 ---
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_PURPLE = (255, 0, 255) # Class 2 (주의)
COLOR_OFF = (0, 0, 0)
COLOR_ERROR = (255, 100, 0)  # 오류시 주황색

# --- 4. 상태 변수 ---
current_state = 0          # 0=IDLE, 1=비상, 2=주의, 3=안전
last_blink_time = 0        # LED 깜빡임 타이머
last_beep_time = 0         # 부저 울림 타이머
neopixel_on = False        # LED 깜빡임 상태
buzzer_on = False          # 부저 울림 상태

# --- 5. 헬퍼 함수 ---
def set_neopixel(color):
    """네오픽셀 색상을 즉시 적용"""
    np[0] = color
    np.write()

def log_message(msg):
    """파일에 로그를 기록합니다."""
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(f"{time.ticks_ms()}: {msg}\n")
    except Exception as e:
        print(f"Failed to write log: {e}")

# --- 6. 부팅 및 시작 ---
log_message("---- SCRIPT STARTED ----")
set_neopixel(COLOR_GREEN)  # 기본 상태를 '안전'으로 시작
current_state = 3
print("Pico Ready. Waiting for Serial commands...")

# --- 7. 메인 루프 ---
while True:
    try:
        now = time.ticks_ms() # 현재 시간 (매 루프마다 갱신)

        # --- A. 시리얼 입력 처리 (비차단) ---
        events = poller.poll(10) # 10ms 동안만 기다림
        
        if events:
            line_data = sys.stdin.readline()
            if line_data:
                class_name = line_data.strip()
                log_message(f"Received: {class_name}")
                
                new_state = 0 # 기본값 (알수없는 명령)
                if class_name == "Class 1":
                    new_state = 1
                elif class_name == "Class 2":
                    new_state = 2
                elif class_name == "Class 3":
                    new_state = 3

                # 상태가 변경되었을 때만 실행
                if new_state != current_state:
                    current_state = new_state
                    
                    # --- 상태 변경 시 모든 장치 초기화 ---
                    buzzer.duty_u16(0)  # 부저 즉시 끄기
                    buzzer_on = False
                    neopixel_on = False
                    
                    # 새 상태가 '안전' 또는 'IDLE'이면 즉시 색상 설정
                    if current_state == 3:
                        set_neopixel(COLOR_GREEN)
                    elif current_state == 0:
                        set_neopixel(COLOR_OFF)
                    
                    # 타이머 초기화 (깜빡임/울림 즉시 시작용)
                    last_blink_time = now
                    last_beep_time = now

        # --- B. 현재 상태에 따른 동작 처리 (비차단) ---

        # 1. 비상 (Class 1): 빨간색 깜빡임 + 2초 간격 비프음
        if current_state == 1:
            # 1-1. 네오픽셀 (0.5초 간격 깜빡임)
            if time.ticks_diff(now, last_blink_time) > 500:
                neopixel_on = not neopixel_on
                set_neopixel(COLOR_RED if neopixel_on else COLOR_OFF)
                last_blink_time = now

            # 1-2. 부저 (2초 주기, 0.5초 울림)
            if not buzzer_on and time.ticks_diff(now, last_beep_time) > 2000:
                buzzer.duty_u16(30000) # 켜기
                buzzer_on = True
                last_beep_time = now
            
            # 켜진 부저 끄기 (0.5초 후)
            if buzzer_on and time.ticks_diff(now, last_beep_time) > 500:
                buzzer.duty_u16(0) # 끄기
                buzzer_on = False

        # 2. 주의 (Class 2): 보라색 깜빡임
        elif current_state == 2:
            # 2-1. 네오픽셀 (0.5초 간격 깜빡임)
            if time.ticks_diff(now, last_blink_time) > 500:
                neopixel_on = not neopixel_on
                set_neopixel(COLOR_PURPLE if neopixel_on else COLOR_OFF)
                last_blink_time = now
            # 2-2. 부저는 (상태 변경 시) 꺼진 상태 유지
        
        # 3. 안전 (Class 3) 또는 0. IDLE (Class 0):
        #    (상태 변경 시 이미 네오픽셀/부저가 설정되었으므로
        #     루프에서 추가로 할 작업 없음)
        
    except Exception as e:
        log_message(f"ERROR: {str(e)}")
        # 오류 발생 시 주황색 5번 깜빡임
        for _ in range(5):
            set_neopixel(COLOR_ERROR); time.sleep_ms(50)
            set_neopixel(COLOR_OFF); time.sleep_ms(50)
