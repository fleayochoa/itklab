from picosdk.pl1000 import pl1000 as pl
from ctypes import c_int16
import numpy as np

class PicoManager:
    def __init__(self):
        pass
    def initialize_device(self):
        self.handle = c_int16()
        self.status = pl.pl1000OpenUnit(self.handle)
        print("Handle:", self.handle.value)
        pl.pl1000SetChannels(self.handle, 0, 1)   
        pl.pl1000SetVoltRange(self.handle, 0, 2)  # ±2.5 V
        