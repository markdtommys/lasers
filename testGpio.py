try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
import time

print("Setting to BCM pin mode")
GPIO.setmode(GPIO.BCM)

print("Setting BCM6 to be OUTPUT")
GPIO.setup(6, GPIO.OUT)

print("Setting BCM6 to LOW")
GPIO.output(6, GPIO.LOW)

print("Sleeping for 3 secs")
time.sleep(3)

print("Setting BCM6 to HIGH")
GPIO.output(6, GPIO.HIGH)

print("Cleaning up")
GPIO.cleanup()
