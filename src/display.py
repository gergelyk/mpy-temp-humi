import ssd1306
import log
from machine import Pin, I2C
from collections import namedtuple

WifiInfo = namedtuple('WifiInfo', ['ip_addr', 'status', 'message'])
_meas_info_fields = ['temp', 'humi', 'tmin', 'tmax', 'hmin', 'hmax']
MeasInfo = namedtuple('MeasInfo', _meas_info_fields)

def _format_int(x):
    if x is None:
        return '  ?'
    return '{:3d}'.format(x)

def _format_float(x):
    if x is None:
        return '  ???'
    return '{:5.1f}'.format(x)

def _format_num(x, k):
    if k in ('temp', 'humi'):
        return _format_float(x)
    return _format_int(x)

class Display:
    def __init__(self, pin_sda, pin_scl):
        i2c = I2C(sda=Pin(pin_sda), scl=Pin(pin_scl)) # using default address 0x3C
        self.hw = ssd1306.SSD1306_I2C(128, 64, i2c)
        self.hw.rotate(False)
        self.hw.invert(0)
        self.hw.poweroff()
        self.active_page = None
        self.wifi_info = WifiInfo(ip_addr='', status='', message='')
        self.meas_info = MeasInfo(**{k: _format_num(None, k) for k in _meas_info_fields})

    def activate_page(self, page):
        page.activate()
        self.active_page = page
        log.info(f'Active page: {page.__class__.__name__}')
    
    def activate_next_page(self):
        self.activate_page(self.active_page.successor)

    def set_wifi_info(self, **wifi_info):
        self.wifi_info = WifiInfo(**wifi_info)
        self.active_page.render()
        
    def set_meas_info(self, **meas_info):
        self.meas_info = MeasInfo(**{k: _format_num(v, k) for k, v in meas_info.items()})
        self.active_page.render()
