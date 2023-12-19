# Application measures temperature and humidity
# Platform: D-duino-V3 (HW-630)
# Tested with MicroPython: ESP8266_GENERIC-20231005-v1.21.0.bin

from time import sleep_ms
import dht
import ssd1306
from machine import Pin, I2C, Timer

machine.freq(160000000)
timer = Timer(-1)

# 5k resistor must be installed between VCC and data line, see manual
dht11 = dht.DHT11(Pin(16)) # pin16 is D0 for D-duino-V3 (HW-630)
led = Pin(2, Pin.OUT, value=1) # negative logic
i2c = I2C(sda=Pin(5), scl=Pin(4)) # using default address 0x3C
display = ssd1306.SSD1306_I2C(128, 64, i2c)
display.rotate(False)
display.invert(0)
display.contrast(1) # 0-255

temp = humi = 0
temp_min = humi_min = 99
temp_max = humi_max = -99

sample_count = 0
error_count = 0


def blink():
    led.off()
    sleep_ms(1)
    led.on()

def measure():
    global temp_min, temp_max
    global humi_min, humi_max
    global sample_count, error_count
    global temp, humi

    try:
        dht11.measure()
        temp = dht11.temperature()
        humi = dht11.humidity()
        if humi > 100:
            raise Exception
    except Exception as exc:
        print(exc)
        error_count += 1
        blink()
        sleep_ms(100)
    else:
        temp_min = min(temp_min, temp)
        temp_max = max(temp_max, temp)
        humi_min = min(humi_min, humi)
        humi_max = max(humi_max, humi)
        sample_count += 1
        error = False

    display.fill(0)
    display.text(f'Temp: {temp:3d}  C', 0, 0, 1)
    display.text(f' min:{temp_min:3d} max:{temp_max:3d}', 0, 10, 1)
    display.text(f'Humi: {humi:3d} %RH', 0, 23, 1)
    display.text(f' min:{humi_min:3d} max:{humi_max:3d}', 0, 33, 1)
    display.text(f'{sample_count:12d} spl', 0, 46, 1)
    display.text(f'{error_count:12d} err', 0, 56, 1)
    display.rect(83, 0, 3, 3, 1) # degree symbol
    display.hline(0, 20, 128, 1)
    display.hline(0, 43, 128, 1)
    display.show()
    blink()

# it seems that DHT11 needs a bit more than a second to get ready
timer.init(period=2000, mode=Timer.PERIODIC, callback=lambda timer: measure())

# alternative variant: easier for debugging, but sampling period not precise
#while True:
#    measure()
#    sleep_ms(2000)
