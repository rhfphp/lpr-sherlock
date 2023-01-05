import os
import pathlib
import configparser
import time

actual_directory = str(pathlib.Path(__file__).parent.resolve())

# Load Config Local
config = configparser.ConfigParser()
config.read_file(open(r'{}/configuracoes.ini'.format(actual_directory)))

# Iniciar Camera
os.system('nohup python3 {}/camera.py &'.format(actual_directory))

for rtsp in config.sections():
    for name, value in config.items(rtsp):
        if(name == 'rtsp_link'):
            # Iniciar Único Sync Plate
            os.system('nohup python3 {}/sync.plates.py {} &'.format(actual_directory, rtsp))
            time.sleep(5)

            # Iniciar Aberturas e Fechamentos Remoto
            os.system('nohup python3 {}/abertura_fechamento_remoto.py {} &'.format(actual_directory, rtsp))

            # Monitoramento
            os.system('nohup python3 {}/monitoramento.py {} &'.format(actual_directory, rtsp))