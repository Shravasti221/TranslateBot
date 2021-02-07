#include<Servo.h>

Servo servoVer; //Vertical Servo
Servo servoHor1; //Horizontal Servo
Servo servoHor2;
Servo servoMouth;
int x;
int y;
int m;

int prevX;
int prevY;

void setup()
{
  Serial.begin(9600);
  Serial.flush();
  
  servoVer.attach(5); //Attach Vertical Servo to Pin 5
  servoHor1.attach(6); //Attach Horizontal Servo to Pin 6
  servoHor2.attach(7); //Attach Horizontal Servo to Pin 7
  servoMouth.attach(8);//Attach Servo controlling mouth to pin 8

  //testing the servo and connections
  servoVer.write(60);
  servoHor1.write(10);
  servoHor2.write(10);
  servoMouth.write(50);

  delay(1000);

  // initial positions
  servoVer.write(90);
  servoHor1.write(90);
  servoHor2.write(90);
  servoMouth.write(0);
}

void Pos()
{
  if(prevX != x || prevY != y)
  {
    int servoX = map(x, 600, 0, 70, 179);
    int servoY = map(y, 450, 0, 179, 95);

    servoX = min(servoX, 179);
    servoX = max(servoX, 70);
    servoY = min(servoY, 179);
    servoY = max(servoY, 95);
    
    servoHor1.write(servoX);
    servoHor2.write(servoX);
    servoVer.write(servoY);
  }
  servoMouth.write(m);
}

void loop()
{
  if(Serial.available() > 0)
  {
    if(Serial.read() == 'X')
    {
      x = Serial.parseInt();
      if(Serial.read() == 'Y')
      {
        y = Serial.parseInt();
        if(Serial.read() == 'M')
        {
          m = Serial.parseInt();
          Pos();
        }

     }
      
    }
    while(Serial.available() > 0)
    {
      Serial.read();
    }
  } 
}
  
