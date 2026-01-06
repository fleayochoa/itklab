NUM_CHANNELS = 12

SAMPLE_RATE = 1000  # Hz
PLOT_RATE = 20  # Hz
TOTAL_TIME = 10 #s
HV_BAUDRATE = 9600

VOLTAGE_CH1 = 975  # Voltage for channel 1
VOLTAGE_CH2 = 975  # Voltage for channel 2
RAMP_SPEED_CH1 = 20  # Ramp speed for channel 1
RAMP_SPEED_CH2 = 20  # Ramp speed for channel 2

channel_list=(1,2,3,4,5,6,7,8,9,10,11,12)
channel_names = {1:"Vin2-", 2:"Vin2+", 3:"GND2-", 
                    4:"GND2+", 5:"HVmon2", 6:"NTC2",
                    7: "HVmon1", 8:"Vin1-", 9:"Vin1+",
                    10: "GND1-", 11:"GND1+", 12:"NTC1"}

csv_names = {1: "Vin2- Prom. (V)", 2: "Vin2+ Prom. (V)", 3: "GND2- Prom. (V)",
                4: "GND2+ Prom. (V)", 5: "HVmon2 Prom. (V)", 6: "NTC2 Prom. (V)",
                7: "HVmon1 Prom. (V)", 8: "Vin1- Prom. (V)", 9: "Vin1+ Prom. (V)",
                10: "GND1- Prom. (V)", 11: "GND1+ Prom. (V)", 12: "NTC1 Prom. (V)"}

pogo_pins = [1,2,3,4]