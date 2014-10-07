
#include <Wire.h>
#include <GOFi2cOLED.h>

GOFi2cOLED GOFoled;

#define ESP8266_E_PIN  13
#define SSID  "<your_ssid>"
#define PASS  "<your_password>"
#define SERVER_IP   "192.168.1.201"
#define SERVER_PORT   "9999"


void setup()
{
  
  Serial.begin(115200);
  
  GOFoled.init(0x3C);
  GOFoled.clearDisplay();
  GOFoled.setTextSize(2);
  GOFoled.setTextColor(WHITE);
 
  
  pinMode(ESP8266_E_PIN,OUTPUT);
  digitalWrite(ESP8266_E_PIN,LOW);
  delay(100);
  digitalWrite(ESP8266_E_PIN,HIGH);
  wait("ready",0);
  
  send_wait("AT+RST","ready",0);
  send_wait("AT+CWMODE=1","OK",1000);
  connect_WiFi(SSID,PASS);
  send_wait("AT+CIPMUX=0","OK",1000);

  boolean connect_state = true;
  while (connect_state){
    if(send_wait("AT+CIFSR","192",2000))
      connect_state = false;
  }
  
  while (!connect_Server(SERVER_IP,SERVER_PORT));
  delay(1000);
  
}
void loop()
{
    unsigned humidity = analogRead(A0)>>2;
    GOFoled.clearDisplay();
    
    sent_data(2,2, humidity);
    
    GOFoled.setTextSize(2);
    GOFoled.setTextColor(WHITE);
    GOFoled.setCursor(0,0);
    GOFoled.print("HUMI : ");
    GOFoled.print(humidity);
    GOFoled.display();     
    
    delay(1000);
}
boolean wait(char *AT_Response,unsigned int time_out){
    unsigned int counter=0;
    unsigned int time_counter = 0;
    char buffer;
    while(true){
        if ( Serial.available()  ) {
            buffer = Serial.read();
            if (buffer == AT_Response[counter]){
                counter++;
            }
            if((counter > 0) && (buffer != AT_Response[counter])){
                counter == 0;
            }
            if(AT_Response[counter] == '\0'){
                return 1;  
            }
        }
        if((time_counter++ >= time_out) && (time_out != 0 ))
            return 0;
        delay(1);
    }
}

boolean send_wait(String AT_Command, char *AT_Response,unsigned int time_out){
  char buffer[1000];
  unsigned long counter=0;
  //dbgSerial.print(AT_Command);
  Serial.println(AT_Command);
  return wait(AT_Response,time_out);
}
boolean connect_WiFi(String NetworkSSID,String NetworkPASS)
{
    String cmd = "AT+CWJAP=\"";
    cmd += NetworkSSID;
    cmd += "\",\"";
    cmd += NetworkPASS;
    cmd += "\"";
    send_wait(cmd,"OK",0);
}
boolean connect_Server(String IP,String port)
{
    char buffer[5];
    unsigned int counter=0;
    String cmd = "AT+CIPSTART=\"TCP\",\"";
    cmd += IP;
    cmd += "\",";
    cmd += port;
    Serial.println(cmd);
    while(true){
        if ( Serial.available()  ) {
            buffer[0] = buffer[1]; 
            buffer[1] = buffer[2]; 
            buffer[2] = buffer[3]; 
            buffer[3] = buffer[4]; 
            buffer[4] = Serial.read();
            if((buffer[3] ==  'O') && (buffer[4] ==  'K'))
                return (1);
            if((buffer[0] ==  'E') && (buffer[1] ==  'R') \
               && (buffer[2] ==  'R') && (buffer[3] ==  'O') \
               && (buffer[4] ==  'R'))
                return (0);
        }
        
    }
    
}
boolean sent_data(byte id ,byte type ,byte data){
  send_wait("AT+CIPSEND=5",">",0);
  Serial.write(0x7e);
  Serial.write(id);
  Serial.write(type);
  Serial.write(data);
  Serial.write(0x7e);
  Serial.println("");
  wait("OK",0);
}
