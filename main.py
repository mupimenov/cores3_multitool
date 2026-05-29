import sys

import core.hw
import core.ui

sys.path.append('/drv')

def main():
    try:
        core.hw.init()
        core.ui.init()
    except Exception as ex:
        print("Exception:", ex)

if __name__=="__main__":
    main()