#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import logging

import paho.mqtt.client as mqtt
import os
from subprocess import Popen, PIPE, STDOUT, run

device = "Zabbix Host Name"
config_file = "/etc/zabbix/zabbix_agent2.conf"
logname = '/var/log/dds238_1zn/dds238_1zn.log'
mqtt_user ="Mqtt User"
mqtt_pwd = "Mqtt Pwd"
mqtt_server = "Mqtt Server Ip Address"
mqtt_topic = "dds238_1zn/out/#"
item_key = "dds238[json]"

def on_message(client, obj, msg):

    json = str(msg.payload.decode("utf-8"))
    logging.debug('Topic: ' + msg.topic + ' JSON Payload: ' + json)
    cmd = ["zabbix_sender", "-c", config_file, "-k", item_key, "-o", json]
    logging.debug("cmd: " + " ".join(cmd))

    pipe = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    sender_stdout = pipe.communicate()[0]
    logging.debug(' '.join(sender_stdout.decode().split())+"\n")

    # result = run(["zabbix_sender", "-c", config_file, "-k", item_key, "-o", json], stdout=PIPE, stderr=>
    # result = run(["zabbix_sender", "-c", config_file, "-k", item_key, "-o", json], stdout=PIPE, stderr=>
    # logging.debug(result.stdout)

def on_log(client, obj, level, string):
    logging.debug(string)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(mqtt_topic)
        logging.debug("Connected OK to Mosquitto - RC= " + str(rc))
    else:
        connected_flag = False
        logging.debug("Error Connection to Mosquitto - RC= " + str(rc))

def on_disconnect(client, userdata, rc):
        logging.debug("Disconnected from Mosquitto - RC= " + str(rc))

if __name__ == "__main__":
    try:

        logging.basicConfig(filename=logname, filemode='w', format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)
        logging.debug('DDS238_1ZN Service started')

        client = mqtt.Client("dds238_1zn.py", clean_session=True)
        client.username_pw_set(mqtt_user, mqtt_pwd)

        client.on_message = on_message
        # client.on_log = on_log
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect

        client.connect(host=mqtt_server, port=1883, keepalive=60)
        client.loop_forever()

    except:
        logging.debug('DDS238_1ZN Service stopped')
        sys.exit()
