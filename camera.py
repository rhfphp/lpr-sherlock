#!/usr/bin/env python3
from __future__ import print_function

import sys
import threading
import cv2 as cv
import json
import time
import requests
import os
import _thread
from datetime import datetime
import RPi.GPIO as GPIO
import pathlib
import configparser

import imutils
from imutils.video import VideoStream

pid = os.getpid()

actual_directory = str(pathlib.Path(__file__).parent.resolve())
config = configparser.ConfigParser()
config.read_file(open(r'{}/configuracoes.ini'.format(actual_directory)))

chave = config.get('licenca', 'chave')
tipo_de_ocr = config.get('licenca', 'tipo_de_ocr')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

cliente = {}
barreira = {}
gpio_pino = {}
segundos_aberto = {}
rtsp_link = {}
direcao_veiculo = {}
abrir_rele_sem_verificar = {}
detectar_moto = {}
identificacao = {}
cnt = {}
cap = {}
fresh = {}
rtsps = []

for rtsp in config.sections():
    if(rtsp == 'licenca'):
        break
    
    # configs
    rtsps.append(rtsp)
    cliente[rtsp] = config.get(rtsp, 'cliente')
    barreira[rtsp] = config.get(rtsp, 'barreira')
    gpio_pino[rtsp] = int(config.get(rtsp, 'gpio_pino'))
    segundos_aberto[rtsp] = int(config.get(rtsp, 'segundos_aberto'))
    rtsp_link[rtsp] = config.get(rtsp, 'rtsp_link')
    direcao_veiculo[rtsp] = config.get(rtsp, 'direcao_veiculo')
    abrir_rele_sem_verificar[rtsp] = config.get(rtsp, 'abrir_rele_sem_verificar')
    detectar_moto[rtsp] = config.get(rtsp, 'detectar_moto')
    identificacao[rtsp] = config.get(rtsp, 'identificacao')
    GPIO.setup(gpio_pino[rtsp], GPIO.OUT, initial=GPIO.HIGH)
    GPIO.output(gpio_pino[rtsp], GPIO.HIGH)
    cap[rtsp] = VideoStream(rtsp_link[rtsp]).start()


if(tipo_de_ocr == 'Nuvem'):
    link_ocr = 'http://192.168.25.233:8081/?chave={}'.format(chave)
else:
    link_ocr = tipo_de_ocr


def fechar_portao(sleep, porta, status):
    time.sleep(sleep)
    # print('Fechei Portao ' + str(datetime.now().strftime('%Y-%m-%dT%H:%M:%S')))
    GPIO.output(porta, GPIO.HIGH)


def enviar_imagem(url, file, uid):
    # print('Imagem ' + str(datetime.now().strftime('%Y-%m-%dT%H:%M:%S')))
    try:
        myobj = {'uid': uid}
        requests.post(url, files=file, data=myobj, timeout=6)
        # print('Imagem enviada ' + str(datetime.now().strftime('%Y-%m-%dT%H:%M:%S')))
    except requests.exceptions.Timeout:
        print('Error Enviar Imagem')
    except:
        print('Error Enviar Imagem')


def bancoplacas(identificacao_1, direcao_veiculo_1):
    
    try:
        data_local = json.load(open( '{}/placas_{}_{}.json'.format(actual_directory, identificacao_1, direcao_veiculo_1), ))
        placas = data_local['data']
    except:
        placas = []

    return placas

def main(reboot=False):

    i = 0

    if reboot:
        time.sleep(6)
        os.system('nohup python3 {}/camera.py > {}/camera.py.errors &'.format(actual_directory, actual_directory))
        os.system('sudo kill {}'.format(str(pid)))

    if config.get(rtsps[i], 'debug') == 'True':
        start = time.time()

    while True:

        time.sleep(0.2)

        rtsp = rtsps[i]

        if config.get(rtsp, 'debug') == 'True':
            stop = time.time()
            print("The time of the run:", stop - start)
            start = time.time()

        # Camera
        frame = cap[rtsp].read()
        if frame is None:
            cap[rtsp].stop()
            cap[rtsp] = VideoStream(rtsp_link[rtsp]).start()
            continue
        else:
            # Só continuar se o Rele estiver aberto
            if GPIO.input(gpio_pino[rtsp]) == GPIO.HIGH:

                # Detectar Carro
                corte_frame_vertical_superior = None
                corte_frame_vertical_inferior = None
                corte_frame_horizontal_esquerdo = None
                corte_frame_horizontal_direito = None
                if config.get(rtsp, 'corte_frame_vertical_superior') != 'None':
                    corte_frame_vertical_superior = int(config.get(rtsp, 'corte_frame_vertical_superior'))

                if config.get(rtsp, 'corte_frame_vertical_inferior') != 'None':
                    corte_frame_vertical_inferior = int(config.get(rtsp, 'corte_frame_vertical_inferior'))

                if config.get(rtsp, 'corte_frame_horizontal_esquerdo') != 'None':
                    corte_frame_horizontal_esquerdo = int(config.get(rtsp, 'corte_frame_horizontal_esquerdo'))

                if config.get(rtsp, 'corte_frame_horizontal_direito') != 'None':
                    corte_frame_horizontal_direito = int(config.get(rtsp, 'corte_frame_horizontal_direito'))

                frame = frame[corte_frame_vertical_superior:corte_frame_vertical_inferior, corte_frame_horizontal_esquerdo:corte_frame_horizontal_direito]
                imencoded = cv.imencode(".jpg", frame)[1]

                if config.get(rtsp, 'debug') == 'True':
                    print('Enviou: ' + ' ' + str(datetime.now().strftime('%Y-%m-%dT%H:%M:%S')))

                data = ''
                try:
                    file = {'upload': ('plate.jpg', imencoded.tobytes(), 'image/jpeg')}
                    r = requests.post(link_ocr,
                    files=file, timeout=6)
                except requests.exceptions.Timeout:
                    print('Error: json load cloud timeout')
                    #main(True)
                except:
                    print('Error: json load cloud')
                    #main(True)
                else:
                    if r.status_code == 200:
                        try:
                            data = json.loads(r.text)
                        except:
                            data = ''
                    else:
                        print('Error: json load cloud internet 200')
                        #main(True)
                if data != '':
                    for key in data['results']:
                        if key['vehicle']['score'] > 0:
                            placa_detectada = key['plate'].upper()

                            if abrir_rele_sem_verificar[rtsp] == 'True':
                                GPIO.output(gpio_pino[rtsp], GPIO.LOW)
                                fechar_portao(segundos_aberto[rtsp], gpio_pino[rtsp], 1)

                                time.sleep(4)

                            horario = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                            placas = bancoplacas(identificacao[rtsp], direcao_veiculo[rtsp])

                            if config.get(rtsp, 'debug') == 'True':
                                print('Processada: ' + data['results'][0]['plate'].upper() + ' ' + str(datetime.now().strftime('%Y-%m-%dT%H:%M:%S')))

                            if placa_detectada in placas:
                                if config.get(rtsp, 'debug') == 'True':
                                    print('Conhecido: ' + placa_detectada + ' ' + str(datetime.now().strftime('%Y-%m-%dT%H:%M:%S')))
                                
                                if abrir_rele_sem_verificar[rtsp] != 'True':
                                    GPIO.output(gpio_pino[rtsp], GPIO.LOW)
                                    fechar_portao(segundos_aberto[rtsp], gpio_pino[rtsp], 1)
                                    
                                    time.sleep(4)

                                # Enviar para Acessos
                                payload = {
                                    "FaceMatches": [
                                        {
                                            "Face": {
                                                "Confidence": 100,
                                                "Similarity": 100,
                                                "ExternalImageId": placa_detectada,
                                                "W": 0,
                                                "H": 0
                                            },
                                            'Similarity': 100
                                        }
                                    ]
                                }

                                try:
                                    files = {
                                        'json': (None, json.dumps(payload), 'application/json'),
                                        'file': ('plate.jpg', imencoded.tobytes(), 'image/jpeg')
                                    }

                                    url = "{}/recognition/vehicle/{}/".format(cliente[rtsp], barreira[rtsp])
                                    enviar_imagem(url + direcao_veiculo[rtsp], files, placa_detectada + horario)
                                    #_thread.start_new_thread(enviar_imagem, (url + direcao_veiculo[rtsp], files, placa_detectada + horario))
                                except requests.exceptions.Timeout:
                                    print('Error: Img Original')
                                except:
                                    print('Error: Img Original')
                                # Fim Enviar para Acessos
                    # Camera
                # Camera
        i += 1        
        if(i == len(rtsps)):
            i = 0

main()
