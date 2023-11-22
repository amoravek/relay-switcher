import RPi.GPIO as GPIO
import time

RELAY_PIN = 23

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

data = True

while True:
    GPIO.output(RELAY_PIN, data)
    time.sleep(5)
    data = not data

GPIO.cleanup()
