#!/usr/bin/python3
# -*- coding: utf-8 -*-

# import context
import json
import paho.mqtt.client as mqtt
import os
from subprocess import Popen, PIPE, STDOUT

device = "piapc"
config_file="/etc/zabbix/zabbix_agent2.conf"


def on_message(mqttc, obj, msg):

    # print(msg.topic)

    if (msg.topic == "/dds238_1zn/out"):
       parsed_json = json.loads(msg.payload)
       current_total_energy = parsed_json['cte']
       current_exported_energy = parsed_json['cee']
       current_imported_energy = parsed_json['cie']
       voltage = parsed_json['v']
       current = parsed_json['c']
       active_power = parsed_json['ap']
       reactive_power = parsed_json['rp']
       power_factor = parsed_json['pf']
       frequency = parsed_json['f']

       device_values = device + " current_exported_energy " +  str(current_exported_energy) + "\n" + \
          device + " current_imported_energy " +  str(current_imported_energy) + "\n" + \
          device + " voltage " + str(voltage) + "\n" + \
          device + " current " + str(current) + "\n" + \
          device + " active_power " + str(active_power) + "\n" + \
          device + " reactive_power " + str(reactive_power) + "\n" + \
          device + " power_factor " + str(power_factor) + "\n" + \
          device + " frequency " + str(frequency) + "\n" + \
          device + " current_total_energy " +  str(current_total_energy) + "\n"

    if (msg.topic == "/dds238_1zn/status"):
       status = str(msg.payload.decode("utf-8"))
       device_values = device + " status " + status + "\n"

    # print(device_values)
    cmd = ["zabbix_sender", "-c", config_file, "-i", "-"]
    pipe = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    sender_stdout = pipe.communicate(input=device_values.encode())[0]
    # print(sender_stdout)


def on_log(mqttc, obj, level, string):
    print(string)

if __name__ == "__main__":

   MQTT_TOPIC = [("/dds238_1zn/out/#",0),("/dds238_1zn/status/#",0)]
   mqttc = mqtt.Client("py-zabbix_1")
   mqttc.username_pw_set("zabbix", "zabbix")
   mqttc.on_message = on_message
   # Uncomment to enable debug messages
   # mqttc.on_log = on_log
   mqttc.connect("192.168.1.34", 1883, 60)
   mqttc.subscribe(MQTT_TOPIC)

   mqttc.loop_forever()

