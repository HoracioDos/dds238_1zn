# **DDS238-1ZN Energy Meter to ZABBIX** 

ESP8266 reads energy data from DDS238-1ZN meter through a RS485 interface as a Modbus RTU Client. Then ESP8266 connects to a MQTT Broker (Mosquitto) via WIFI and publish data in JSON format.
On the other side, a python program subscribes to the device topic, it reads the JSON payload and it sends data using zabbix_sender command also as JSON.
There is also a telnet service running on the ESP8266. It allows to connect to ESP8266 to check the output payload in realtime.

![DDS238-1ZN](https://raw.githubusercontent.com/HoracioDos/dds238_1zn/main/Images/DDS238-1ZN.png)

![ZabbixDashboardDDS238-1ZN](https://raw.githubusercontent.com/HoracioDos/dds238_1zn/main/Images/ZabbixDashboardDDS238-1ZN.png)
=======

## ToDo

* Wiring Diagram. 
* Document project.
