#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "EBS_CSI_RADAR";
const char* password = "12345678";

WiFiUDP udp;
IPAddress broadcastIP(192, 168, 4, 255);
const int port = 3333;

void setup() {
  Serial.begin(115200);

  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password, 6);

  Serial.println("ESP32 TRANSMITTER STARTED");
  Serial.print("AP IP: ");
  Serial.println(WiFi.softAPIP());
}

void loop() {
  udp.beginPacket(broadcastIP, port);
  udp.print("EBS_CSI_PACKET");
  udp.endPacket();

  delay(20);
}
