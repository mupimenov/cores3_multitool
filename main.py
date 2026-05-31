import sys
import uasyncio as asyncio

import core.hw
import core.ui

sys.path.append('/drv')

async def main():
    try:
        core.hw.init()
        await core.ui.run()
    except Exception as ex:
        print("Exception:", ex)

if __name__=="__main__":
    asyncio.run(main())