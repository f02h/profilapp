#include <Wire.h>
#include <GPIO.h>

#include <ArduinoJson.h>
#include <AccelStepper.h>

volatile int drillTool = 1;
volatile int profileLoading = 0;
volatile int profileLoadingFail = 0;
volatile int isLoading = 0;
volatile int pickupLowered = 0;

int motorBay1 = 3900;
int motorBay2 = 6000;
int motorVozBay1 = 3900;
int motorVozBay2 = 6000;

/*
motorKlesceDvig
motorKlescePomik
motorKlesceDvigVoz
motorKlescePomikVoz
*/

AccelStepper motorKlesceDvig(AccelStepper::DRIVER, 50, 51);
AccelStepper motorKlescePomik(AccelStepper::DRIVER, 52, 53);
AccelStepper motorKlesceDvigVoz(AccelStepper::DRIVER, 46, 47);
AccelStepper motorKlescePomikVoz(AccelStepper::DRIVER, 48, 49);


GPIO<BOARD::D41> snezorVozDvig;
GPIO<BOARD::D38> senzorVozPomik;
GPIO<BOARD::D42> senzorVozKlesce;
GPIO<BOARD::D37> pnevmatikaVozKlesce;

GPIO<BOARD::D43> snezorDvig;
GPIO<BOARD::D40> senzorPomik;
GPIO<BOARD::D45> senzorKlesce;
GPIO<BOARD::D29> pnevmatikaKlesce;

GPIO<BOARD::D44> profileLoaded;

GPIO<BOARD::D34> extensionFwd;
GPIO<BOARD::D35> extensionRev;

// rele
/*
GPIO<BOARD::D40> fingersFixedSensor;
GPIO<BOARD::D41> profileFixedPickupSensor;
GPIO<BOARD::D42> fingerLoaderSensor;
GPIO<BOARD::D43> profileLoaderPickupSensor;
*/

/*
GPIO<BOARD::D22> profileLoaderSwitch;
GPIO<BOARD::D23> profileLoaderSwitchArm;
GPIO<BOARD::D24> fingersLoader;
GPIO<BOARD::D25> extension;
GPIO<BOARD::D26> profileFixedSwitch;
GPIO<BOARD::D27> profileFixedSwitchArm;
GPIO<BOARD::D28> profileFixedPickup;
GPIO<BOARD::D29> fingersFixed;
*/
//GPIO<BOARD::D30> ;
//GPIO<BOARD::D31> ;
//GPIO<BOARD::D32> ;
//GPIO<BOARD::D33> ;
/*GPIO<BOARD::D36> pnevmatikaOn;
GPIO<BOARD::D37> profileLoaderPickup;*/
//GPIO<BOARD::D38> ;
//GPIO<BOARD::D39> ;


void setup() {

  motorKlesceDvig.setMaxSpeed(5000000);
  motorKlesceDvig.setAcceleration(10000.0);

  motorKlescePomik.setMaxSpeed(5000000);
  motorKlescePomik.setAcceleration(10000.0);

  motorKlesceDvigVoz.setMaxSpeed(5000000);
  motorKlesceDvigVoz.setAcceleration(10000.0);

  motorKlescePomikVoz.setMaxSpeed(5000000);
  motorKlescePomikVoz.setAcceleration(10000.0);

  Serial.begin(115200);
  while (!Serial) continue;
/*
  pnevmatikaOn.output();
  pnevmatikaOn = HIGH;
/*
  profileLoaderSwitch.output();
  profileLoaderSwitch = HIGH;
  profileFixedSwitch.output();
  profileFixedSwitch = HIGH;
  profileLoaderSwitchArm.output();
  profileLoaderSwitchArm = HIGH;
  profileFixedSwitchArm.output();
  profileFixedSwitchArm = HIGH;
  profileLoaderPickup.output();
  profileFixedPickup.output();
  fingersLoader.output();
  fingersLoader = HIGH;
  fingersFixed.output();
  fingersFixed = HIGH;
*/

  snezorVozDvig.input();
  senzorVozPomik.input();
  senzorVozKlesce.input();
  pnevmatikaVozKlesce.output();
  pnevmatikaVozKlesce = HIGH;

  snezorDvig.input();
  senzorPomik.input();
  senzorKlesce.input();
  pnevmatikaKlesce.output();
  pnevmatikaKlesce = HIGH;
  
  profileLoaded.input();


  extensionRev.output();
  extensionRev = HIGH;
  extensionFwd.output();
  extensionFwd = LOW;

  /*profileFixedPickupSensor.input();
  profileLoaderPickupSensor.input();

  fingersFixedSensor.input();
  fingerLoaderSensor.input();
*/
  profileLoaded.input();


  /*extension.output();

  extension = HIGH;
  profileLoaderPickup = HIGH;
  profileFixedPickup = HIGH;
  delay(1000);*/
  //pnevmatikaOn = LOW;
/*

  while(1) {
    pnevmatikaKlesce = LOW;
    delay(1000);
    pnevmatikaKlesce = HIGH;
    delay(1000);
  }*/
  /*loadLoader(1);
  delay(3000);
  unloadLoader();
  delay(3000);
  */
  //}

  //loadLoader(0);



/*while(1) {
    loadLoader(0);
    delay(5000);
    loadLoader(1);
    delay(5000);
}
*/
/*
  while (1) {
    loadLoader(1);
    delay(5000);
    loadLoader(0);
    delay(5000);
    /*
    profileLoaderPickup = HIGH;
    delay(2000);
    profileLoaderPickup = LOW;
    delay(2000);

  }
*/
  homming();
  loadLoaderStage1(1);
}

void loop()
{
  if (Serial.available()) {  // check for incoming serial data
      String command = Serial.readString();
      StaticJsonDocument<200> doc;
      int str_len = command.length() + 1;
      char char_array[str_len];
      command.toCharArray(char_array, str_len);

      DeserializationError error = deserializeJson(doc, char_array);

      // Test if parsing succeeds.
      if (error) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.f_str());
        return;
      }

      String action = doc["A"];
      int bay = doc["B"];


    if (action == "load") {
        StaticJsonDocument<200> doc2;
        doc2["status"] = "done";
        serializeJson(doc2, Serial);
        Serial.println();
        loadLoaderStage1(bay);
        //loadLoader(bay);
        //unloadLoader();
    } else if (action == "unload") {
        StaticJsonDocument<200> doc2;
        doc2["status"] = "done";
        serializeJson(doc2, Serial);
        Serial.println();
    } else if (action == "extensionE") {
        extensionFwd = HIGH;
        extensionRev = LOW;
        StaticJsonDocument<200> doc2;
        doc2["status"] = "done";
        serializeJson(doc2, Serial);
        Serial.println();
    } else if (action == "extensionF") {
        extensionFwd = LOW;
        extensionRev = HIGH;
        StaticJsonDocument<200> doc2;
        doc2["status"] = "done";
        serializeJson(doc2, Serial);
        Serial.println();
    } else if (action == "resetLoader") {
        StaticJsonDocument<200> doc2;
        doc2["status"] = "done";
        serializeJson(doc2, Serial);
        Serial.println();
    } else if (action == "retractLoader") {

        StaticJsonDocument<200> doc2;
        doc2["status"] = "done";
        serializeJson(doc2, Serial);
        Serial.println();
    } else if (action == "home") {  // turn on LED
          homming();
          motorKlesceDvig.setCurrentPosition(0);
          motorKlescePomik.setCurrentPosition(0);
          motorKlesceDvigVoz.setCurrentPosition(0);
          motorKlescePomikVoz.setCurrentPosition(0);
          DynamicJsonDocument doc2(1024);
          doc2["status"] = "done";
          serializeJson(doc2, Serial);
          Serial.println();
    }

   }

   if (isLoading == 1 && pickupLowered == 1) {
      if (senzorKlesce == HIGH && senzorVozKlesce == HIGH) {
        profileLoading = 1;
        loadLoaderStage2();
      } else {

        if (!senzorKlesce) {
          moveOneStep1(50,100);
        }

        if (!senzorVozKlesce) {
          moveOneStep1(46,100);
        }
      }
   }

}

bool loadLoaderStage1(int profileSwitch) {
  isLoading = 1;

  if (profileSwitch == 1) {
    motorKlescePomik.moveTo(motorBay1*-1);
    motorKlescePomikVoz.moveTo(motorVozBay1);
    motorKlescePomik.runToPosition();
    motorKlescePomikVoz.runToPosition();
  
    pnevmatikaVozKlesce = HIGH;
    pnevmatikaKlesce = HIGH;

  } else {
    motorKlescePomik.moveTo(motorBay2*-1);
    motorKlescePomikVoz.moveTo(motorVozBay2);
    motorKlescePomik.runToPosition();
    motorKlescePomikVoz.runToPosition();

    pnevmatikaVozKlesce = HIGH;
    pnevmatikaKlesce = HIGH;

  }
    pickupLowered = 1;
    return true;
}

bool loadLoaderStage2() {

    pnevmatikaKlesce = LOW;
    pnevmatikaVozKlesce = LOW;
    delay(100);

    digitalWrite(51, HIGH);
    digitalWrite(47, LOW);

    while(!snezorDvig || !snezorVozDvig) {
      if (!snezorDvig) {
        moveOneStep1(50,100);
      }
      if (!snezorVozDvig) {
        moveOneStep1(46,100);
      }
    }

    digitalWrite(51, LOW);
    digitalWrite(47, HIGH);

    pickupLowered = 0;
    isLoading = 0;
    unloadLoader();

    return true;

}

bool unloadLoader() {

    bool tmpErr = false;
    bool tmpErr2 = false;
    if (senzorKlesce != HIGH || senzorVozKlesce != HIGH) {
      tmpErr = true;
    }

    delay(350);

    if (senzorKlesce != HIGH || senzorVozKlesce != HIGH) {
      tmpErr2 = true;
    }

    if (profileLoading == 1) {
      if (tmpErr && tmpErr2) {
        profileLoadingFail = 1;
      } else {
        // motor za pomik na 0

        while(!senzorPomik || !senzorVozPomik) {
          if (!senzorPomik) {
            moveOneStep1(52,100);
          }
          if (!senzorVozPomik) {
            moveOneStep1(48,100);
          }
        }

        motorKlescePomik.setCurrentPosition(0);
        motorKlescePomikVoz.setCurrentPosition(0);
      }
    }

    tmpErr = false;
    tmpErr2 = false;
    if (senzorKlesce != HIGH || senzorVozKlesce != HIGH) {
      tmpErr = true;
    }
    delay(350);
    if (senzorKlesce != HIGH || senzorVozKlesce != HIGH) {
      tmpErr2 = true;
    }

    if (profileLoading == 1 && profileLoadingFail == 0) {
      if (tmpErr && tmpErr2) {
        profileLoadingFail = 1;
      } 
    }

    if (profileLoadingFail == 0) {
      while(profileLoaded == LOW) {
        moveOneStep1(50,100);
        moveOneStep1(46,100);
      }
      //delay(4000);
      profileLoadingFail = 0;

      pnevmatikaKlesce = HIGH;
      pnevmatikaVozKlesce = HIGH;
      delay(200);

      digitalWrite(51, LOW);
      digitalWrite(47, HIGH);
      moveOneStep1(50,100);
      moveOneStep1(46,100);
      digitalWrite(51, HIGH);
      digitalWrite(47, LOW);

      profileLoading = 0;
/*
      while(1) {
        if (profileFixedPickupSensor == HIGH && profileLoaderPickupSensor == HIGH) {
          profileLoaderSwitch = HIGH;
          profileFixedSwitch = HIGH;
          break;
        }
      }
*/
    }

    //loadProfile(0);
/*
    fingersFixed = LOW;
    fingersLoader = LOW;
*/
  return true;
}


/*
bool loadLoaderStage1(int profileSwitch) {
  isLoading = 1;
/*
motorKlesceDvig
motorKlescePomik
motorKlesceDvigVoz
motorKlescePomikVoz
*/
/*  if (profileSwitch == 1) {
    motorKlescePomik.moveTo(motorBay1*-1);
    motorKlescePomikVoz.moveTo(motorVozBay1);
    motorKlescePomik.runToPosition();
    motorKlescePomikVoz.runToPosition();
  
    pnevmatikaVozKlesce = HIGH;
    pnevmatikaKlesce = HIGH;

    while(!senzorKlesce || !senzorVozKlesce) {
        if (!senzorKlesce) {
          moveOneStep1(50,100);
        }
        if (!senzorVozKlesce) {
          moveOneStep1(46,100);
        }
    }

    pnevmatikaKlesce = LOW;
    pnevmatikaVozKlesce = LOW;
    delay(100);

    digitalWrite(51, HIGH);
    digitalWrite(47, LOW);

    while(!snezorDvig || !snezorVozDvig) {
      if (!snezorDvig) {
        moveOneStep1(50,100);
      }
      if (!snezorVozDvig) {
        moveOneStep1(46,100);
      }
    }

    digitalWrite(51, LOW);
    digitalWrite(47, HIGH);

  } else {
    motorKlescePomik.moveTo(motorBay2*-1);
    motorKlescePomikVoz.moveTo(motorVozBay2);
    motorKlescePomik.runToPosition();
    motorKlescePomikVoz.runToPosition();

    pnevmatikaVozKlesce = HIGH;
    pnevmatikaKlesce = HIGH;

    while(!senzorKlesce || !senzorVozKlesce) {
        if (!senzorKlesce) {
          moveOneStep1(50,100);
        }
        if (!senzorVozKlesce) {
          moveOneStep1(46,100);
        }
    }

    pnevmatikaKlesce = LOW;
    pnevmatikaVozKlesce = LOW;
    delay(100);

    digitalWrite(51, HIGH);
    digitalWrite(47, LOW);

    while(!snezorDvig || !snezorVozDvig) {
      if (!snezorDvig) {
        moveOneStep1(50,100);
      }
      if (!snezorVozDvig) {
        moveOneStep1(46,100);
      }
    }
    
    digitalWrite(51, LOW);
    digitalWrite(47, HIGH);

  }
    pickupLowered = 1;
    return true;
}
*/


boolean homming() {

  if (!homming1(50, 51, 43, 1)) {
    while (1) {};
  }

  if (!homming1(46, 47, 41, 0)) {
    while (1) {};
  }

  if (!homming1(52, 53, 40, 1)) {
    while (1) {};
  }

  if (!homming1(48, 49, 38, 0)) {
    while (1) {};
  }

  return true;
}

boolean homming1(int stepPin, int dirPin, int homeSenzor, int fDir) {

  //directionPin1 = HIGH;
  digitalWrite(dirPin, fDir);

  int hommingSenzorState = digitalRead(homeSenzor);
  if (hommingSenzorState == LOW)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {
      hommingSenzorState = digitalRead(homeSenzor);
      if (hommingSenzorState == HIGH)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep1(stepPin,40);
      //delayMicroseconds(20000);
      delayMicroseconds(320);
    }

    if (limitSwitchFlag == false)
      return (false);
  }
/*
  digitalWrite(dirPin, LOW);
  //directionPin1 = LOW;
  hommingSenzorState = digitalRead(homeSenzor);
  if (hommingSenzorState == HIGH)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {
      hommingSenzorState = digitalRead(homeSenzor);
      if (hommingSenzorState == LOW)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep1(stepPin);
      delayMicroseconds(16000);
    }

    if (limitSwitchFlag == false)
      return (false);
  }
*/
  digitalWrite(dirPin, !fDir);
  //directionPin1 = LOW;
  return true;
}

void moveOneStep1(int stepPinO, int delayC) {
    //directionPin = LOW;
    digitalWrite(stepPinO, HIGH);
    //stepPin1 = HIGH;
    delayMicroseconds(delayC);
    digitalWrite(stepPinO, LOW);
    //stepPin1 = LOW;
    delayMicroseconds(delayC);
}

