#include <Wire.h>
#include <GPIO.h>

#include <AccelStepper.h>
//#include <SpeedyStepper.h>
#include <ArduinoJson.h>

//Initializing LED Pin
int led_pin = 6;

int stepsPerMM = 160;

volatile int drillTool = 1;


// init motors
GPIO<BOARD::D39> hommingSenzor1;
GPIO<BOARD::D53> directionPin1;
GPIO<BOARD::D52> stepPin1;
AccelStepper stepper1(AccelStepper::DRIVER, 52, 53);

GPIO<BOARD::D38> hommingSenzor2;
GPIO<BOARD::D51> directionPin2;
GPIO<BOARD::D50> stepPin2;
AccelStepper stepper2(AccelStepper::DRIVER, 50, 51);

GPIO<BOARD::D37> hommingSenzor3;
GPIO<BOARD::D49> directionPin3;
GPIO<BOARD::D48> stepPin3;
AccelStepper stepper3(AccelStepper::DRIVER, 48, 49);

GPIO<BOARD::D36> hommingSenzor4;
GPIO<BOARD::D47> directionPin4;
GPIO<BOARD::D46> stepPin4;
AccelStepper stepper4(AccelStepper::DRIVER, 46, 47);

GPIO<BOARD::D35> hommingSenzor5;
GPIO<BOARD::D45> directionPin5;
GPIO<BOARD::D44> stepPin5;
AccelStepper stepper5(AccelStepper::DRIVER, 44, 45);

GPIO<BOARD::D34> hommingSenzor6;
GPIO<BOARD::D43> directionPin6;
GPIO<BOARD::D42> stepPin6;
AccelStepper stepper6(AccelStepper::DRIVER, 42, 43);

GPIO<BOARD::D33> hommingSenzor7;
GPIO<BOARD::D41> directionPin7;
GPIO<BOARD::D40> stepPin7;
AccelStepper stepper7(AccelStepper::DRIVER, 40, 41);

AccelStepper stepperArr[7] = {stepper1, stepper2, stepper3, stepper4, stepper5, stepper6, stepper7};


GPIO<BOARD::D32> pneumatikaSenzor1;
GPIO<BOARD::D31> pneumatikaSenzor2;
GPIO<BOARD::D30> pneumatikaSenzor3;
GPIO<BOARD::D29> pneumatikaSenzor4;
GPIO<BOARD::D28> pneumatikaSenzorPrijemalo;

GPIO<BOARD::D27> pneumatikaVentil1;
GPIO<BOARD::D26> pneumatikaVentil2;
GPIO<BOARD::D25> pneumatikaVentil3;
GPIO<BOARD::D24> pneumatikaVentil4;
GPIO<BOARD::D23> pneumatikaVentilPrijemalo;

GPIO<BOARD::D22> mazalkaL;
GPIO<BOARD::D21> mazalkaD;
GPIO<BOARD::D20> mazalkaZaga;

GPIO<BOARD::D9> mazalkaProfil;

GPIO<BOARD::D18> alarm;
boolean alarmTripped = false;


int spindel1 = 2;
int spindel2 = 3;
int spindel3 = 4;
int spindel4 = 5;
int spindel5 = 6;
int spindel6 = 7;
int zaga = 8;

volatile int pozicijaLNull = 0;
volatile int pozicijaDNull = 0;

volatile int maxPozicija = 8000;
volatile int maxHod = 14400;
volatile int maxPovrtavanjeHod = 14400;
volatile int minPovratekL = 200;
volatile int minPovratekD = 200;

volatile int pozicijaL = 0;
volatile int pozicijaD = 0;

volatile int drillToolL = 1;
volatile int drillToolR = 3;


volatile int hod = 15000;
volatile int tmpHod = (maxHod - maxPozicija) + 4800;
volatile int tmpHodL = 14400;
volatile int slowHodL = 800;
volatile int slowHodLSpeed = 75;

volatile int tmpHodD = 14400;
volatile int slowHodD = 800;
volatile int slowHodDSpeed = 75;

volatile int hodL = 0;
volatile int hodD = 0;

volatile int povratekL = 1000;
volatile int povratekD = 1000;

volatile int minPovratekProfil = 1000;

// hod levo hod desno, povratek levo povratek desno

volatile int povrtavanjeL = 11200; // 7cm
volatile int povrtavanjeD = 11200;
volatile int minPovratekPovrtavanjeL = 0;
volatile int minPovratekPovrtavanjeD = 0;

volatile int hodZaga = 8000;
volatile int slowHodZaga = 800;
volatile int slowHodZagaSpeed = 300;


void setup() {

  pinMode(18, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(18), triggerAlarm,CHANGE);
  
 /* hommingSenzor1.input();
  hommingSenzor2.input();
  hommingSenzor3.input();
  hommingSenzor4.input();
  */

  if (hodL > tmpHodL) {
     hodL = tmpHodL; 
  }
  if (hodD > tmpHodD) {
     hodD = tmpHodD;
  }

  pinMode(spindel1, OUTPUT);
  pinMode(spindel2, OUTPUT);
  pinMode(spindel3, OUTPUT);
  pinMode(spindel4, OUTPUT);
  pinMode(spindel5, OUTPUT);
  pinMode(spindel6, OUTPUT);
  pinMode(zaga, OUTPUT);

  digitalWrite(2, HIGH);
  digitalWrite(3, HIGH);
  digitalWrite(4, HIGH);
  digitalWrite(5, HIGH);
  digitalWrite(6, HIGH);
  digitalWrite(7, HIGH);
  digitalWrite(8, HIGH);
  
  pneumatikaVentil1.output();
  pneumatikaVentil1 = HIGH;

  pneumatikaVentil2.output();
  pneumatikaVentil2 = HIGH;

  pneumatikaVentil3.output();
  pneumatikaVentil3 = HIGH;

  pneumatikaVentil4.output();
  pneumatikaVentil4 = HIGH;

  pneumatikaVentilPrijemalo.output();
  pneumatikaVentilPrijemalo = HIGH;

  mazalkaL.output();
  mazalkaL = HIGH;
  mazalkaD.output();
  mazalkaD = HIGH;
  mazalkaZaga.output();
  mazalkaZaga = HIGH;
  mazalkaProfil.output();
  mazalkaProfil = HIGH;
  
  stepPin1.output();
  stepPin1 = LOW;
  directionPin1.output();
  directionPin1 = HIGH;

  stepPin2.output();
  stepPin2 = LOW;
  directionPin2.output();
  directionPin2 = HIGH;

  stepPin3.output();
  stepPin3 = LOW;
  directionPin3.output();
  directionPin3 = HIGH;

  stepPin4.output();
  stepPin4 = LOW;
  directionPin4.output();
  directionPin4 = HIGH;

  stepPin5.output();
  stepPin5 = LOW;
  directionPin5.output();
  directionPin5 = HIGH;

  stepPin6.output();
  stepPin6 = LOW;
  directionPin6.output();
  directionPin6 = HIGH;

  stepPin7.output();
  stepPin7 = LOW;
  directionPin7.output();
  directionPin7 = HIGH;
  Serial.begin(115200);

  stepper1.setMaxSpeed(12000);
  stepper1.setAcceleration(6000.0);
  
  stepper2.setMaxSpeed(12000);
  stepper2.setAcceleration(6000.0);

  stepper3.setMaxSpeed(3000);
  stepper3.setAcceleration(1500.0);

  stepper4.setMaxSpeed(3000);
  stepper4.setAcceleration(1500.0);

  stepper5.setMaxSpeed(6000);
  stepper5.setAcceleration(6000.0);

  stepper6.setMaxSpeed(6000);
  stepper6.setAcceleration(6000.0);

  stepper7.setMaxSpeed(20000);
  stepper7.setAcceleration(20000);

//  drill();


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
    
      // Fetch values.
      //
      // Most of the time, you can rely on the implicit casts.
      // In other case, you can do doc["time"].as<long>();
      String action = doc["action"];
      String action2 = doc["A"];
      
      // read command from serial port
      /*if (action2 == "drill") {
         changePositionL(doc["PL"]);
         changePositionD(doc["PD"]);

         hodL = doc["HL"];
         if (hodL > tmpHodL) {
            hodL = tmpHodL; 
         }
         hodD = doc["HD"];
         if (hodD > tmpHodD) {
            hodD = tmpHodD; 
         }
         drill();
         Serial.println("done");*/
       if (false && alarmTripped) {
        StaticJsonDocument<200> doc2;
        doc2["status"] = "failed";
        serializeJson(doc2, Serial);
        Serial.println();
       }

         
       if (action2 == "drill") {
         changePositionL(doc["PL"]);
         changePositionD(doc["PD"]);

         hodL = doc["HL"];
         hodL = checkMove(1,hodL);
         if (hodL > tmpHodL) {
            hodL = tmpHodL; 
         }

         hodD = doc["HD"];
         hodD = checkMove(2, hodD);
         if (hodD > tmpHodD) {
            hodD = tmpHodD; 
         }

         drillToolL = doc["OL"];
         drillToolR = doc["OD"];

         slowHodL = doc["PHL"];
         slowHodLSpeed = doc["PHLH"];

         slowHodD = doc["PHD"];
         slowHodDSpeed = doc["PHDH"];

         povrtavanjeL = doc["POVL"];
         povrtavanjeD = doc["POVD"];
         
         drill();
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
      } else if (action2 == "cut") {
        hodZaga = doc["MZ"];
        slowHodZaga = doc["PHZ"];
        slowHodZagaSpeed = doc["PHZH"];
        cut();
        StaticJsonDocument<200> doc2;
        doc2["status"] = "done";
        serializeJson(doc2, Serial);
        Serial.println();
      } else if (doc["A"] == "moveS") {
        moveStepper(doc["IDS"], doc["MS"]);
        StaticJsonDocument<200> doc2;
        doc2["status"] = "done";
        JsonArray data = doc2.createNestedArray("data");
        for (int i = 1; i <8; i++) {
          data.add(returnStepperPosition(i));
        }
        serializeJson(doc2, Serial);
        Serial.println();
      } else if (doc["A"] == "spindle") {
        runSpindle(doc["IDS"], doc["T"]);
        Serial.println("done");
      } else if (doc["A"] == "CTL" || doc["A"] == "CTR") {
        if (doc["A"] == "CTL") {
          drillToolL = doc["T"];
        } else {
          drillToolR = doc["T"];
        }
        setupBothTool();
        Serial.println("done");
      } else if (doc["A"] == "spindleA") {
        allSpindle(doc["T"]);
        Serial.println("done");
      }
   }

}

boolean homming11() {
  digitalWrite(LED_BUILTIN, HIGH); 
  delay(5000);
  digitalWrite(LED_BUILTIN, LOW);
  return true;
}

boolean setupTool() {
  switch(drillTool) {
    case 1:
      switchTool();
  }
}

boolean setupBothTool() {
  switch(drillToolL) {
    case 1:
      pneumatikaVentil3 = HIGH;
      delay(500);
      while(pneumatikaSenzor3) {}
      pneumatikaVentil1 = LOW;
      while(pneumatikaSenzor1) {}
      delay(1000);
      break;

  case 3:
      pneumatikaVentil1 = HIGH;
      delay(500);
      while(!pneumatikaSenzor1) {}
      pneumatikaVentil3 = LOW;
      while(!pneumatikaSenzor3) {}
      delay(1000);
      break;
  }

  switch(drillToolR) {
    case 2:
      pneumatikaVentil4 = HIGH;
      delay(500);
      while(pneumatikaSenzor4) {}
      pneumatikaVentil2 = LOW;
      while(pneumatikaSenzor2) {}
      delay(1000);
      break;
  case 4:
      pneumatikaVentil2 = HIGH;
      delay(500);
      while(!pneumatikaSenzor2) {}
      pneumatikaVentil4 = LOW;
      while(!pneumatikaSenzor4) {}
      delay(1000);
      break;
  }
}


boolean drill() {
  // žaga do konca
  stepper7.moveTo(-400);
  stepper7.runToPosition();

  pneumatikaVentilPrijemalo = LOW;
  
  setupBothTool();

  stepper1.moveTo(hodL-slowHodL);
  stepper2.moveTo(hodD-slowHodD);

  bool stepper1R,stepper2R;
  do {
    stepper1R = stepper1.run();
    stepper2R = stepper2.run();
  } while (stepper1R || stepper2R);

  // slow down before drilling
  stepper1.moveTo(hodL);
  stepper1.setAcceleration(slowHodLSpeed);
  stepper1.setMaxSpeed(slowHodLSpeed);
  
  stepper2.moveTo(hodD);
  stepper2.setAcceleration(slowHodDSpeed);
  stepper2.setMaxSpeed(slowHodDSpeed);

  runSpindle(drillToolL,0);
  runSpindle(drillToolR,0);

  stepper1R = false;
  stepper2R = false;
  do {
    stepper1R = stepper1.run();
    stepper2R = stepper2.run();
  } while (stepper1R || stepper2R);


  stepper1.setAcceleration(6000.0);
  stepper1.setMaxSpeed(12000);
  stepper2.setAcceleration(6000.0);
  stepper2.setMaxSpeed(12000);
  
  stepper1.moveTo((hodL-slowHodL));
  stepper2.moveTo((hodD-slowHodD));
  stepper1R = false;
  stepper2R = false;
  do {
    stepper1R = stepper1.run();
    stepper2R = stepper2.run();
  } while (stepper1R || stepper2R);


  runSpindle(5,0);
  stepper5.moveTo(povrtavanjeL);
  stepper5.runToPosition();
  stepper5.moveTo(pozicijaD + 3200);
  stepper5.runToPosition();

  runSpindle(6,0);
  stepper6.moveTo(povrtavanjeD);
  stepper6.runToPosition();
  stepper6.moveTo(pozicijaL + 3200);
  stepper6.runToPosition();

  runSpindle(drillToolL,1);
  runSpindle(drillToolR,1);
  runSpindle(5,1);
  runSpindle(6,1);

  pneumatikaVentilPrijemalo = HIGH;
}

boolean cut() {

  pneumatikaVentilPrijemalo = LOW;

  stepper1.moveTo(0);
  stepper5.moveTo(0);
  
  bool stepper1R,stepper5R;
  do {
    stepper1R = stepper5.run();
    stepper5R = stepper5.run();
  } while (stepper1R || stepper5R);

  int hodZ = checkMove(7,hodZaga);

  runSpindle(7,0);
  delay(4000);  

  stepper7.moveTo(hodZ-slowHodZaga);
  stepper7.runToPosition();

  stepper7.setAcceleration(24000);
  stepper7.setMaxSpeed(slowHodZagaSpeed);
  stepper7.moveTo(hodZ);
  stepper7.runToPosition();
  runSpindle(7,1);

  stepper7.setAcceleration(20000);
  stepper7.setMaxSpeed(20000);
  stepper7.moveTo(-400);
  stepper7.runToPosition();
/*
  stepper1.moveTo(hodL-slowHodL);
  stepper5.moveTo(pozicijaD + 3200);

  stepper1R = false;
  stepper5R = false;
  do {
    stepper1R = stepper1.run();
    stepper5R = stepper5.run();
  } while (stepper1R || stepper5R);
*/
  pneumatikaVentilPrijemalo = HIGH;
}


boolean drill2() {
  // žaga do konca
  stepper7.moveTo(-400);
  stepper7.runToPosition();

  pneumatikaVentilPrijemalo = LOW;
  setupTool();

  stepper1.moveTo(hodL);
  stepper2.moveTo(hodD);
  
  
  bool stepper1R,stepper2R;
  do {
    stepper1R = stepper1.run();
    stepper2R = stepper2.run();
  } while (stepper1R || stepper2R);

  stepper1.moveTo((hodL-povratekL));
  stepper2.moveTo((hodD-povratekD));
  stepper1R = false;
  stepper2R = false;
  do {
    stepper1R = stepper1.run();
    stepper2R = stepper2.run();
  } while (stepper1R || stepper2R);

  
  stepper5.moveTo(povrtavanjeL);
  stepper5.runToPosition();
  stepper5.moveTo(pozicijaL);
  stepper5.runToPosition();
  
  stepper6.moveTo(povrtavanjeD);
  stepper6.runToPosition();
  stepper6.moveTo(pozicijaD);
  stepper6.runToPosition();

  pneumatikaVentilPrijemalo = HIGH;
    
}


boolean changePositionL(int pozicija3) {

  pozicija3 = checkMove(3, pozicija3);
  if (pozicija3 < pozicijaL) {
      //minPovratekPovrtavanjeL = pozicija3;
      stepper6.moveTo(pozicija3 + 3200);
      stepper6.runToPosition();
  }

  if (pozicija3 > pozicijaL) {
      if (pozicija3 > 4800) {
        tmpHodL = maxHod - (pozicija3 - 4800);
        if (stepper1.currentPosition() > tmpHodL) {
          stepper1.moveTo(tmpHodL);
          stepper1.runToPosition();
        }
      } else {
        tmpHodL = 14400;
      }
  }
 
  pozicijaL = pozicija3;
  stepper3.moveTo(pozicijaL);
  bool stepper3R;
  do {
    stepper3R = stepper3.run();
  } while (stepper3R);

}

boolean changePositionD(int pozicija4) {

  pozicija4 = checkMove(4, pozicija4);
  if (pozicija4 < pozicijaD) {
      //minPovratekPovrtavanjeD = pozicija4;
      stepper5.moveTo(pozicija4 + 3200);
      stepper5.runToPosition();
  }

  if (pozicija4 > pozicijaD) {
      if (pozicija4 > 4800) {
        tmpHodD = maxHod - (pozicija4 - 4800);
        if (stepper2.currentPosition() > tmpHodD) {
          stepper2.moveTo(tmpHodD);
          stepper2.runToPosition();
        }
      } else {
        tmpHodD = 14400;
      }
  }

  pozicijaD = pozicija4;
  
  stepper4.moveTo(pozicijaD);
  bool stepper4R;
  do {
    stepper4R = stepper4.run();
  } while (stepper4R);
}


int checkMove(int idStepper, int steps) {

  switch(idStepper) {
    case 1:
      if (steps > tmpHodL) {
        return tmpHodL;
      }
      break;
    case 2:
      if (steps > tmpHodD) {
        return tmpHodD;
      }
      break;
    case 3:
    case 4:
      if (steps > maxPozicija) {
        return maxPozicija; 
      }
      break;
    case 5:
    case 6: 
    case 7:
      if (steps > 13680 ) {
        return 13680;
      }
      break;
  }

  return steps;
  
}
boolean moveStepper(int idStepper, int moveToStep) {

  int safeMove = checkMove(idStepper, moveToStep);

  switch(idStepper) {
    case 1: 
      stepper1.moveTo(safeMove);
      stepper1.runToPosition();
      break;
    case 2: 
      stepper2.moveTo(safeMove);
      stepper2.runToPosition();
      break;  
    case 3: 
      changePositionL(safeMove);
      /*stepper3.moveTo(safeMove);
      stepper3.runToPosition();*/
      break;
    case 4: 
      changePositionD(safeMove);
      /*
      stepper4.moveTo(safeMove);
      stepper4.runToPosition();*/
      break;
    case 5: 
      stepper5.moveTo(safeMove);
      stepper5.runToPosition();
      break;
    case 6: 
      stepper6.moveTo(safeMove);
      stepper6.runToPosition();
      break;
    case 7: 
      stepper7.moveTo(safeMove);
      stepper7.runToPosition();
      break;
  }
  return true;
}

int returnStepperPosition(int idStepper) {

  switch(idStepper) {
    case 1: 
      return stepper1.currentPosition();
    case 2: 
      return stepper2.currentPosition();  
    case 3: 
      return stepper3.currentPosition();
    case 4: 
      return stepper4.currentPosition();
    case 5: 
      return stepper5.currentPosition();
    case 6: 
      return stepper6.currentPosition();
    case 7: 
      return stepper7.currentPosition();
  }
  return 0;
}




boolean runSpindle(int idSpindle, int toggle) {

  switch(idSpindle) {
    case 1: 
      digitalWrite(spindel1, toggle == 0 ? LOW : HIGH);break;
    case 2: 
      digitalWrite(spindel2, toggle == 0 ? LOW : HIGH);break;  
    case 3: 
      digitalWrite(spindel3, toggle == 0 ? LOW : HIGH);break;
    case 4: 
      digitalWrite(spindel4, toggle == 0 ? LOW : HIGH);break;
    case 5: 
      digitalWrite(spindel5, toggle == 0 ? LOW : HIGH);break;
    case 6: 
      digitalWrite(spindel6, toggle == 0 ? LOW : HIGH);break;
    case 7: 
      digitalWrite(zaga, toggle == 0 ? LOW : HIGH);break;
  }
  return true;
}

boolean allSpindle(int action) {
  for(int i = 1; i <=7; i++) {
    if (i == 7 && action == 0) {
      continue;
    }
    runSpindle(i, action);
  }
}

boolean homming() {

  if (!homming7()) {
    while (1) {};
  }

  if (!homming5()) {
    while (1) {};
  }
  
  if (!homming6()) {
    while (1) {};
  }

  if (!homming1()) {
    while (1) {};
  }

  if (!homming2()) {
    while (1) {};
  }

  if (!homming3()) {
    while (1) {};
  }

  if (!homming4()) {
    while (1) {};
  }

  
  //hommingPneu();

  stepper1.setCurrentPosition(0);
  stepper2.setCurrentPosition(0);
  stepper3.setCurrentPosition(0);
  stepper4.setCurrentPosition(0);
  stepper5.setCurrentPosition(0);
  stepper6.setCurrentPosition(0);
  stepper7.setCurrentPosition(0);

  stepper3.moveTo(pozicijaLNull);
  stepper3.runToPosition();

  stepper4.moveTo(pozicijaDNull);
  stepper4.runToPosition();

  stepper3.setCurrentPosition(0);
  stepper4.setCurrentPosition(0);

  return true;
}


boolean hommingPneu() {
  pneumatikaVentil1 = LOW;
  delay(500);
  while(pneumatikaSenzor1) {}
  pneumatikaVentil1 = HIGH;
  delay(500);
  while(!pneumatikaSenzor1) {}  

  delay(1000);

  pneumatikaVentil2 = LOW;
  delay(500);
  while(pneumatikaSenzor2) {}
  pneumatikaVentil2 = HIGH;
  delay(500);
  while(!pneumatikaSenzor2) {}  

  delay(1000);
  
  pneumatikaVentil3 = LOW;
  delay(500);
  while(!pneumatikaSenzor3) {}
  delay(500);
  pneumatikaVentil3 = HIGH;
  while(pneumatikaSenzor3) {}  

  delay(1000);

  pneumatikaVentil4 = LOW;
  delay(500);
  while(!pneumatikaSenzor4) {}
  delay(500);
  pneumatikaVentil4 = HIGH;
  while(pneumatikaSenzor4) {} 

  delay(1000);

  pneumatikaVentilPrijemalo = LOW;
  delay(500);
  while(pneumatikaSenzorPrijemalo) {}
  delay(500);
  pneumatikaVentilPrijemalo = HIGH;
  while(!pneumatikaSenzorPrijemalo) {} 
  
  return true;
}

boolean switchTool() {
  switch(drillTool) {
    case 1:
      pneumatikaVentil3 = HIGH;
      while(pneumatikaSenzor3) {}
      pneumatikaVentil1 = LOW;
      while(pneumatikaSenzor1) {}
      delay(1000);

      pneumatikaVentil4 = HIGH;
      while(pneumatikaSenzor4) {}
      pneumatikaVentil2 = LOW;
      while(pneumatikaSenzor2) {}
      delay(1000);
      break;
  }
}


boolean homming1() {

  directionPin1 = LOW;

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

  directionPin1 = HIGH;
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

  directionPin1 = HIGH;

  return true;
}

void moveOneStep1() {
    //directionPin = LOW;

    stepPin1 = HIGH;
    delayMicroseconds(40);
    stepPin1 = LOW;
    delayMicroseconds(40);
 
}

boolean homming2() {

directionPin2 = LOW;
  if (hommingSenzor2 == LOW)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {

      if (hommingSenzor2 == HIGH)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep2();
      delayMicroseconds(320);
    }

    if (limitSwitchFlag == false)
      return (false);
  }

  directionPin2 = HIGH;
  if (hommingSenzor2 == HIGH)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {
      if (hommingSenzor2 == LOW)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep2();
      delayMicroseconds(16000);
    }

    if (limitSwitchFlag == false)
      return (false);
  }

  directionPin2 = HIGH;

  return true;
}

void moveOneStep2() {
  //directionPin = LOW;

    stepPin2 = HIGH;
    delayMicroseconds(40);
    stepPin2 = LOW;
    delayMicroseconds(40);
 
}

boolean homming3() {

  directionPin3 = LOW;
  if (hommingSenzor3 == LOW)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {

      if (hommingSenzor3 == HIGH)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep3();
      delayMicroseconds(1000);
    }

    if (limitSwitchFlag == false)
      return (false);
  }

  directionPin3 = HIGH;
  if (hommingSenzor3 == HIGH)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {
      if (hommingSenzor3 == LOW)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep3();
      delayMicroseconds(16000);
    }

    if (limitSwitchFlag == false)
      return (false);
  }

  directionPin3 = HIGH;

  return true;
}

void moveOneStep3() {
  //directionPin = LOW;

    stepPin3 = HIGH;
    delayMicroseconds(40);
    stepPin3 = LOW;
    delayMicroseconds(40);
 
}

boolean homming4() {

  directionPin4 = LOW;
  if (hommingSenzor4 == LOW)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {

      if (hommingSenzor4 == HIGH)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep4();
      delayMicroseconds(1000);
    }

    if (limitSwitchFlag == false)
      return (false);
  }

  directionPin4 = HIGH;
  if (hommingSenzor4 == HIGH)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {
      if (hommingSenzor4 == LOW)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep4();
      delayMicroseconds(16000);
    }

    if (limitSwitchFlag == false)
      return (false);
  }

  directionPin4 = HIGH;

  return true;
}

void moveOneStep4() {
  //directionPin = LOW;

    stepPin4 = HIGH;
    delayMicroseconds(40);
    stepPin4 = LOW;
    delayMicroseconds(40);
 
}

boolean homming5() {

  directionPin5 = LOW;

  if (hommingSenzor5 == LOW)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {

      if (hommingSenzor5 == HIGH)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep5();
      //delayMicroseconds(20000);
      delayMicroseconds(320);
    }

    if (limitSwitchFlag == false)
      return (false);
  }

  directionPin5 = HIGH;
  if (hommingSenzor5 == HIGH)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {
      if (hommingSenzor5 == LOW)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep5();
      delayMicroseconds(16000);
    }

    if (limitSwitchFlag == false)
      return (false);
  }

  directionPin5 = HIGH;

  return true;
}

void moveOneStep5() {
    //directionPin = LOW;

    stepPin5 = HIGH;
    delayMicroseconds(40);
    stepPin5 = LOW;
    delayMicroseconds(40);
 
}

boolean homming6() {

  directionPin6 = LOW;

  if (hommingSenzor6 == LOW)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {

      if (hommingSenzor6 == HIGH)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep6();
      //delayMicroseconds(20000);
      delayMicroseconds(320);
    }

    if (limitSwitchFlag == false)
      return (false);
  }

  directionPin6 = HIGH;
  if (hommingSenzor6 == HIGH)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {
      if (hommingSenzor6 == LOW)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep6();
      delayMicroseconds(16000);
    }

    if (limitSwitchFlag == false)
      return (false);
  }

  directionPin6 = HIGH;

  return true;
}

void moveOneStep6() {
    //directionPin = LOW;

    stepPin6 = HIGH;
    delayMicroseconds(40);
    stepPin6 = LOW;
    delayMicroseconds(40);
 
}


boolean homming7() {

  directionPin7 = LOW;

  if (hommingSenzor7 == LOW)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {

      if (hommingSenzor7 == HIGH)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep7();
      //delayMicroseconds(20000);
      delayMicroseconds(320);
    }

    if (limitSwitchFlag == false)
      return (false);
  }

  directionPin7 = HIGH;
  if (hommingSenzor7 == HIGH)
  {
    boolean limitSwitchFlag = false;
    while (1)
    {
      if (hommingSenzor7 == LOW)
      {
        limitSwitchFlag = true;
        break;
      }

      moveOneStep7();
      delayMicroseconds(4000);
    }

    if (limitSwitchFlag == false)
      return (false);
  }

  directionPin7 = HIGH;

  return true;
}

void moveOneStep7() {
    //directionPin = LOW;

    stepPin7 = HIGH;
    delayMicroseconds(40);
    stepPin7 = LOW;
    delayMicroseconds(40);
 
}

void triggerAlarm() {
  alarmTripped = true;
}
