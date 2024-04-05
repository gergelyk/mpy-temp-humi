from machine import Pin
import time

class Button:

    def __init__(self, on_pressed, on_held, pin, debounce_timeout=200, hold_time=2000):
        self.last_irq_ts = 0

        def btn_pressed(pin):
            self.last_irq_ts
            ts = time.ticks_ms()
            diff = ts - self.last_irq_ts
            self.last_irq_ts = ts
            if diff < debounce_timeout:
                return

            on_pressed()
            
            while not pin.value():
                if time.ticks_ms() - ts > hold_time:
                    on_held()
                    return

        self.btn = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.btn.irq(btn_pressed, Pin.IRQ_FALLING)
