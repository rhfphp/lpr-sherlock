import requests
import configparser
import pathlib
import sys
import json
import time

actual_directory = str(pathlib.Path(__file__).parent.resolve())
config = configparser.ConfigParser()
config.read_file(open(r'{}/configuracoes.ini'.format(actual_directory)))

chave = config.get('licenca', 'chave')
tipo_de_ocr = config.get('licenca', 'tipo_de_ocr')

cliente_1 = config.get(sys.argv[1], 'cliente')
barreira_1 = config.get(sys.argv[1], 'barreira')
gpio_pino_1 = int(config.get(sys.argv[1], 'gpio_pino'))
segundos_aberto_1 = int(config.get(sys.argv[1], 'segundos_aberto'))
rtsp_link_1 = config.get(sys.argv[1], 'rtsp_link')
direcao_veiculo_1 = config.get(sys.argv[1], 'direcao_veiculo')
abrir_rele_sem_verificar_1 = config.get(sys.argv[1], 'abrir_rele_sem_verificar')
detectar_moto_1 = config.get(sys.argv[1], 'detectar_moto')
identificacao_1 = config.get(sys.argv[1], 'identificacao')

def updateplacas():
    try:
        r = requests.get('{}/recognition/list_plates?hashonly=true&chave={}&equipamento={}&direcao={}'.format(cliente_1, chave, identificacao_1, direcao_veiculo_1), timeout=6)
    except requests.exceptions.Timeout:
        print('Error: Update Plates DB')
        time.sleep(10)
    except:
        print('Error: Update Plates DB')
        time.sleep(10)
    else:

        
            data_nuvem = json.loads(r.text)

            try:
                json.load(open( '{}/placas_{}_{}.json'.format(actual_directory, identificacao_1, direcao_veiculo_1), ))
            except:
                open( '{}/placas_{}_{}.json'.format(actual_directory, identificacao_1, direcao_veiculo_1), 'w').write('{}'.format(json.dumps({
                    "hash": ""})))
            
            data_local = json.load(open( '{}/placas_{}_{}.json'.format(actual_directory, identificacao_1, direcao_veiculo_1), ))

            if data_nuvem['hash'] != data_local['hash']:
                try:
                    r = requests.get('{}/recognition/list_plates?hashonly=false&chave={}&equipamento={}&direcao={}'.format(cliente_1, chave, identificacao_1, direcao_veiculo_1), timeout=6)
                except requests.exceptions.Timeout:
                    print('Error list_plates')
                else:
                    if r.status_code == 200:
                        json_vals = json.loads(r.text)

                        placas = []
                        for placa in json_vals['data']:   
                            placas.append(placa['placa'])

                        open( '{}/placas_{}_{}.json'.format(actual_directory, identificacao_1, direcao_veiculo_1), 'w+').write(
                            json.dumps(
                                {
                                    "hash": json_vals['hash'],
                                    "data": placas
                                }
                            )
                        )

while True:
    updateplacas()
    time.sleep(2)