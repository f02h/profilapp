#include <Wire.h>
#include <GPIO.h>

#include <ArduinoJson.h>
#include <AccelStepper.h>

volatile int drillTool = 1;
volatile int profileLoading = 0;
volatile int profileLoadingFail = 0;
volatile int isLoading = 0;
volatile int pickupLowered = 0;
volatile int currentProfile = 1;
volatile int singleLoader = 0;

int motorBay1 = 1950;
int motorBay2 = 3420;
int motorVozBay1 = 1950;
int motorVozBay2 = 3420;

int maxSpust = 2850;
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
  loadLoaderStage1(2);
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
        singleLoader = doc["L"];
        loadLoaderStage1(bay);
        //loadLoader(bay);
        //unloadLoader();
    } else if (action == "unload") {
        unloadLoader();
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
        resetLoader();
        StaticJsonDocument<200> doc2;
        doc2["status"] = "done";
        serializeJson(doc2, Serial);
        Serial.println();
    } else if (action == "retractLoader") {
        retractLoader();
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
  currentProfile = profileSwitch;


  if (singleLoader == 0) {
    if (profileSwitch == 1) {
      motorKlescePomik.moveTo(motorBay1*-1);
      motorKlescePomikVoz.moveTo(motorVozBay1);
  /*  motorKlescePomik.runToPosition();
      motorKlescePomikVoz.runToPosition();
  */

      bool stepper1R,stepper2R;
      do {
        stepper1R = motorKlescePomik.run();
        stepper2R = motorKlescePomikVoz.run();
      } while (stepper1R || stepper2R);
      
      pnevmatikaVozKlesce = HIGH;
      pnevmatikaKlesce = HIGH;

    } else {
      motorKlescePomik.moveTo(motorBay2*-1);
      motorKlescePomikVoz.moveTo(motorVozBay2);
      
      bool stepper1R,stepper2R;
      do {
        stepper1R = motorKlescePomik.run();
        stepper2R = motorKlescePomikVoz.run();
      } while (stepper1R || stepper2R);
      
      pnevmatikaVozKlesce = HIGH;
      pnevmatikaKlesce = HIGH;

    }
  } else {
      if (profileSwitch == 1) {
      motorKlescePomik.moveTo(motorBay1*-1);
      bool stepper1R;

      do {
        stepper1R = motorKlescePomik.run();
      } while (stepper1R);
      
      pnevmatikaKlesce = HIGH;

    } else {
      motorKlescePomik.moveTo(motorBay2*-1);
      bool stepper1R;

      do {
        stepper1R = motorKlescePomik.run();
      } while (stepper1R);
      
      pnevmatikaKlesce = HIGH;
    }
  }
    pickupLowered = 1;
    return true;
}

bool loadLoaderStage2() {

    if (singleLoader == 0) {
      pnevmatikaKlesce = LOW;
      pnevmatikaVozKlesce = LOW;
      delay(300);

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
      pnevmatikaKlesce = LOW;
      delay(300);

      digitalWrite(51, HIGH);

      while(!snezorDvig) {
        if (!snezorDvig) {
          moveOneStep1(50,100);
        }
      }

      digitalWrite(51, LOW);

    }

    pickupLowered = 0;
    isLoading = 0;
    unloadLoader();

    return true;

}

bool unloadLoader() {

    bool tmpErr = false;
    bool tmpErr2 = false;

    if (singleLoader == 0) {

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

          digitalWrite(53, HIGH);
          digitalWrite(49, LOW);

          int tmpMinDelay = 100;
          int currDelay = 350;
          int tmpDelayInterval = 5;

          int tmpBay1 = motorBay1;
          if (currentProfile != 1) {
            tmpBay1 = motorBay2;
          }
          
          while(!senzorPomik || !senzorVozPomik) {
            if (tmpMinDelay < currDelay && tmpBay1 > 350) {
              currDelay -= 1;
            }

            if (tmpBay1 < 500 && tmpBay1 > -1) {
              currDelay += 1;
            }

            if (!senzorPomik) {
              moveOneStep1(52,currDelay);
            }
            if (!senzorVozPomik) {
              moveOneStep1(48,currDelay);
            }

            tmpBay1 -= 1;
          }

          digitalWrite(53, LOW);
          digitalWrite(49, HIGH);

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
        int tmpDropCnt = 0;
        while(profileLoaded == LOW && tmpDropCnt < maxSpust) {
          moveOneStep1(50,100);
          moveOneStep1(46,100);
          tmpDropCnt += 1;
        }
        //delay(4000);
        profileLoadingFail = 0;

        pnevmatikaKlesce = HIGH;
        pnevmatikaVozKlesce = HIGH;
        delay(400);

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

        profileLoading = 0;

      }

    } else {
      
      if (senzorKlesce != HIGH) {
        tmpErr = true;
      }

      delay(350);

      if (senzorKlesce != HIGH) {
        tmpErr2 = true;
      }

      if (profileLoading == 1) {
        if (tmpErr && tmpErr2) {
          profileLoadingFail = 1;
        } else {
          // motor za pomik na 0

          digitalWrite(53, HIGH);

          int tmpMinDelay = 100;
          int currDelay = 350;
          int tmpDelayInterval = 5;

          int tmpBay1 = motorBay1;
          if (currentProfile != 1) {
            tmpBay1 = motorBay2;
          }
          
          while(!senzorPomik) {
            if (tmpMinDelay < currDelay && tmpBay1 > 350) {
              currDelay -= 1;
            }

            if (tmpBay1 < 500 && tmpBay1 > -1) {
              currDelay += 1;
            }

            if (!senzorPomik) {
              moveOneStep1(52,currDelay);
            }
            tmpBay1 -= 1;
          }

          digitalWrite(53, LOW);

          motorKlescePomik.setCurrentPosition(0);
        }
      }

      tmpErr = false;
      tmpErr2 = false;
      if (senzorKlesce != HIGH) {
        tmpErr = true;
      }
      delay(350);
      if (senzorKlesce != HIGH) {
        tmpErr2 = true;
      }

      if (profileLoading == 1 && profileLoadingFail == 0) {
        if (tmpErr && tmpErr2) {
          profileLoadingFail = 1;
        } 
      }

      if (profileLoadingFail == 0) {
        int tmpDropCnt = 0;
        while(profileLoaded == LOW && tmpDropCnt < maxSpust) {
          moveOneStep1(50,100);
          tmpDropCnt += 1;
        }
        //delay(4000);
        profileLoadingFail = 0;

        pnevmatikaKlesce = HIGH;
        delay(400);

        digitalWrite(51, HIGH);
        
        while(!snezorDvig) {
          if (!snezorDvig) {
            moveOneStep1(50,100);
          }
        }
        
        digitalWrite(51, LOW);

        profileLoading = 0;
      }
    }


  return true;
}

bool retractLoader() {

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

  return true;
}


bool resetLoader() {

  homming();

  extensionRev = HIGH;
  extensionFwd = LOW;

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

      moveOneStep1(stepPin,100);
      //delayMicroseconds(20000);
      delayMicroseconds(520);
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

