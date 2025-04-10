import RPi.GPIO as GPIO
import time

SERVO_PIN = 37  # Altere para um dos pinos que você conectou o servo

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz PWM
pwm.start(7.5)  # Posição inicial

try:
    while True:
        pwm.ChangeDutyCycle(5)  # Girar para uma posição
        time.sleep(1)
        pwm.ChangeDutyCycle(10)  # Girar para outra posição
        time.sleep(1)
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
