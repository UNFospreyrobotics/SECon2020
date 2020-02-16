//ST 2x12 is in analog mode
//resistor and capacitor used to condition PWM signal into a better DC-like signal

int S1 = 5; //pin 5 connected to ST pin S1 as analog input 0-5V
int S2 = 6; //pin 6  ""              "" S2 ""               ""
char pyByte = ' '; //initializing char for serial comm

void robotForward()
{
  analogWrite(S1, 255); //value of 255 writes 5V, which the ST reads as full speed forward
  analogWrite(S2, 255);
}

void robotReverse()
{
  analogWrite(S1, 0); //value of 0 writes 0V, which the ST reads as full speed reverse
  analogWrite(S2, 0); 
}
//turn both motors opposite directions, making robot turn clockwise
void robotCW()
{
  analogWrite(S1, 255);
  analogWrite(S2, 0);
}

//make robot turn anti-clockwise
void robotACW()
{
  analogWrite(S1, 0);
  analogWrite(S2, 255);
}

void robotStop()
{
  analogWrite(S1, 127); //value of 127 writes roughly 2.5V, which the ST reads as stop
  analogWrite(S2, 127);
}

void setup() 
{
  Serial.begin(9600);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  //Serial.println("Motor Arduino UNO active");

}

void loop() 
{
//  robotStop();
//  delay(500);
//  robotCW();
//  delay(1000);
//  robotStop();
//  delay(1500);
//  robot(ACW);
//  delay(500);
  if(Serial.available())
  {
    pyByte = Serial.read(); //read command byte sent from Python program
  }
  
  switch (pyByte) //execute motor control command based on read pyByte char
  {
    case 'S': 
      robotStop();
      break;
    case 'F': 
      robotForward();
      break;
    case 'R': 
      robotReverse();
      break;
    case 'C': 
      robotCW();
      break;
    case 'A': 
      robotACW();
      break;
    default: //precaution: stops robot if no assigned command is received
      robotStop();
      break;
  }
  delay(50); //may not be needed
  
}
