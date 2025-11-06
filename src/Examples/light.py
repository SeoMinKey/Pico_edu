from machine import Pin, I2C
from utime import sleep
from bh1750 import BH1750

light = BH1750(0x23, I2C(0, sda=Pin(4), scl=Pin(5)))

while True:
  print(light.measurement)  # 현재 밝기 출력 (lx)
  sleep(1)

    