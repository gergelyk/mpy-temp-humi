import log
import dht
from machine import Pin

class Sensor:

    def __init__(self, pin):
        self.dht11 = dht.DHT11(Pin(pin))
    
    def measure(self):
        try:
            self.dht11.measure()
            temp = self.dht11.temperature()
            humi = self.dht11.humidity()
            if humi > 100:
                raise Exception("Incorrect humidity")
        except Exception as exc:
            log.error('DHT11 error: ' + str(exc))
            temp = None
            humi = None
        return temp, humi
