
import RPi.GPIO as GPIO

# Use pin numbers as inputs
GPIO.setmode(GPIO.BOARD)
#GPIO.setmode(GPIO.BCM)

# Setup outpu
GPIO.setup(pin, GPIO.OUT)

# Setup input using internal pull up resistor
GPIO.setup(pin, GPIO.IN, pull_up_down_GPIO.PUD_UP)

# True = high
GPIO.output(pin,True)

# Clears all pins
GPIO.cleanup()

puslewave = GPIO.PWM(pin, hertz)
pulsewave.start(duty_cycle)
pulsewave.ChangeDutyCycle(duty_cycle)
pulsewave.ChangeFrequency(hertz)
pulsewave.stop()
