"""
--------------------------------------------------------------------------
Wearable Metronome
--------------------------------------------------------------------------
License:   
Copyright 2019 <Hoang Vu>

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this 
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------

Software for Wearable Metronome - Full description at https://www.hackster.io/hoangvu/wearable-metronome-53c2b7

"""
import time #to record/calculate time
import alsaaudio, wave, numpy
import Adafruit_BBIO.GPIO as GPIO #rename library to GPIO

import ht16k33_i2c as HT16K33 #i2c library for lcd screen
import alsaaudio, wave, numpy #for sound processing

import Adafruit_BBIO.ADC as ADC # for ADC pins
import Adafruit_BBIO.PWM as PWM # for PWM pins

# ------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------

BUTTON                       = "P1_29" #button GPIO117 = P2_2
BUZZER                       = "P2_4" #button GPIO58 = P2_4
LOWCORNER                    = 50 # change this variable to change sensitivity to different range of frequencies, must be smaller than MIDCORNER and smaller than 256
MIDCORNER                    = 180 # change this variable to change sensitivity to different range of frequencies, must be bigger than LOWCORNER and smaller than 256

RESET_TIME                   = 2.0
DUTY                         = 50
LEDRED                       = "P2_3" # PWM2 B
LEDBLUE                      = "P2_1" # PWM1 A
LEDGREEN                     = "P1_33" # PWM0 B



# ------------------------------------------------------------------------
# Main Tasks
# ------------------------------------------------------------------------

def setup():
    """Setup the hardware components."""
    
    # Initialize Display
    HT16K33.display_setup()
    HT16K33.update_display(0000)
    
    #Initialize Button
    GPIO.setup(BUTTON, GPIO.IN)
    GPIO.setup(BUZZER, GPIO.OUT)
   
# End def


def task():
    """Execute the main program."""
    base_tempo                 = 50        # Number of people to be displayed
    button_press_time            = 0.0      # Time button was pressed (in seconds)
    period = 60.0/base_tempo
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE)
    inp.setchannels(1)
    inp.setrate(44100)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(512)
    
    while(1):
    
        time_start = time.time()
        # Wait for button press
        while(GPIO.input(BUTTON) == 0):
            
        # Record time
                button_press_time = time.time()
        
        
        # Wait for button release
        while(GPIO.input(BUTTON) == 1):
            try:
                l, data = inp.read()
                a = numpy.fromstring(data, dtype='int16') # obtain data from microphone
                # print(len(a))
                freq = numpy.fft.rfft(a) # do a real time fast fourier transform on the microphone data
                # print(len(freq))
                """separate frequency response into 3 bands of frequencies """
                low = sum(abs(freq[:LOWCORNER])) 
                # print(low)
                mid = sum(abs(freq[LOWCORNER:MIDCORNER]))
                # print(mid)
            
                high = sum(abs(freq[MIDCORNER:]))
                # print(high)
                # print(a)
                maxvalue = max(low,mid,high) # find max value of low, mid and high for normalization
                
                GPIO.output(BUZZER, GPIO.LOW)
                
                """Duty cycle for each color of LED is set based on the magnitude of the frequency band"""
                
                PWM.set_duty_cycle(LEDRED,int(low/maxvalue*100))
                PWM.set_duty_cycle(LEDGREEN,int(mid/maxvalue*100))
                PWM.set_duty_cycle(LEDBLUE,int(high/maxvalue*100))
                
                if (time.time() - time_start)%period < period/2 and base_tempo > 50: # set the duty cycle to be 50% for both vibrators and LED
                    GPIO.output(BUZZER, GPIO.HIGH)
                    PWM.set_duty_cycle(LEDRED,0)
                    PWM.set_duty_cycle(LEDGREEN,0)
                    PWM.set_duty_cycle(LEDBLUE,0)
                    
                pass
            except:
                pass
        
           
            
        # Reset the program to base tempo and no vibration if button is pressed more than 2 seconds from the previous press
        if ((time.time() - button_press_time) > RESET_TIME): #if beyond 2 seconds
            base_tempo = 50
            GPIO.output(BUZZER, GPIO.LOW)
        else:
            if base_tempo == 200: # maximum tempo 
                pass
            else:
                base_tempo += 1
                period = 60.0/base_tempo
                    
        HT16K33.update_display(base_tempo) # update display of lcd
       
        
# End def


def cleanup():
    """Cleanup the hardware components. Returns 'dead' if cleaned up"""
    
    # Set Display to something fun to show program is complete
    PWM.cleanup()
    HT16K33.display_set_digit(0, 13)        # "D"
    HT16K33.display_set_digit(1, 14)        # "E"
    HT16K33.display_set_digit(2, 10)        # "A"
    HT16K33.display_set_digit(3, 13)        # "D"
   
     
# End def


# ------------------------------------------------------------------------
# Main script
# ------------------------------------------------------------------------

if __name__ == '__main__':
    setup()
    PWM.start(LEDRED,10 , 10000)
    PWM.start(LEDGREEN,10 , 10000)
    PWM.start(LEDBLUE,10 , 10000)
    base_tempo = 50
    try:
        print("Task is running.")
        task()
    except KeyboardInterrupt:
        pass

    cleanup
    print("Program Complete.")

