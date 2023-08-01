#include <Wire.h>
#include <GPIO.h>

#include <AccelStepper.h>
#include <SpeedyStepper.h>
#include <ArduinoJson.h>

int stepsPerMM = 160;

// init motors
//GPIO<BOARD::D38> startSenzorMali;
//GPIO<BOARD::D37> startSenzorVeliki;
int startSenzorMali = 38;
int startSenzorVeliki = 37;


GPIO<BOARD::D39> hommingSenzor1;
GPIO<BOARD::D53> directionPin1;
GPIO<BOARD::D52> stepPin1;
AccelStepper stepper1(AccelStepper::DRIVER, 52, 53);

// 4385mm / 180,25 per rev / 4000 steps
int maxHod = 97309;

void setup() {
  Serial.begin(115200);
  //startSenzorMali.input();
  //startSenzorVeliki.input();
  pinMode(startSenzorMali, INPUT);
  pinMode(startSenzorVeliki, INPUT);

 
  stepPin1.output();
  stepPin1 = LOW;
  directionPin1.output();
  directionPin1 = HIGH;

  stepper1.setMaxSpeed(500000);
  stepper1.setAcceleration(5000.0);

    homming();

  stepper1.setCurrentPosition(0);

  //180,25

    moveRev(12000,0);
 /*
  stepper1.moveTo(-97309);
  stepper1.runToPosition();*/  
}



void loop() 
{

    

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
      }
    
      // Fetch values.
      //
      // Most of the time, you can rely on the implicit casts.
      // In other case, you can do doc["time"].as<long>();
      String action = doc["A"];
      int profile = doc["P"];
      long int moveStep = doc["M"];
      int absMove = doc["M2"];

      
/*
      StaticJsonDocument<500> doc3;
       doc3["status"] = "done";
       doc3["A"] = action;
       doc3["M"] = moveStep;
       doc3["F"] = firstMove;
       doc3["com"] = command;
       serializeJson(doc3, Serial);
       Serial.println();
  */    
      // read command from serial port
      if (action == "moveFwdF") {
         while(!waitForProfile(profile)) {}  
         moveFwd(moveStep, absMove);
         StaticJsonDocument<200> doc2;
         doc2["status"] = "done";
         serializeJson(doc2, Serial);
         Serial.println();
      } else if (action == "moveFwd") {
         moveFwd(moveStep, absMove);
         StaticJsonDocument<200> doc2;
         doc2["status"] = "done";
         serializeJson(doc2, Serial);
         Serial.println();
      } else if (action == "moveRev") {  // turn on LED
         moveRev(moveStep, absMove);
         StaticJsonDocument<200> doc2;
         doc2["status"] = "done";
         serializeJson(doc2, Serial);
         Serial.println();
      } else if (action == "home") {  // turn on LED
         homming();
         StaticJsonDocument<200> doc2;
         doc2["status"] = "done";
         serializeJson(doc2, Serial);
         Serial.println();
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
  
  
/*
  Serial.println();
  
  if (startSenzorMali) {
    Serial.println("mali profil");
  }

  if (startSenzorVeliki) {
     Serial.println("veliki profil");
  }

  Serial.println();

  return false;
  
*/
  
  if (profileSize == 1) {
    if (senzorMali == HIGH  && senzorVeliki == LOW) {
      return true;
    }
  } 
  
  if (profileSize == 2) {
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


boolean homming1() {

  directionPin1 = HIGH;

  if (hommingSenzor1 == LOW)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {

      if (hommingSenzor1 == HIGH)
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

  directionPin1 = LOW;
  if (hommingSenzor1 == HIGH)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {
      if (hommingSenzor1 == LOW)
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

  directionPin1 = LOW;

  return true;
}

void moveOneStep1() {
    //directionPin = LOW;

    stepPin1 = HIGH;
    delayMicroseconds(40);
    stepPin1 = LOW;
    delayMicroseconds(40);
 
}
