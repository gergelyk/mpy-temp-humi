import net
import app
import log
import button
import display
import pages
import led
import machine
import sensor
import calc
import gc
from machine import Timer
from config import load_wifi_config, reset_wifi_config

def start_app(disp, led_blue):

    wifi_config = load_wifi_config()
    log.info(f"WiFi mode: {wifi_config.mode}")
    
    setup_wifi_page = pages.SetupWiFi(disp, led_blue)
    light_mode_page = pages.LightMode(disp, led_blue)
    dark_mode_page = pages.DarkMode(disp, led_blue)
    night_mode_page = pages.NightMode(disp, led_blue)

    setup_wifi_page.successor = light_mode_page
    light_mode_page.successor = dark_mode_page
    dark_mode_page.successor = night_mode_page
    night_mode_page.successor = light_mode_page

    if wifi_config.mode == 'ACCESS_POINT':
        ip_addr = net.setup_access_point(net.SSID, net.PSWD)
        disp.activate_page(setup_wifi_page)
        disp.set_wifi_info(
            ip_addr=ip_addr,
            status='available:',
            message=' ' + net.SSID)
        app.app.run()
    elif wifi_config.mode == 'STATION':
        disp.activate_page(light_mode_page)
        disp.set_wifi_info(
            ip_addr='',
            status='enabled',
            message=' ' + 'Connecting...')
        try:
            ip_addr = net.setup_station(wifi_config.ssid, wifi_config.pswd)
        except Exception as exc:
            log.info(f'WiFi error: {exc}')
            disp.set_wifi_info(
                ip_addr='',
                status='error:',
                message=' ' + 'Cannot connect')
        else:
            disp.set_wifi_info(
                ip_addr=ip_addr,
                status='connected',
                message=' ' + ip_addr)
            app.app.run()
    else:
        disp.activate_page(light_mode_page)
        disp.set_wifi_info(
            ip_addr='',
            status='disabled',
            message='Hold DISP Button')

machine.freq(160000000)

log.setup()

led_blue = led.Led(pin=2)
    
sens = sensor.Sensor(pin=16) # pin16 is D0 for D-duino-V3 (HW-630)

disp = display.Display(
    pin_sda=5,
    pin_scl=4)

btn = button.Button(
    on_pressed=disp.activate_next_page,
    on_held=reset_wifi_config,
    pin=0)

def set_sample():
    led_blue.blink()
    temp, humi = sens.measure()
    calc.set_sample(temp, humi)    
    disp.set_meas_info(
        temp=temp,
        humi=humi,
        tmin=calc.temp_minmax.val_min,
        tmax=calc.temp_minmax.val_max,
        hmin=calc.humi_minmax.val_min,
        hmax=calc.humi_minmax.val_max)
    #log.debug('Free mem: ' + str(gc.mem_free()))

timer = Timer(-1)
timer.init(
    period=2000,
    mode=Timer.PERIODIC,
    callback=lambda timer: set_sample())

start_app(disp, led_blue)
