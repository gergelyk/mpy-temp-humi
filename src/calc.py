import log
from array import array
from micropython import const

NaN = const(127)
MAX_SAMLES = const(150) # 5 min
MARGIN = const(10)

DIVISOR_1H = const(12)
DIVISOR_1D = const(24)

class Measurements:
    def __init__(self):
        self.temp = array('b', (NaN for _ in range(MAX_SAMLES + MARGIN)))
        self.humi = array('b', (NaN for _ in range(MAX_SAMLES + MARGIN)))
        self.sample_index = 0

    def set_sample(self, t, h):
        self.temp[self.sample_index] = t
        self.humi[self.sample_index] = h

        self.sample_index += 1
        if self.sample_index == MAX_SAMLES:
            self.sample_index = 0
            
        return self.sample_index

class Accumulator:
    def __init__(self):
        self.temp = 0
        self.humi = 0
        self._count = 0
        
    def set_sample(self, t, h):
        if t != NaN and h != NaN:
            self.temp += t
            self.humi += h
            self._count += 1
            
    def clear(self):
        if self._count:
            t = round(self.temp / self._count)
            h = round(self.humi / self._count)
        else:
            t = h = NaN

        self.temp = 0
        self.humi = 0
        self._count = 0
        return t, h
    
class MinMax:
    def __init__(self):
        self.val_min = None
        self.val_max = None
        
    def set_sample(self, val):
        if self.val_min is None or self.val_min > val:
            self.val_min = val
            
        if self.val_max is None or self.val_max < val:
            self.val_max = val

meas_5m = Measurements()
accu_5m = Accumulator()
meas_1h = Measurements()
accu_1h = Accumulator()
meas_1d = Measurements()
temp_minmax = MinMax()
humi_minmax = MinMax()

def set_sample(spl_5m_temp, spl_5m_humi):
    
    spl_5m_temp = NaN if spl_5m_temp is None else spl_5m_temp
    spl_5m_humi = NaN if spl_5m_humi is None else spl_5m_humi

    temp_minmax.set_sample(spl_5m_temp)
    humi_minmax.set_sample(spl_5m_humi)
    
    index_5m = meas_5m.set_sample(spl_5m_temp, spl_5m_humi)
    accu_5m.set_sample(spl_5m_temp, spl_5m_humi)
    if index_5m % DIVISOR_1H == 0:
        spl_1h_temp, spl_1h_humi = accu_5m.clear()
        index_1h = meas_1h.set_sample(spl_1h_temp, spl_1h_humi)
        accu_1h.set_sample(spl_1h_temp, spl_1h_humi)
        if index_1h % DIVISOR_1D == 0:
            spl_1d_temp, spl_1d_humi = accu_1h.clear()
            meas_1d.set_sample(spl_1d_temp, spl_1d_humi)


