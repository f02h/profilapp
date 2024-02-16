#include <ArduinoWiFiServer.h>
#include <BearSSLHelpers.h>
#include <CertStoreBearSSL.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiAP.h>
#include <ESP8266WiFiGeneric.h>
#include <ESP8266WiFiGratuitous.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266WiFiSTA.h>
#include <ESP8266WiFiScan.h>
#include <ESP8266WiFiType.h>
#include <WiFiClient.h>
#include <WiFiClientSecure.h>
#include <WiFiClientSecureBearSSL.h>
#include <WiFiServer.h>
#include <WiFiServerSecure.h>
#include <WiFiServerSecureBearSSL.h>
#include <WiFiUdp.h>

#include <Wire.h>
#include <ESP8266WiFi.h>

//#include <GPIO.h>

#include <AccelStepper.h>
//#include <SpeedyStepper.h>
#include <ArduinoJson.h>

int stepsPerMM = 160;

// init motors
//GPIO<BOARD::D38> startSenzorMali;
//GPIO<BOARD::D37> startSenzorVeliki;
int startSenzorMali = D6;
int startSenzorVeliki = D5;
int hommingSenzor1 = D7;
int measureSenzor = D8;

int directionPin1 = D2;
int stepPin1 = D1;
/*
GPIO<BOARD::D39> hommingSenzor1;
GPIO<BOARD::D53> directionPin1;
GPIO<BOARD::D52> stepPin1;*/
AccelStepper stepper1(AccelStepper::DRIVER, stepPin1, directionPin1);

// 4385mm / 180,25 per rev / 4000 steps
int maxHod = 97309;

bool changeLength = false;



void setup() {
  WiFi.mode(WIFI_OFF);
  Serial.begin(115200);
  while (!Serial) continue;

  pinMode(startSenzorMali, INPUT);
  pinMode(startSenzorVeliki, INPUT);
  pinMode(stepPin1, OUTPUT);
  pinMode(directionPin1, OUTPUT);

  digitalWrite(stepPin1, LOW);
  digitalWrite(directionPin1, HIGH);

  stepper1.setMaxSpeed(5000000);
  stepper1.setAcceleration(10000.0);

  stepper1.setCurrentPosition(0);

  //moveRev(24000,0);

}



void loop()
{

    changeLength = false;

    if (Serial.available()) {  // check for incoming serial data

    /*  StaticJsonDocument<200> doc3;
       doc3["status"] = "done";
       doc3["A"] = 0;
       doc3["M"] = 0;
       serializeJson(doc3, Serial);
       Serial.println();*/

      String command = Serial.readString();
      StaticJsonDocument<500> doc;
      int str_len = command.length() + 3;
      char char_array[str_len];
      command.toCharArray(char_array, str_len);

      DeserializationError error = deserializeJson(doc, char_array);

      // Test if parsing succeeds.
      if (error) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.f_str());
        return;
      } else {

        // Fetch values.
        //
        // Most of the time, you can rely on the implicit casts.
        // In other case, you can do doc["time"].as<long>();
        String action = doc["A"];
        int profile = doc["P"];
        long moveStep = doc["M"];
        int absMove = doc["M2"];

      // read command from serial port

        if (action == "waitForProfile") {
          /*while (!waitForProfile(profile) && !changeLength) {
            if (Serial.available()) {  // check for incoming serial data
              String command = Serial.readString();
              StaticJsonDocument<500> doc;
              int str_len = command.length() + 3;
              char char_array[str_len];
              command.toCharArray(char_array, str_len);

              DeserializationError error = deserializeJson(doc, char_array);

              if (error) {
                Serial.print(F("deserializeJson() failed: "));
                Serial.println(error.f_str());
                return;
              } else {
                if (doc["A"] == "changeLength") {
                  changeLength = true;
                }
              }
            }

            if (!changeLength) {
              DynamicJsonDocument doc2(1024);
                  doc2["status"] = "waitingForProfile";
                  serializeJson(doc2, Serial);
                  Serial.println();
            }
          } */

          if (waitForProfile(profile)) {
            DynamicJsonDocument doc2(1024);
            doc2["status"] = "done";
            serializeJson(doc2, Serial);
            Serial.println();
          } else {
            DynamicJsonDocument doc2(1024);
            doc2["status"] = "waiting";
            serializeJson(doc2, Serial);
            Serial.println();
          }

        } else if (action == "moveFwdF") {
          moveFwd(moveStep, absMove);
          DynamicJsonDocument doc2(1024);
          doc2["status"] = "done";
          serializeJson(doc2, Serial);
          Serial.println();
        } else if (action == "moveFwd") {
          moveFwd(moveStep, absMove);
          DynamicJsonDocument doc2(1024);
          doc2["status"] = "done";
          serializeJson(doc2, Serial);
          Serial.println();
        } else if (action == "moveRev") { 
          moveRev(moveStep, absMove);
          DynamicJsonDocument doc2(1024);
          doc2["status"] = "done";
          serializeJson(doc2, Serial);
          Serial.println();
        } else if (action == "home") {  
          homming();
          stepper1.setCurrentPosition(0);
          DynamicJsonDocument doc2(1024);
          doc2["status"] = "done";
          serializeJson(doc2, Serial);
          Serial.println();
        } else if (action == "setRef") {
          homming();
          moveRev(moveStep, absMove);
          stepper1.setCurrentPosition(0);
          DynamicJsonDocument doc2(1024);
          doc2["status"] = "done";
          serializeJson(doc2, Serial);
          Serial.println();
        } else if (action == "measure") {
          toMeasure();
          DynamicJsonDocument doc2(1024);
          doc2["status"] = "done";
          serializeJson(doc2, Serial);
          Serial.println();
        }
      }

   }

}

boolean waitForProfile(int profileSize) {

  //startSenzorMali.input();
  int senzorMali = digitalRead(startSenzorMali);
  delay(300);
  int senzorVeliki = digitalRead(startSenzorVeliki);
  if (senzorMali) {
    senzorMali = digitalRead(startSenzorMali);
  }

  if (profileSize == 1 || profileSize == 3 || profileSize == 4 || profileSize == 5) {
    if (senzorMali == HIGH  && senzorVeliki == LOW) {
      return true;
    }
  }

  if (profileSize == 2 || profileSize == 6 || profileSize == 7 || profileSize == 8) {
    if (senzorMali == HIGH && senzorVeliki == HIGH) {
        return true;
    }
  }

  return false;
}



boolean moveFwd(long int moveSteps, int absMove) {
  if (absMove == 1) {
    stepper1.moveTo(moveSteps);
  } else {
    stepper1.move(moveSteps);
  }

  stepper1.runToPosition();
  return true;

}

boolean moveRev(long int moveSteps, int absMove) {
  if (absMove == 1) {
    stepper1.moveTo(moveSteps * -1);
  } else {
    stepper1.move(moveSteps * -1);
  }

  stepper1.runToPosition();
  return true;
}

boolean homming() {

  if (!homming1()) {
    while (1) {};
  }

  return true;
}

boolean toMeasure() {
/*
  if (!measure()) {
    while (1) {};
  }

  return true;
  */

  stepper1.setMaxSpeed(1000);
  stepper1.setAcceleration(100.0);

  stepper1.moveTo(0);

  bool stepper1R;
  bool toM = false;
  do {
    yield();
    stepper1R = stepper1.run();
    int macSenzorState = digitalRead(measureSenzor);
    if (macSenzorState == HIGH) {
      toM = true;
    }
  } while (!toM);

  stepper1.setMaxSpeed(5000000);
  stepper1.setAcceleration(10000.0);

  return true;

}


boolean homming1() {

  yield();
  //directionPin1 = HIGH;
  digitalWrite(directionPin1, HIGH);

  int hommingSenzorState = digitalRead(hommingSenzor1);
  if (hommingSenzorState == LOW)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {
      yield();
      hommingSenzorState = digitalRead(hommingSenzor1);
      if (hommingSenzorState == HIGH)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep1();
      //delayMicroseconds(20000);
      delayMicroseconds(320);
    }

    if (limitSwitchFlag == false)
      return (false);
  }

  digitalWrite(directionPin1, LOW);
  //directionPin1 = LOW;
  hommingSenzorState = digitalRead(hommingSenzor1);
  if (hommingSenzorState == HIGH)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {
      yield();
      hommingSenzorState = digitalRead(hommingSenzor1);
      if (hommingSenzorState == LOW)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep1();
      delayMicroseconds(16000);
    }

    if (limitSwitchFlag == false)
      return (false);
  }

  digitalWrite(directionPin1, LOW);
  //directionPin1 = LOW;
  return true;
}

boolean measure() {

  yield();
  //directionPin1 = HIGH;
  digitalWrite(directionPin1, HIGH);

  int macSenzorState = digitalRead(measureSenzor);
  if (macSenzorState == LOW)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {
      yield();
      macSenzorState = digitalRead(measureSenzor);
      if (macSenzorState == HIGH)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep1();
      //delayMicroseconds(20000);
      delayMicroseconds(1000);
    }

    if (limitSwitchFlag == false)
      return (false);
  }

  digitalWrite(directionPin1, LOW);
  //directionPin1 = LOW;
  return true;
}

void moveOneStep1() {
    //directionPin = LOW;
    digitalWrite(stepPin1, HIGH);
    //stepPin1 = HIGH;
    delayMicroseconds(40);
    digitalWrite(stepPin1, LOW);
    //stepPin1 = LOW;
    delayMicroseconds(40);
}
