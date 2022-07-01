#!/usr/bin/env python

from __future__ import division
from pymodbus.client.sync import ModbusSerialClient as ModbusClient  # initialize a serial RTU client instance

method = "rtu"
port = "/dev/ttyUSB0"
baudrate = 9600
stopbits = 1
bytesize = 8
parity = "N"
timeout = 1
retries = 2

try:
    client = ModbusClient(method=method, port=port, stopbits=stopbits, bytesize=bytesize, parity=parity,
                          baudrate=baudrate, timeout=timeout, retries=retries)
    connection = client.connect()
except:
    print("Modbus error / DDS238-1 ZN")


def get_registers(app_id):
    try:
        data = client.read_holding_registers(0, 18, unit=app_id)
        client.close()
        for registers in data.registers:
            print(registers)
        dds2381zn_cte_low = data.registers[0]
        dds2381zn_cte_high = data.registers[1] / 100
        dds2381zn_current_total_energy = dds2381zn_cte_low + dds2381zn_cte_high
        dds2381zn_cee_low = data.registers[8]
        dds2381zn_cee_high = data.registers[9] / 100
        dds2381zn_current_export_energy = dds2381zn_cee_low + dds2381zn_cee_high/100
        dds2381zn_cie_low = data.registers[10]
        dds2381zn_cie_high = data.registers[11] / 100
        dds2381zn_current_import_energy = dds2381zn_cie_low + dds2381zn_cie_high/100
        dds2381zn_voltage = data.registers[12] / 10
        dds2381zn_current = data.registers[13]
        dds2381zn_active_power = data.registers[14]
        dds2381zn_reactive_power = data.registers[15]
        dds2381zn_power_factor = data.registers[16]
        dds2381zn_frequency = data.registers[17] / 100

        return dds2381zn_current_export_energy, dds2381zn_current_import_energy, dds2381zn_current_total_energy, \
            dds2381zn_voltage, dds2381zn_current, dds2381zn_active_power, dds2381zn_reactive_power,\
            dds2381zn_power_factor, dds2381zn_frequency
    except:
        print("Modbus register error (get_registers)")
        return 0

while True:
    print(get_registers(1))
