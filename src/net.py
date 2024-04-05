from time import sleep_ms
import machine
import network
import log

SSID = 'IOT-' + '-'.join(map("{:02x}".format, machine.unique_id())).upper()
PSWD = 'ESP-8266'

def setup_station(ssid, pswd, attempts=100):
    network.WLAN(network.AP_IF).active(False)
    sta = network.WLAN(network.STA_IF)
    log.info(f'Connecting to AP {ssid!r}', end='')
    network.hostname('th01')
    sta.active(True)
    sta.connect(ssid, pswd)
    for _ in range(attempts):
        if sta.isconnected():
            break
        sleep_ms(200)
        log.info('.', end='')
    else:
        log.info('')
        raise RuntimeError('Cannot connect')
    log.info('')
    ip_addr, *_ = sta.ifconfig()
    log.info('Connected to AP')
    log.info(f'IP: {ip_addr}')
    return ip_addr

def setup_access_point(ssid, pswd):
    network.WLAN(network.STA_IF).active(False)
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid)
    ap.config(authmode=2, password=pswd) # apparently must have at least 8 characters
    ip_addr, *_ = ap.ifconfig()
    log.info('\nAP created')
    log.info(f'IP: {ip_addr}')
    #log.info('Waiting for a client...')
    #while True:
        #if ap.isconnected():
            #break
        #sleep_ms(200)
    #log.info('First client connected to AP')
    return ip_addr

