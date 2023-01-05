import requests
import configparser
import pathlib
import sys
import time
import RPi.GPIO as GPIO

actual_directory = str(pathlib.Path(__file__).parent.resolve())
config = configparser.ConfigParser()
config.read_file(open(r'{}/configuracoes.ini'.format(actual_directory)))

chave = config.get('licenca', 'chave')

cliente_1 = config.get(sys.argv[1], 'cliente')
gpio_pino_1 = int(config.get(sys.argv[1], 'gpio_pino'))
barreira_1 = config.get(sys.argv[1], 'barreira')
segundos_aberto_1 = int(config.get(sys.argv[1], 'segundos_aberto'))

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(gpio_pino_1, GPIO.OUT, initial=GPIO.HIGH)
GPIO.output(gpio_pino_1, GPIO.HIGH)

def abrirfechar():
    try:
        r = requests.get('{}/equipamentos/abrirfechar?chave={}&barreira={}'.format(cliente_1, chave, barreira_1), timeout=3)
    except requests.exceptions.Timeout:
        print('Error: abrirfechar')
        time.sleep(5)
    except:
        print('Error: abrirfechar')
        time.sleep(5)
    else:        
        if r.status_code == 200:
            if(r.text == 'abrir'):
                GPIO.output(gpio_pino_1, GPIO.LOW)
                time.sleep(0.15)
                GPIO.output(gpio_pino_1, GPIO.HIGH)
            
            if(r.text == 'emergencia_abrir'):
                GPIO.output(gpio_pino_1, GPIO.LOW)

            if(r.text == 'emergencia_fechar'):
                GPIO.output(gpio_pino_1, GPIO.HIGH)

while True:
    abrirfechar()
    time.sleep(3)