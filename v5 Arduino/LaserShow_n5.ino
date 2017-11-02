/*
  Takes commands as single line strings from the serial port
  
  Examples
  M09Hello World             Puts the Laser in Marquee mode displaying size 09 'Hello World'
  S20Hello World             Puts the Laser in Static mode displaying size 20 'Hello World'
  F50ALERT!                  Puts the Laser in Flashing mode displaying size 50 'ALERT!'
  A09PLANE                   Plays the 'PLANE' animation at size 09
  X                          Turns the laser off
  I1000                      Changes the output repeat interval to 1000mSecs (default is 3Secs)

  Created 24/10/2017
  Authors Neil,Mark and Tom
*/
 
// Extended from LaserShow ...

#include "Laser.h"
#include "Drawing.h"
#include "Cube.h"
#include "Objects.h"
#include "Logo.h"
String myteststring = "CHELTENHAM - 17C - WINDY";
int inputactive = 0;
String inputString = "";         // a String to hold incoming data
boolean stringComplete = false;  // whether the string is complete
int cnt = 0;
int laserMode = 0;
int laserCommand = 0;
String laserMsg = "";         // a String to hold the laser message
int laserAnim = 0;            // An int to hold the laser animation selected
int laserSize = 25;           // An int to hold the size to display things at [0..99]
unsigned long laserInterval = 3000; //Interval default = 3 seconds
unsigned long previousMillis = 0;
boolean repeat = false; // Flag to repeat display in this loop

// Create laser instance (with laser pointer connected to digital pin 5)
Laser laser(5);

void setup()
{  
  laser.init();
  
  // initialize serial:
  Serial.begin(9600);
  // reserve 200 bytes for the inputString:
  inputString.reserve(200);
}


void letterEffect()
{  
  String dyn = "MOTSYT";
  String lu  = "TOMMYS";
  int w = Drawing::stringAdvance(lu);
  laser.setScale(3048./w);
  laser.setOffset(2048,2048);
  for (int i = 0;i<35;i++) {
    Drawing::drawString(dyn, -w/2,0,4);
    for (int i = 0;i<8;i++){ 
      if (lu[i]>dyn[i]) dyn[i]++;
      if (lu[i]<dyn[i]) dyn[i]--;
    }
  }
  int clip = 0;
  for (int i = 0;i<60;i++) {
    laser.setClipArea(clip, 0, 4095-clip, 4095);
    Drawing::drawString(lu, -w/2,0,1);
    clip += 2048 / 50;
  }
  laser.resetClipArea();
}

void presents() {
  String str = "FRIKIN";
  int w = Drawing::stringAdvance(str);
  laser.setScale(3048./w);
  laser.setOffset(2048,2048);
  float scale = 0;
  for (int i = 0; i<70;i++) {
    scale += 0.01;
    laser.setScale(scale);
    Drawing::drawString(str,-w/2, 0);
  }
}

void arduino()
{
  String str = "ARDUINO";
  int w = Drawing::stringAdvance(str);
  laser.setScale(0.5);
  laser.setOffset(1024,1024);
  int count = 360/4;
  int angle = 45;
  for (int i = 0;i<count;i++) {
    Matrix3 world;
    world = Matrix3::rotateX(angle % 360);
    laser.setEnable3D(true);
    laser.setMatrix(world);
    laser.setZDist(2000);
    Drawing::drawString(str,-w/2,-500, 1);
    angle += 8;
  }
  laser.setEnable3D(false);
}

void laserShow()
{
  String str = "LASER";
  int w = Drawing::stringAdvance(str);
  int count = 360/4;
  int angle = 0;
  laser.setScale(0.5);
  for (int i = 0;i<count;i++) {
    Matrix3 world;
    laser.setEnable3D(true);
    world = Matrix3::rotateX(angle % 360);
    laser.setMatrix(world);
    laser.setZDist(4000);
    laser.setOffset(1024,1024 + 600);
    Drawing::drawString(str,-w/2,-500, 1);
    world = Matrix3::rotateY(angle % 360);
    laser.setMatrix(world);
    laser.setOffset(1024,1024 - 600);
    Drawing::drawString("SHOW",-w/2,-500, 1);
    angle += 8;
  }
  laser.setEnable3D(false);
}


// draw a circle using sin/cos
void circle() {
  const int scale = 12;
  laser.sendto(SIN(0)/scale, COS(0)/scale);
  laser.on();
  for (int r = 5;r<=360;r+=5)
  {    
    laser.sendto(SIN(r)/scale, COS(r)/scale);
  }
  laser.off();
}

// Draw circle and count down from 9 to 1
void countDown() {
  laser.setScale(1);
  laser.setOffset(2048,2048);
  int center = Drawing::advance('9');
  for (char j = '9';j>'0';j--) {
    float scale = 0.0;
    float step = 0.01;
    for (int i = 0;i<40;i++) {
      laser.setScale(1);
      circle();
      laser.setScale(scale);
      Drawing::drawLetter(j, -center/3, -center*2/3 + 100);   
      scale += step;
      step += 0.002;
    }
  }
}
void drawPlane()
{
  int count = 180;
  float scale = 1;
  laser.setScale(2);
  laser.setOffset(0,0);
  long x = 4096;
  long y = 4096;
  for (int i = 0;i<count;i++) {
    laser.setScale(scale);
    laser.setOffset(x,y);
    Drawing::drawObject(draw_plane, sizeof(draw_plane)/4);
    x -= 20*scale;
    y -= 20;
    scale += 0.01;
  }
}


// draws text as scroller from right to left
void drawScroller(String s, float scale = 0.5, int offsetY = 2048, int speed = 100)
{
  int charW = Drawing::advance('I'); // worst case: smallest char
  int maxChar = (4096. / (charW * scale) );
  if ( maxChar > 99 ) {
    Serial.println("DEBUG in drawScroller - maxChar limited to 99 was " + String(maxChar));
    maxChar=99;
  }
    
  // some senseful max buffer, don't use a very small scale...
  char buffer[100];
  for (int j = 0;j<maxChar;j++) {
    buffer[j] = ' ';
  }
  laser.setOffset(0,offsetY);
  laser.setScale(scale);
  int scrollX = 0;
  for (int c = 0; c < s.length() + maxChar; c++) {
    int currentScroll = Drawing::advance(buffer[0]);
    while (scrollX < currentScroll) {
      long time = millis();
      int x = -scrollX;;
      int y = 0;
      bool somethingDrawn = false;
      for (int i = 0;i<maxChar;i++) {
        if (buffer[i] != ' ') {
          somethingDrawn = true;
        }
        x += Drawing::drawLetter(buffer[i], x, y);
        if (x > 4096 / scale) {
          break;
        }
      }
      if (!somethingDrawn) { scrollX = currentScroll; }
      scrollX += speed / scale;
      long elapsed = millis() - time;
      if (elapsed < 50) { delay(50-elapsed); }

    }
    scrollX -= currentScroll;
    for (int k = 0;k<maxChar-1;k++) {
      buffer[k] = buffer[k+1];
    }
    if (c<s.length()) {
      buffer[maxChar-1] = s[c];
    } else{
      buffer[maxChar-1] = ' ';
    }
  }
}

String animations[17] = {"OFF","LETTEREFFECT","PRESENTS","ARDUINO","LASERSHOW","PLANE","LOGO","WELOVE"
                        ,"ARDUINO2DROTATE","WHATABOUT3D","ROTATECUBE","BIKE"
                        ,"GLOBE","ARDUINO3D","OBJECTS","JUMPINGTEXT","COUNTDOWN"};
                              
void loop() {

  // Look for commands coming in and set control variables
  acceptCommands();

  // Write out status info for debug
  outputStatus();
  
  // Decide what to output to the Laser
  // If laserMsg is set we should display a message ...
  if ( repeat )
  {
    if ( laserMsg.length() > 0 ) {
    
      drawScroller(String(laserMsg),laserSize/100.0,2048,100);
    
      //drawScroller(String("THIS PROJECT IS AVAILABLE ON INSTRUCTABLES.COM"),0.5,2048,100);
      //drawScroller(String(myteststring),0.25,2048,100);
    } else {
      switch( laserAnim )
      {
        case 0:
          // No Animation
          break;
        case 1:
          //letterEffect();        // index 1 type Animation name LETTEREFFECT
          break;
        case 2:
          //presents();            // index 2 type Animation name FRIKIN
          break;
        case 3:
          //arduino();             // index 3 type Animation name ARDUINO
          break;
        case 4:
          //laserShow();           // index 4 type Animation name LASERSHOW
          break;
        case 5:
          drawPlane();           // index 5 type Animation name PLANE
          break;
        case 6:
         //countDown();           // index 6 type Animation name COUNTDOWN
          break;
        case 7:
      
          break;
        case 8:
      
          break;
        case 9:
      
          break;
        case 10:
      
          break;
    
      
        default:
          // Do nothing
          break;
      }
    }
    repeat = false;
  }
}

// Return the text version of the current laser animation
String getLaserAnimation() {
  return animations[laserAnim];
}

// Return the text version of the current mode
String getLaserMode() {
  String res = "";
  
  switch( laserMode )
  {
    case 'A':
      res = "Animation";
      break;
    case 'M':
      res = "Marquee";
      break;
    case 'S':
      res = "Static";
      break;
    case 'F':
      res = "Flashing";
      break;
    case 'X':
      res = "Off";
      break;
    case 'I':
      res = "Interval";
      break;
    default:
      res = "Unknown";
  }
  return res;
}

void setLaserSize() {
      // Set size based on 2nd and 3rd characters
    laserSize = inputString.substring(1,3).toInt();
    Serial.println("DEBUG laserSize = " + (String)laserSize);
}

/*
  SerialEvent occurs whenever a new data comes in the hardware serial RX. This
  routine is run between each time loop() runs, so using delay inside loop can
  delay response. Multiple bytes of data may be available.
*/
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      // add it to the inputString:
      inputString += inChar;
    }
  }
}

/* Set control variables based on strings sent in on the serial port
   Control variables and what they mean ...
   laserAnim     : gets set to a number to select a specific animated object
   laserMode     : the way to display the text
   laserMsg      : text to display 
   laserSize     : size to display text or animation (0-99)
   laserInterval : Repeat interval mSecs
*/
void acceptCommands() {
    // print the string when a newline arrives:
  if (stringComplete) {
    cnt += 1;
    Serial.println("DEBUG You sent : " + inputString);
    
    // Get command based on first character
    laserCommand = inputString.charAt(0);
    Serial.println("DEBUG laserCommand = " + (String)laserCommand);
    
    String laserAnimStr = "";   
    switch(laserCommand) {
      case 'A':
        setLaserSize();
        laserAnimStr = inputString.substring(3);
        if ( laserAnimStr == "PLANE") {
          laserAnim = 5;
        } else if ( laserAnimStr == "BIKE" ) {
          laserAnim = 11;
        } else if ( laserAnimStr == "ARDUINO3D" ) {
          laserAnim = 13;
        } // Unknown animations leave the animation selected unchanged

        laserMode = laserCommand;
        Serial.println("DEBUG Laser mode set to " + getLaserMode() + " " + getLaserAnimation() + " selected");
        laserMsg="";
        break;
      case 'M':
        setLaserSize();
        laserMode = laserCommand;
        Serial.println("DEBUG Laser mode set to " + getLaserMode());
        // Only change the message if a new one is present
        if ( inputString.substring(3).length() > 1 )
        {
          laserMsg = inputString.substring(3);
          laserAnim = 0;
        }
        break;
      case 'S':
        setLaserSize();
        laserMode = laserCommand;
        Serial.println("DEBUG Laser mode set to " + getLaserMode());
        // Only change the message if a new one is present
        if ( inputString.substring(3).length() > 1 )
        {
          laserMsg = inputString.substring(3);
        }
        break;
      case 'F':
        setLaserSize();
        laserMode = laserCommand;
        Serial.println("DEBUG Laser mode set to " + getLaserMode());
        // Only change the message if a new one is present
        if ( inputString.substring(3).length() > 1 )
        {
          laserMsg = inputString.substring(3);
        }
        break;
      case 'X':
        laserMode = laserCommand;
        Serial.println("DEBUG Laser " + getLaserMode());
        laserMsg = "";
        laserAnim = 0;
        break;
      case 'I':
        laserInterval = inputString.substring(1).toInt();
        Serial.println("DEBUG Laser interval set to " + (String)laserInterval);
        break;
      default:
        Serial.println("DEBUG Laser Mode " + getLaserMode());
    }

    // clear the string:
    inputString = "";
    stringComplete = false;
  }
}

void outputStatus() {
  unsigned long currentMillis = millis();

  if ( laserInterval != 0 )
  {
    if (currentMillis - previousMillis >= laserInterval) {
      repeat = true;
      // output the message at each laserInterval 
      previousMillis = currentMillis;
      if ( laserMsg.length() > 0 ) 
      {
        // Output Laser message
        Serial.println( (String)currentMillis + " Mode " + getLaserMode() + " Size " + (String)laserSize + " Length " + (String)laserMsg.length() + " Msg " + laserMsg);
      }
      
      if ( laserAnim != 0 )
      {
        // Output laserAnimation
        Serial.println( (String)currentMillis + " Mode " + getLaserMode() + " Size " + (String)laserSize + " Animation " + getLaserAnimation());
      }
    }
  }  

}
