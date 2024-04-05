import json
import machine
import log
from mlask import Mlask, HttpResponse
from net import SSID
from config import load_wifi_config, save_wifi_config, disable_wifi, DEFAULT_WIFI_CONFIG, WifiConfig
from calc import meas_5m, meas_1h, meas_1d, MAX_SAMLES

NO_CACHE_HEADERS = { 
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'
}

app = Mlask()

@app.route_get('/')
def root(req):
    return HttpResponse.redirect('/plots')

@app.route_get('/info')
def data_info(req):   
    wifi_config = load_wifi_config()

    return HttpResponse(
        body=json.dumps(dict(
            ssid=wifi_config.ssid,
            sample_index={
                '5m': meas_5m.sample_index,
                '1h': meas_1h.sample_index,
                '1d': meas_1d.sample_index,
            },
            sample_count=MAX_SAMLES,
            device_id=SSID)),
        headers=NO_CACHE_HEADERS,
        content_type='application/json')

@app.route_get('/data')
def data(req):
    args = req.get_url_args()
    time_range = args['tr']
    dimension = args['dim']
    meas = {'5m': meas_5m, '1h': meas_1h, '1d': meas_1d}[time_range]
    data = {'temp': meas.temp, 'humi': meas.humi}[dimension]
    resp = map("{:02x}\n".format, data)
    return HttpResponse.from_iterable(resp, length=len(data)*3, content_type=None)

@app.route_post('/reset')
def reset_post(req):
    machine.reset()

@app.route_get('/wifi')
def wifi_get(req):
    return HttpResponse.from_file('wifi.html')

@app.route_post('/wifi')
def wifi_post(req):
    form_args = req.get_form_args()
    if form_args['ssid']:
        wifi_config = WifiConfig(ssid=form_args['ssid'], pswd=form_args['pswd'], mode='STATION')
    else:
        wifi_config = DEFAULT_WIFI_CONFIG
    
    save_wifi_config(wifi_config)
    return HttpResponse.from_file('reset.html')

@app.route_post('/disable_wifi')
def disable_wifi_post(req):
    disable_wifi()
    return HttpResponse.from_file('reset.html')

@app.route_get('/plots')
def plots(req):
    return HttpResponse.from_file('plots.html')

@app.route_get('/uPlot.iife.min.js')
def chota_get(req):
    return HttpResponse.from_file('uPlot.iife.min.js', content_type='text/javascript')

@app.route_get('/uPlot.min.css')
def chota_get(req):
    return HttpResponse.from_file('uPlot.min.css', content_type='text/css')

@app.route_get('/chota-0.9.2.css')
def chota_get(req):
    return HttpResponse.from_file('chota-0.9.2.css', content_type='text/css')

