
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ModbusRTU.h>
#include <ArduinoJson.h>
#include <ESP8266mDNS.h>
#include <TelnetStream.h>


// Modbus Settings
#define SLAVE_ID 1
#define FIRST_REG 0
#define REG_COUNT 18
#define D1 (5)
#define D2 (4)
#define D0 (16)
#define KEEPALIVE 60
#define DELAY 5000
ModbusRTU dds238_1zn;
String response;

// Telnet Settings
const char* host_name = "dds238_1zn";
const char* host_password = "Telnet Password"; 
int const   host_port = 23; 

// Wifi Client Settings 
const char* ssid = "WIFI SSID";
const char* password = "WIFI Pwd";
const char* mqtt_server = "Mqtt Ip Address";
const char* mqtt_user = "Mqtt User";
const char* mqtt_pwd = "Mqtt Pwd";
const char* willTopic = "/dds238_1zn/status";

// MQTT Settings
bool willRetain = true;
const char* willMessage = "";
bool const cleanSession = true;
int const willQoS = 0;
const char* clientId = "DDS238-1ZN";

WiFiClient espClient;
PubSubClient client(espClient);


void setup_telnet() {
  TelnetStream.begin();
}

void setup_wifi() {
  String hostNameWifi = host_name;
  hostNameWifi.concat(".local");
  WiFi.hostname(hostNameWifi);
  
  WiFi.mode(WIFI_STA);

  // Wifi Client Connection
  delay(10);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void setup_mDNS() {
  // Starting  mDNS to dds238_1zn.local
  
  while (!MDNS.begin(host_name)) {             
    // Serial.println("starting mDNS...");
  }
   
  MDNS.addService("telnet", "tcp", host_port);
    // Serial.print("mDNS started: " + String(host_name) + ":" + String(host_port));
}  


/*
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}
*/

// MQTT Connection
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    // Serial.print("Attempting MQTT connection to: ");
    // Serial.println(mqtt_server);
    // Attempt to connect
    willMessage = "";
    if (client.connect(clientId, mqtt_user, mqtt_pwd, willTopic, willQoS, willRetain, willMessage, cleanSession)) {          
        client.subscribe("dds238_1zn/in");
    } else {
        delay(5000);
    }
  }
}


// MODBUS Callback to monitor errors
bool cb(Modbus::ResultCode event, uint16_t transactionId, void* data) { 
  if (event != Modbus::EX_SUCCESS) {
    // Serial.print("Error while getting Holding Registers. Request result: 0x");
    // Serial.println(event, HEX);
  }
  response = String(event, HEX);
  return true;
}

// Read & Publish Holding Registers
void publish_HoldingRegisters() {

  uint16_t registers[REG_COUNT];
  if (!dds238_1zn.slave()) {    // Check if no transaction in progress
    dds238_1zn.readHreg(SLAVE_ID, FIRST_REG, registers, REG_COUNT, cb); // Send Read Hreg from Modbus Server 
    while(dds238_1zn.slave()) { // Check if transaction is active
      dds238_1zn.task();
    }
  }
  if (response == "0") { 

    DynamicJsonDocument json_data(200);
    char data_buffer[200];
       
    // Current Total Energy = Cur Tot Energy Low + Cur Tot Energy High 
    json_data["cte"] = float(registers[0] + registers[1] / 100.00);
    // Current Export Energy = Cur Exp Energy Low + Cur Exp Energy High
    json_data["cee"] = float(registers[8] + registers[9] / 100.00);
    // Current Import Energy = Cur Imp Energy Low + Cur Imp Energy High
    json_data["cie"] = float(registers[10] + registers[11] / 100.00);
    // Voltage
    json_data["v"] = float(registers[12] /10.00);
    // Current
    json_data["c"] = float(registers[13] /10.00);
    // Active Power
    json_data["ap"] = registers[14];
    // reactive Power
    json_data["rp"] = registers[15];
    // Power Factor
    json_data["pf"] = float(registers[16] /1000.000);
    // Frequency
    json_data["f"] = float(registers[17] /100.00);

    size_t data_size= serializeJson(json_data, data_buffer);
    client.publish("dds238_1zn/out", data_buffer, data_size);
    TelnetStream.print(String(data_buffer) + "\n");

  } 
}

void setup() {

  Serial.begin(9600);
  dds238_1zn.begin(&Serial, D0);
  dds238_1zn.master();
  
  setup_wifi();
  setup_mDNS();
  setup_telnet();
  
  client.setServer(mqtt_server, 1883);
  client.setKeepAlive(KEEPALIVE);
//  client.setCallback(callback);

}

void loop() {
  
  if (!client.connected()) {
    reconnect();
  }

  TelnetStream.read();
  
  publish_HoldingRegisters(); 
  if (response == "0") {
      delay(DELAY);
  }  
  client.loop();
  MDNS.update();
}
