import log
import dht
from machine import Pin

class Sensor:

    def __init__(self, pin):
        self.dht22 = dht.DHT22(Pin(pin))
    
    def measure(self):
        try:
            self.dht22.measure()
            temp = self.dht22.temperature()
            humi = self.dht22.humidity()
            if humi > 100:
                raise Exception("Incorrect humidity")
        except Exception as exc:
            log.error('DHT22 error: ' + str(exc))
            temp = None
            humi = None
        return temp, humi
