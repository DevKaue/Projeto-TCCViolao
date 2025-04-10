import RPi.GPIO as GPIO
import time

# Configura o modo da GPIO
GPIO.setmode(GPIO.BCM)

# Seleciona dois pinos para testar
pin1 = 18
pin2 = 23
GPIO.setup(pin1, GPIO.OUT)
GPIO.setup(pin2, GPIO.OUT)

try:
    for i in range(5):
        # Liga o primeiro pino GPIO
        GPIO.output(pin1, GPIO.HIGH)
        GPIO.output(pin2, GPIO.LOW)
        print(f"Pino {pin1} ligando e pino {pin2} desligado.")
        time.sleep(1) # Para por 1 segundo

        # Liga o segundo pino GPIO
        GPIO.output(pin1, GPIO.LOW)
        GPIO.output(pin2, GPIO.HIGH)
        print(f"Pino {pin1} ligando e pino {pin2} desligado.")
        time.sleep(1) # Para por 1 segundo
except KeyboardInterrupt:
    pass 
finally:
    # Limpa a configurações dos GPIO's
    GPIO.cleanup()
    print('Configurações dos GPIOs limpas.')

