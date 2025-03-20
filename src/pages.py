import net

class Page:
    def __init__(self, disp, led):
        self._disp = disp
        self._led = led
        self.successor = None

    def activate(self):
        self._disp.hw.poweron()
        self._disp.hw.contrast(255) # 0-255
        self._led.set_intensity(1023)
        self.render() 
    
    def render(self):
        pass

class SetupWiFi(Page):
    def render(self):
        
        wifi_info = self._disp.wifi_info
        
        self._disp.hw.fill(0)
        self._disp.hw.text(f'Connect to WiFi:', 0, 0, 1)
        self._disp.hw.text(net.SSID, 4, 10, 1)
        self._disp.hw.text(f'Password:', 0, 23, 1)
        self._disp.hw.text(net.PSWD, 4, 33, 1)
        self._disp.hw.text(f'Go to: http://', 0, 46, 1)
        self._disp.hw.text(f'{wifi_info.ip_addr}', 4, 56, 1)
        self._disp.hw.show()

class LightMode(Page):    
    def render(self):

        wifi_info = self._disp.wifi_info
        meas_info = self._disp.meas_info

        self._disp.hw.fill(0)
        self._disp.hw.text(f'Temp: {meas_info.temp}  C', 0, 0, 1)
        self._disp.hw.text(f' min:{meas_info.tmin} max:{meas_info.tmax}', 0, 10, 1)
        self._disp.hw.text(f'Humi: {meas_info.humi} %RH', 0, 23, 1)
        self._disp.hw.text(f' min:{meas_info.hmin} max:{meas_info.hmax}', 0, 33, 1)
        self._disp.hw.text(f'WiFi: {wifi_info.status}', 0, 46, 1)
        self._disp.hw.text(wifi_info.message, 0, 56, 1)
        self._disp.hw.rect(97, 0, 3, 3, 1) # degree symbol
        self._disp.hw.hline(0, 20, 128, 1)
        self._disp.hw.hline(0, 43, 128, 1)
        self._disp.hw.show()
        
class DarkMode(LightMode):
    def activate(self):
        self._disp.hw.poweron()
        self._disp.hw.contrast(1)
        self._led.set_intensity(1)
        self.render()
        
class NightMode(Page):
    def activate(self):
        self._disp.hw.poweroff()
        self._led.set_intensity(1)
