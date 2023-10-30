#include <Wire.h>
#include <GPIO.h>

#include <ArduinoJson.h>

volatile int drillTool = 1;
volatile int profileLoading = 0;
volatile int profileLoadingFail = 0;

// rele
GPIO<BOARD::D40> fingersFixedSensor;
GPIO<BOARD::D41> profileFixedPickupSensor;
GPIO<BOARD::D42> fingerLoaderSensor;
GPIO<BOARD::D43> profileLoaderPickupSensor;
GPIO<BOARD::D44> profileLoaded;


GPIO<BOARD::D22> profileLoaderSwitch;
GPIO<BOARD::D23> profileLoaderSwitchArm;
GPIO<BOARD::D24> fingersLoader;
GPIO<BOARD::D25> extension;
GPIO<BOARD::D26> profileFixedSwitch;
GPIO<BOARD::D27> profileFixedSwitchArm;
GPIO<BOARD::D28> profileFixedPickup;
GPIO<BOARD::D29> fingersFixed;

//GPIO<BOARD::D30> ;
//GPIO<BOARD::D31> ;
//GPIO<BOARD::D32> ;
//GPIO<BOARD::D33> ;
GPIO<BOARD::D34> extensionRev;
GPIO<BOARD::D35> extensionFwd;
GPIO<BOARD::D36> pnevmatikaOn;
GPIO<BOARD::D37> profileLoaderPickup;
//GPIO<BOARD::D38> ;
//GPIO<BOARD::D39> ;


void setup() {

  Serial.begin(115200);
  while (!Serial) continue;

  pnevmatikaOn.output();
  pnevmatikaOn = HIGH;

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

  extensionRev.output();
  extensionRev = HIGH;
  extensionFwd.output();
  extensionFwd = LOW;

  profileFixedPickupSensor.input();
  profileLoaderPickupSensor.input();

  fingersFixedSensor.input();
  fingerLoaderSensor.input();

  profileLoaded.input();


  extension.output();

  extension = HIGH;
  profileLoaderPickup = HIGH;
  profileFixedPickup = HIGH;
  delay(1000);
  pnevmatikaOn = LOW;

/*
  while(1) {
    pnevmatikaOn = LOW;
    delay(1000);
    pnevmatikaOn = HIGH;
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
        loadLoader(bay);
        unloadLoader();
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
    }
   }
}


bool loadLoader(int profileSwitch) {
  if (profileSwitch == 1) {
    profileLoaderSwitch = LOW;
    profileFixedSwitch = LOW;
    delay(500);
    profileLoaderSwitchArm = LOW;
    profileFixedSwitchArm = LOW;
    delay(2000);
    fingersFixed = HIGH;
    fingersLoader = HIGH;
    profileLoaderPickup = LOW;
    profileFixedPickup = LOW;
    //delay(4000);

    while(1) {
      if (fingersFixedSensor == HIGH && fingerLoaderSensor == HIGH) {
        profileLoading = 1;
        break;
      }
    }
    //while(fingersFixedSensor == LOW) {}
    //while(fingerLoaderSensor == LOW) {}

    fingersFixed = LOW;
    fingersLoader = LOW;
    delay(2000);
    profileLoaderPickup = HIGH;
    profileFixedPickup = HIGH;

    while(1) {
      if (profileFixedPickupSensor == HIGH && profileLoaderPickupSensor == HIGH) {
        break;
      }
    }


  } else {
    profileLoaderSwitch = HIGH;
    profileFixedSwitch = HIGH;
    delay(500);
    profileLoaderSwitchArm = LOW;
    profileFixedSwitchArm = LOW;
    delay(2000);
    fingersFixed = HIGH;
    fingersLoader = HIGH;
    profileLoaderPickup = LOW;
    profileFixedPickup = LOW;
    //delay(4000);

    while(1) {
      if (fingersFixedSensor == HIGH && fingerLoaderSensor == HIGH) {
        profileLoading = 1;
        break;
      }
    }

    fingersFixed = LOW;
    fingersLoader = LOW;
    delay(2000);
    profileLoaderPickup = HIGH;
    profileFixedPickup = HIGH;

    while(1) {
      if (profileFixedPickupSensor == HIGH && profileLoaderPickupSensor == HIGH) {
        break;
      }
    }

  }

  return true;
}

bool retractLoader() {
  while(1) {
    if (profileFixedPickupSensor == HIGH && profileLoaderPickupSensor == HIGH) {
      break;
    }
  }

  return true;
}

bool resetLoader() {

  profileLoaderPickup = HIGH;
  profileFixedPickup = HIGH;
  delay(2000);

  profileLoaderSwitch = HIGH;
  profileFixedSwitch = HIGH;

  profileLoaderSwitchArm = HIGH;
  profileFixedSwitchArm = HIGH;

  fingersLoader = HIGH;
  fingersFixed = HIGH;

  extensionRev = HIGH;
  extensionFwd = LOW;

  return true;
}

bool unloadLoader() {

    if (profileLoading == 1) {
      if (fingersFixedSensor != HIGH || fingerLoaderSensor != HIGH) {
        profileLoadingFail = 1;
      } else {
        profileLoaderSwitch = HIGH;
        profileFixedSwitch = HIGH;
        delay(500);
      }
    }

    if (profileLoading == 1) {
      if (fingersFixedSensor != HIGH || fingerLoaderSensor != HIGH) {
        profileLoadingFail = 1;
      } else {
        profileLoaderSwitchArm = HIGH;
        profileFixedSwitchArm = HIGH;
        delay(2000);
      }
    }

    if (profileLoading == 1) {
      if (fingersFixedSensor != HIGH || fingerLoaderSensor != HIGH) {
        profileLoadingFail = 1;
      } else {
        profileLoaderPickup = LOW;
        profileFixedPickup = LOW;
        //delay(2000);
      }
    }

    if (profileLoadingFail == 0) {
      int unloadCounter = 20;
      while(profileLoaded == LOW) {
        unloadCounter -= 1;
        delay(100);
        profileLoadingFail = 1;
      }

      profileLoadingFail = 0;
      fingersFixed = HIGH;
      fingersLoader = HIGH;
      delay(2000);
      profileLoaderPickup = HIGH;
      profileFixedPickup = HIGH;
      profileLoading = 0;

      while(1) {
        if (profileFixedPickupSensor == HIGH && profileLoaderPickupSensor == HIGH) {
          profileLoaderSwitch = HIGH;
          profileFixedSwitch = HIGH;
          break;
        }
      }

    }

    //loadProfile(0);
/*
    fingersFixed = LOW;
    fingersLoader = LOW;
*/
  return true;
}