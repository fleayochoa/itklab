import ctypes
from ctypes import c_int16
import numpy as np
import time
import picosdk
from lvhv_ui.utils import config
from picosdk.pl1000 import pl1000 as pl
from picosdk.functions import adc2mVpl1000, assert_pico_ok

class PicoManager:
    def __init__(self):
        self.handle = c_int16()
        self.status = {}
        self.channel_list=(1,2,3,4,5,6,7,8,9,10,11,12)
        self.channel_names = {1:"Vin2-", 2:"Vin2+", 3:"GND2-", 
                              4:"GND2+", 5:"HVmon2", 6:"NTC2",
                              7: "HVmon1", 8:"Vin1-", 9:"Vin1+",
                              10: "GND1-", 11:"GND1+", 12:"NTC1"}
        self.usForBlock = ctypes.c_uint32(int(1_000_000)) 
        self.noOfValues = ctypes.c_uint32(int(config.SAMPLE_RATE)) # 10
        self.nchannels = len(self.channel_list)
        self.channel_array = (ctypes.c_uint16 * self.nchannels)()
        for i, ch in enumerate(self.channel_list):
            self.channel_array[i] = pl.PL1000Inputs[f"PL1000_CHANNEL_{ch}"]
        self.read_buffer_size = self.noOfValues.value * self.nchannels
        self.read_sample_count = ctypes.c_uint32(self.read_buffer_size)
        self.read_buffer = (ctypes.c_uint16 * self.read_buffer_size)()
        self.captured_samples = np.zeros(shape=(0, self.nchannels), dtype=np.uint16)
        self.leftover_sample_buffer = np.zeros(shape=(0, ), dtype=np.uint16)
        self.leftover_sample_counter = 0
        self.overflow = ctypes.c_uint16()
        self.triggerIndex = ctypes.c_uint32()
        self.maxADC = ctypes.c_uint16()

    def initialize_device(self):
        self.status["openUnit"] = pl.pl1000OpenUnit(ctypes.byref(self.handle))
        assert_pico_ok(self.status["openUnit"])
        print("Handle:", self.handle.value)
        self.set_interval()

    def set_interval(self):
        assert_pico_ok(
            pl.pl1000MaxValue(self.handle, ctypes.byref(self.maxADC))
            )
        assert_pico_ok(
                pl.pl1000Run(
                    self.handle,
                    ctypes.c_uint32(self.read_buffer_size),
                    pl.PL1000_BLOCK_METHOD["BM_STREAM"]
                )
        )
        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)
        while ready.value == check.value:
            assert_pico_ok(pl.pl1000Ready(self.handle, ctypes.byref(ready)))
        
        

    def get_acquisition_data(self):

        self.read_sample_count = ctypes.c_uint32((int)(self.read_buffer_size//self.nchannels))
        assert_pico_ok(
            pl.pl1000GetValues(
                self.handle,
                ctypes.byref(self.read_buffer),
                ctypes.byref(self.read_sample_count),
                ctypes.byref(self.overflow),
                ctypes.byref(self.triggerIndex)
            )
        )
        
        read_samples_numpy_varsized = np.array(self.read_buffer[:self.read_sample_count.value * self.nchannels]) # get only the valid samples out of the read_buffer
        channelized_samples = read_samples_numpy_varsized.reshape((-1,self.nchannels))
        # Append to final Array
        self.captured_samples = np.vstack((self.captured_samples,channelized_samples))
        input_range = 2500
        # Convert ADC counts to mV
        for i in range(len(self.captured_samples)):
            self.captured_samples[i] = adc2mVpl1000(self.captured_samples[i], input_range)
        # Debug - list array sizes
        # print(f'  - channelized_samples.shape: {channelized_samples.shape}')
        # print(f'  - captured_samples.shape: {captured_samples.shape}')
        # print('---')
        return self.captured_samples
    def close_device(self):
        assert_pico_ok(pl.pl1000CloseUnit(self.handle))

