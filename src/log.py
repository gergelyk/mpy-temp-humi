
def debug(msg, **kwargs):
    print(msg, **kwargs)

def info(msg, **kwargs):
    print(msg, **kwargs)

def error(msg, **kwargs):
    print(msg, **kwargs)

def setup():
    # typically after reset we will see some garbage from the bootloader
    # let's clean the screen and go back to the upper left corner
    print(chr(27) + "[2J", end='')
    print(chr(27) + "[0;0H", end='')
