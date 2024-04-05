import os
import time
import platform
import pkg_resources
from IPython.core.magic import Magics, magics_class, line_magic
from IPython import get_ipython

from meerkat.api import send_meerkat_notification, get_user_token

module_runtime = int(time.time()*1000)

if not os.environ.get("MEERKAT_TOKEN"):
    try:
        with open(os.path.expanduser("~") + "/.meerkat") as file:
            os.environ["MEERKAT_TOKEN"] = file.read()
    except Exception as e:
        pass

def _play_sound(file_name: str):
    system = platform.system()
    if system == 'Darwin':  # macOS
        os.system(f'afplay {file_name}')
    elif system == 'Linux':
        os.system(f'aplay {file_name}')
    elif system == 'Windows':
        os.system(f'powershell -c "(New-Object Media.SoundPlayer \'{file_name}\').PlaySync();"')
    else:
        print('Unsupported operating system.')

#
# Notification Functions
#
def ping():
    sound_path = pkg_resources.resource_filename('meerkat', 'ping_sounds/default_ping.mp3')
    _play_sound(sound_path)

def email(token=None, message=""):
    if token == None:
        token = os.environ.get("MEERKAT_TOKEN")

    if not token:
        print("No MeerkatIO token found in the environment. Please login or go to https://meerkatio.com to set up your account to enable this feature.")
        return
    
    return send_meerkat_notification("email", token, message)

def sms(token=None, message=""):
    if token == None:
        token = os.environ.get("MEERKAT_TOKEN")

    if not token:
        print("No MeerkatIO token found in the environment. Please login or go to https://meerkatio.com to set up your account to enable this feature.")
        return
    
    return send_meerkat_notification("sms", token, message)

#
# iPython Extension
#

@magics_class
class MeerkatMagics(Magics):
    @line_magic
    def ping(self, line):
        sound_path = pkg_resources.resource_filename('meerkat', 'ping_sounds/default_ping.mp3')
        _play_sound(sound_path)

    @line_magic
    def email(self, line):
        email(line)

    @line_magic
    def sms(self, line):
        sms(line)

try:
    # Register the magics with the notebook
    ip = get_ipython()
    ip.register_magics(MeerkatMagics)
except:
    # not in a notebook
    pass