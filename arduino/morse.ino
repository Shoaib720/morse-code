// C++ code
//

int wpm = 15;
int ledPin = 13;
int buzzerPin = 8;
long dot_length_ms = (1.2/wpm)*1000;
long dash_length_ms = 3 * dot_length_ms;
long space_within_letter_ms = dot_length_ms;
long space_between_letters_ms = 3 * dot_length_ms;
long space_between_words_ms = 7 * dot_length_ms;

void setup()
{
  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  Serial.begin(9600);
  Serial.setTimeout(10); 
}

void loop()
{
  if (Serial.available() > 0) {
    String inputString = Serial.readStringUntil('\n');
    inputString.trim();
    
    for(int i=0; i < inputString.length(); i++){
      char c = inputString.charAt(i);
      if (c == '.') {
        digitalWrite(ledPin, HIGH);
        tone(buzzerPin, 523);
        delay(dot_length_ms);
        digitalWrite(ledPin, LOW);
        noTone(buzzerPin);
        delay(space_within_letter_ms);
      }
      else if (c == '-') {
        digitalWrite(ledPin, HIGH);
        tone(buzzerPin, 523);
        delay(dash_length_ms);
        digitalWrite(ledPin, LOW);
        noTone(buzzerPin);
        delay(space_within_letter_ms);
      }
      else if (c == '_') {
        delay(space_between_letters_ms);
      }
      else if (c == ' ') {
        delay(space_between_words_ms);
      }
      else {
        Serial.print("Invalid code: ");
        Serial.println(c);
      }
    }
      Serial.println("DONE");
  }
}