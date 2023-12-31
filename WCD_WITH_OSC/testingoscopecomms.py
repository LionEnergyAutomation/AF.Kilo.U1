from bleak import BleakClient, BleakScanner
import asyncio

devices = []


async def scan():
    dev = await BleakScanner.discover()
    for i in range(0, len(dev)):
        print("[" + str(i) + "]" + str(dev[i]))
        devices.append(dev[i])


# async def connect(address, loop):
#     async with BleakClient(address, loop=loop) as client:
#         services = await client.get_services()
#         for ser in services:
#             print(ser.uuid)

loop = asyncio.get_event_loop()
loop.run_until_complete(scan())
# index = input('please select device from 0 to ' + str(len(devices)) + ":")
# index = int(index)
# loop.run_until_complete(connect(devices[index].address, loop))