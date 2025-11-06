from machine import Pin, I2C
from utime import sleep
from bh1750 import BH1750
from neopixel import NeoPixel

light = BH1750(0x23, I2C(0, sda=Pin(4), scl=Pin(5)))
np = NeoPixel(Pin(21), 1)

while True:
  print(light.measurement)        # 현재 조도(lx) 출력
  if light.measurement >= 750:    # 밝기 값이 750lx 이상이면
    np[0] = (255, 0, 0)           # NeoPixel 빨간색 켜기
  elif light.measurement >= 500:  # 밝기 값이 500lx 이상이면
    np[0] = (0, 255, 0)           # NeoPixel 초록색 켜기
  elif light.measurement >= 250:  # 밝기 값이 250lx 이상이면
    np[0] = (0, 0, 255)           # NeoPixel 파란색 켜기
  else:                           # 그 외 (250lx 미만)
    np[0] = (0, 0, 0)             # NeoPixel 끄기
  np.write()                      # NeoPixel에 적용
  sleep(1)

    