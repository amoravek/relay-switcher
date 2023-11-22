import RPi.GPIO as GPIO
import time

RELAY_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

is_on = True

try:
    while True:
        print(f'is_on: {is_on}')
        
        if is_on:
            GPIO.output(RELAY_PIN, GPIO.HIGH)
        else:  
            GPIO.output(RELAY_PIN, GPIO.LOW)

        time.sleep(5)
        is_on = not is_on
finally:
    GPIO.cleanup()
