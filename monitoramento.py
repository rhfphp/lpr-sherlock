import requests
import time
import pathlib

import base64
import sys
import configparser

actual_directory = str(pathlib.Path(__file__).parent.resolve())
config = configparser.ConfigParser()
config.read_file(open(r'{}/configuracoes.ini'.format(actual_directory)))

config_global = configparser.ConfigParser()
config_global.read_file(open(r'{}/global.ini'.format(actual_directory)))


def monitorar():
    usuario_equipamento = config_global.get('configuracoes', 'usuario_equipamento').encode()
    usuario_equipamento = base64.b64encode(usuario_equipamento).decode()

    senha_equipamento = config_global.get('configuracoes', 'senha_equipamento').encode()
    senha_equipamento = base64.b64encode(senha_equipamento).decode()
    
    try:
        requests.get(url='http://' + config.get(sys.argv[1], 'ip'), timeout=3)
    except:
        try:
            requests.post('https://monitoramento.iasec.com.br/monitor/inserir/?tipo=lpr&cliente={}&status=ok&identificacao={}&direcao={}&ip={}&chave={}&usuario={}&senha={}'
            .format(
                config.get(sys.argv[1], 'cliente'),
                config.get(sys.argv[1], 'identificacao'), 
                config.get(sys.argv[1], 'direcao_veiculo'),
                config.get(sys.argv[1], 'ip'),
                config_global.get('configuracoes', 'chave'),
                usuario_equipamento,
                senha_equipamento
                ), timeout=10
            )
        except Exception as e:
            print('here 1')
            print(e)
            time.sleep(10)
    else:
        try:
            requests.post('https://monitoramento.iasec.com.br/monitor/inserir/?tipo=lpr&cliente={}&status=ok&identificacao={}&direcao={}&ip={}&chave={}&usuario={}&senha={}'
            .format(
                config.get(sys.argv[1], 'cliente'),
                config.get(sys.argv[1], 'identificacao'), 
                config.get(sys.argv[1], 'direcao_veiculo'),
                config.get(sys.argv[1], 'ip'),
                config_global.get('configuracoes', 'chave'),
                usuario_equipamento,
                senha_equipamento
                ), timeout=10
            )
        except Exception as e:
            print('here 2')
            print(e)
            time.sleep(10)

while True:
    monitorar()
    time.sleep(10)
