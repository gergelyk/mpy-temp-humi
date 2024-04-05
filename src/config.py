import json
import os
import log
import machine
from collections import namedtuple

WIFI_CONFIG_PATH = 'wifi.json'

WifiConfig = namedtuple('WifiConfig', ['ssid', 'pswd', 'mode'])
DEFAULT_WIFI_CONFIG = WifiConfig(ssid='', pswd='', mode='ACCESS_POINT')

asdict = lambda t: {a: getattr(t, a) for a in dir(t) if not a.startswith('_')}

def load_wifi_config():
    try:
        with open(WIFI_CONFIG_PATH) as fh:
            wifi_config = WifiConfig(**json.load(fh))
            log.info(WIFI_CONFIG_PATH + ' loaded')
    except Exception:
        log.info(WIFI_CONFIG_PATH + ' not loaded')
        wifi_config = DEFAULT_WIFI_CONFIG
    return wifi_config


def save_wifi_config(wifi_config):
    with open(WIFI_CONFIG_PATH, 'w+') as fh:
        json.dump(asdict(wifi_config), fh)

    log.info('WiFi mode set to ' + wifi_config.mode)

def reset_wifi_config():
    save_wifi_config(DEFAULT_WIFI_CONFIG)
    log.info("WiFi config reset")
    machine.reset()
    
def disable_wifi():
    wifi_config = WifiConfig(ssid='', pswd='', mode='DISABLED')
    save_wifi_config(wifi_config)
