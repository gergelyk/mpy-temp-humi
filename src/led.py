from machine import Pin, PWM
from time import sleep_ms

class Led:
    def __init__(self, pin, intensity=1023):
        pin_obj = Pin(pin, Pin.OUT, value=1)
        self._pwm = PWM(pin_obj)
        self._pwm.freq(1000)
        self._pwm.duty(1023) # off
        self.set_intensity(intensity)

    def set_intensity(self, intensity): # 0=off, 1...1023
        self._duty = 1023 - intensity

    def blink(self, duration=50):
        self._pwm.duty(self._duty)
        sleep_ms(duration)
        self._pwm.duty(1023) # off
