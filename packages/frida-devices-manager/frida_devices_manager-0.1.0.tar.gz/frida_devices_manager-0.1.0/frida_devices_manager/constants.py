import os

FRIDA_SERVER_PATH = '/data/local/tmp/frida-server'
LOCAL_FRIDA_SERVER_PATH = os.path.join(os.path.dirname(__file__), '/bin/frida_server')
FRIDA_DEVICE_TYPE = 'usb'
AUTOMATIC_LOADING_DEVICE = True

# 在加载时如果env中设置了环境变量FRIDA_SERVER_PATH，那么就会调用set_frida_server_path方法
if 'FRIDA_SERVER_PATH' in os.environ:
    FRIDA_SERVER_PATH = os.environ['FRIDA_SERVER_PATH']

if 'FRIDA_DEVICE_TYPE' in os.environ:
    FRIDA_DEVICE_TYPE = os.environ['FRIDA_DEVICE_TYPE']

if 'LOCAL_FRIDA_SERVER_PATH' in os.environ:
    LOCAL_FRIDA_SERVER_PATH = os.environ['LOCAL_FRIDA_SERVER_PATH']
