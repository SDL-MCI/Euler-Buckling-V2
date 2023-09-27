#include <Arduino.h>
#include "HX711.h"

//////////
/* Pins */
//////////

#define pin_SCK_1 13
#define pin_DT_1 14
#define pin_SCK_2 20
#define pin_DT_2 15
#define pin_SCK_3 18
#define pin_DT_3 16
#define pin_SCK_4 19
#define pin_DT_4 17

///////////////////////
/* Variables/Objects */
///////////////////////

int8_t rx_buffer[4] = {0};  // receive buffer (USB VCOM)
char tx_buffer[16] = {0};    // send buffer (USB VCOM)
float scalingFac = 46200;   // scaling factor (from calibration)
float result1 = 0;          // Measurement Result ADC 1
float result2 = 0;          // Measurement Result ADC 2
float result3 = 0;          // Measurement Result ADC 3
float result4 = 0;          // Measurement Result ADC 4
int8_t dt = 0;              // Measurement Duration
uint16_t i = 0;
HX711 scale1;               // ADC 1 -> Channel A
HX711 scale2;               // ADC 2 -> Channel A
HX711 scale3;               // ADC 3 -> Channel A
HX711 scale4;               // ADC 4 -> Channel A           
IntervalTimer USB_Timer;

///////////
/* Setup */
///////////
void setup()
{
    // Serial COM
    Serial.begin(9600);
    // load cell config
    scale1.begin(pin_DT_1,pin_SCK_1);
    scale2.begin(pin_DT_2,pin_SCK_2);
    scale3.begin(pin_DT_3,pin_SCK_3);
    scale4.begin(pin_DT_4,pin_SCK_4);
    scale1.set_scale(scalingFac);
    scale2.set_scale(scalingFac);
    scale3.set_scale(scalingFac);
    scale4.set_scale(scalingFac);
    // Timed interrupt priorities
    USB_Timer.priority(0);
}


void fun_reset()
{   // enables the measurements to be executed successively
    Serial.flush();
    USB_Timer.end();
    result1 = 0;
    result2 = 0;
    result3 = 0;
    result4 = 0;
    i = 0;
}

void ISR_USB_SEND()
{
    if ((uint16_t)((dt+1)*20) > i)
    {
        // Write into 16 character long buffer
        memcpy(&tx_buffer[0], (const char *)(&result1), 4);
        memcpy(&tx_buffer[4], (const char *)(&result2), 4);
        memcpy(&tx_buffer[8], (const char *)(&result3), 4);
        memcpy(&tx_buffer[12], (const char *)(&result4), 4);
        Serial.write(tx_buffer, 16);
    }
    else
    {
        fun_reset();
    }
    i++;
}

void serialEvent()
{   // When serial data is received the timed interrupts start and the tare function is executed
    scale1.tare();
    delay(500);
    scale2.tare();
    delay(500);
    scale3.tare();
    delay(500);
    scale4.tare();
    delay(500);
    Serial.readBytes((char *)rx_buffer, 4); // read serial buffer
    dt = rx_buffer[2];                      // determine duration of the measurement
    USB_Timer.begin(ISR_USB_SEND, 50000);   // 20 Hz
}

void loop() {
    if ((uint16_t)((dt+1)*20) > i)
    {
        result1 = (float)(scale1.get_units(1));
        result2 = (float)(scale2.get_units(1));
        result3 = (float)(scale3.get_units(1));
        result4 = (float)(scale4.get_units(1));
    }
}