#include <WiFi.h>
#include <WiFiUdp.h>
#include "esp_wifi.h"

const char* ssid = "EBS_CSI_RADAR";
const char* password = "12345678";

WiFiUDP udp;
const int port = 3333;

void csi_callback(void *ctx, wifi_csi_info_t *info) {
  if (!info || !info->buf) return;

  Serial.print(millis());
  Serial.print(",");
  Serial.print(info->rx_ctrl.rssi);
  Serial.print(",");
  Serial.print(info->len);

  for (int i = 0; i < info->len; i++) {
    Serial.print(",");
    Serial.print(info->buf[i]);
  }

  Serial.println();
}

void setup() {
  Serial.begin(115200);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  Serial.println("ESP32 RECEIVER CONNECTING...");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("ESP32 RECEIVER CONNECTED");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  udp.begin(port);

  wifi_csi_config_t csi_config = {
    .lltf_en = true,
    .htltf_en = true,
    .stbc_htltf2_en = true,
    .ltf_merge_en = true,
    .channel_filter_en = false,
    .manu_scale = false,
    .shift = false
  };

  esp_wifi_set_csi_config(&csi_config);
  esp_wifi_set_csi_rx_cb(csi_callback, NULL);
  esp_wifi_set_csi(true);

  Serial.println("CSI READING STARTED");
}

void loop() {
  int packetSize = udp.parsePacket();

  if (packetSize) {
    while (udp.available()) {
      udp.read();
    }
  }

  delay(1);
}
