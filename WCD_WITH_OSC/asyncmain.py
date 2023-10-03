import asyncio
import json
from winsdk.windows.devices import radios
from bleak import BleakClient, discover, BleakScanner
from time import sleep
import pyvisa as visa
import netgear_class

# from NetsuiteAPI import NetsuiteAPI as ns

visa.ResourceManager('@py')
rm = visa.ResourceManager()
Oscope = rm.open_resource("USB0::0xF4EC::0xEE3a::512D22278::INSTR")
Oscope.timeout = 5000

# mac_address = '70:b8:f6:c4:84:2A'
# mac_address = '10:97:BD:EB:AB:36'
# mac_address = '24:4C:AB:C1:C3:EA'
mac_address = ''
serial_number = ''
failure = 1
current_bms = 0

############## CHANGE THESE DEPENDING ON THE HARDWARE AND FIRMWARE #################################
wcd_fw_version = 'v2.0.0'
wcd_hw_version = 'v2.0.0'

dev_test = False
dev_test_done = False

bms_test = False
bms_test_check = False
bms_value = 1
pf_array = [0, 0, 0, 0, 0, 0, 0, 0]

wifi_setup = False
network_check = False
network_test = False
credential_check = False
credential_test = False
AP_check = False
AP_test = False
status_check = False
status_test = False
ethernet_test = False
ethernet_check = False
status_check_2 = False

while True:
    try:
        ntg = netgear_class.netgear_switch()
        break
    except:
        print("failed connecting to netgear")
        sleep(5)
        pass

updown, status = ntg.retrieve_data(port=3)
print("updown is: " + str(updown) + " status is: " + status)
sleep(3)
ntg.set_port(port=3, status='disable')
sleep(3)

channel1_v = [0, 0, 0, 0, 0, 0, 0, 0]
channel2_v = [0, 0, 0, 0, 0, 0, 0, 0]

board_ver = 0


def scope_setup():
    global Oscope
    global board_ver
    # set up global settings
    Oscope.write("TRig_MoDe AUTO")  # trigger mode auto
    if int(board_ver) == 1:
        Oscope.write("TDIV 1MS")  # set the divisions to 1MS
        Oscope.write("TRDL 20US")  # sets M Pos (trigger delay) to 20 Us
        Oscope.write("C1:TRig_LeVel 4000mV")
        print("here")
    else:
        Oscope.write("TDIV 500US")  # set the divisions to 500us
        Oscope.write("TRDL 3.59MS")  # sets M Pos (trigger delay) to 3.59 ms
        Oscope.write("C1:TRig_LeVel 4000mV")
    Oscope.write("TRSE GLIT, SR, C1, HT, PL, HV, 835NS")  # set trigger to pulse of channel 1, set it to larger than specified pulse and set spec pulse to 835NS

    # set up all settings
    Oscope.write("BWL C1, ON")  # bandwidth limit channel 1
    Oscope.write("BWL C2, ON")  # bandwidth limit channel 2
    Oscope.write("C1:CPL D1M")  # AC current coupling channel 1
    Oscope.write("C2:CPL D1M")  # AC current coupling channel 2
    Oscope.write("C1:FILTS TYPE, LP, UPPLIMIT, 12.5KHz")  # set low pass filter channel 1
    Oscope.write("C2:FILTS TYPE, LP, UPPLIMIT, 12.5KHz")  # set low pass filter channel 1
    Oscope.write("C1:VDIV 2V")  # volts per division channel 1
    Oscope.write("C2:VDIV 2V")  # volts per division channel 1
    Oscope.write("C1:INVS OFF")  # make sure channel 1 isnt inverted
    Oscope.write("C2:INVS OFF")  # make sure channel 2 isnt inverted
    Oscope.write("C1:OFST 0V")  # set the offset to 0 volts channel 1
    Oscope.write("C2:OFST 0V")  # set the offset to 0 volts channel 2

    sleep(3)

    pkpk = Oscope.query("C1:PAVA? PKPK")
    pkmax = Oscope.query("C1:PAVA? MAX")

    print('automatically set the Oscilloscope')

    sleep(4)
    Oscope.write("ARM")

async def bluetooth_power(turn_on):
    all_radios = await radios.Radio.get_radios_async()
    for this_radio in all_radios:
        if this_radio.kind == radios.RadioKind.BLUETOOTH:
            if turn_on:
                result = await this_radio.set_state_async(radios.RadioState.ON)
            else:
                result = await this_radio.set_state_async(radios.RadioState.OFF)

# def upload_to_netsuite(device_id, pf, battery_comm, inverter_comm, overall_wifi_comm, ethernet_comm, serial):
#     global wcd_fw_version
#     global wcd_hw_version
#
# #    ns = NetsuiteAPI()
#
#     if battery_comm:
#         battery_comm = 1
#     else:
#         battery_comm = 2
#
#     if inverter_comm:
#         inverter_comm = 1
#     else:
#         inverter_comm = 2
#
#     if overall_wifi_comm:
#         overall_wifi_comm = 1
#     else:
#         overall_wifi_comm = 2
#
#     if ethernet_comm:
#         ethernet_comm = 1
#     else:
#         ethernet_comm = 2
#
#     # WCD NETSUITE upload
#     payload = {
#         'custrecord_item': 4965,
#         'custrecord_serial_number': device_id,
#         'custrecord_wcd_id': device_id,
#         'custrecord_machine_id': 'AF.Kilo.U1',
#         'custrecord_test_result': pf,
#         'custrecord_wcd_firmware_v': wcd_fw_version,
#         'custrecord_inverter_serial': serial,
#         'custrecord_wcd_hardware_version': wcd_hw_version,
#         'custrecord_comms_with_battery': battery_comm,
#         'custrecord_comms_with_inverter': inverter_comm,
#         'custrecord_comms_with_wifi': overall_wifi_comm,
#         'custrecord_comms_with_ethernet': ethernet_comm
#     }
#     try:
#         res = ns.create_testing_record(payload)
#         print(res)
#         if res['status_code'] != 200:
#             print('XXXX NETSUITE UPLOAD ERROR XXXX\nTrying again in  seconds', end='\n\n')
#             print(res)
#             upload_to_netsuite(device_id, pf, battery_comm, inverter_comm, overall_wifi_comm, ethernet_comm, serial)
#         else:
#             print('Successful WCD Upload for the device: ' + device_id)
#     except:
#         print("NetSuite error!")
#         sleep(5)
#         upload_to_netsuite(device_id, pf, battery_comm, inverter_comm, overall_wifi_comm, ethernet_comm, serial)
#should no longer need, keeping just in case 9/12/23

async def full_test():
    read_UUID = '2d14e53e-aeb7-11ec-b909-0242ac120002'
    write_UUID = 'c2e938b6-ac7e-11ec-b909-0242ac120002'
    global mac_address
    global Oscope, channel1_v, channel2_v
    global serial_number, failure
    global dev_test, dev_test_done
    global bms_test, bms_test_check, bms_value, pf_array, wifi_setup
    global network_check, network_test, credential_check, credential_test
    global AP_check, AP_test, status_check, status_test, board_ver
    global ethernet_test, ethernet_check, ntg, status_check_2

    def encode_package(package):
        encoded_package = json.dumps(package)
        encoded_package = "1/1:" + encoded_package
        encoded_package = bytes(encoded_package, 'utf-8')
        return encoded_package

    def oscope_PKPK_check():
        v1 = 0
        v2 = 0
        v1_2 = 0
        v2_2 = 0
        first_check = True
        i = 0
        while True:
            i += 1
            try:
                channel1 = Oscope.query("C1:PAVA? PKPK")
                channel2 = Oscope.query("C2:PAVA? PKPK")
                value1 = float(channel1[13:17])
                value2 = float(channel2[13:17])

                sign1 = str(channel1[18])
                sign2 = str(channel2[18])
                power1 = float(channel1[19:21])
                power2 = float(channel2[19:21])

                if sign1 == '+':
                    value1 = value1 * (10 ** power1)
                else:
                    value1 = value1 * (10 ** (-1 * power1))
                if sign2 == '+':
                    value2 = value2 * (10 ** power2)
                else:
                    value2 = value2 * (10 ** (-1 * power2))

                print("aftermath" + "  value1: " + str(value1) + "  value2: " + str(value2))

                if first_check:
                    first_check = False
                    v1 = value1
                    v1_2 = value2
                else:
                    if value1 != v1:
                        v2 = value1
                    if value2 != v1_2:
                        v2_2 = value2
                    if v2 != 0 and v2_2 != 0:
                        # sleep(5)
                        return min(v1, v2), min(v1_2, v2_2)
                    if i > 50:
                        # sleep(10)
                        return max(v1, v2), max(v1_2, v2_2)
            except:
                print("failing")
                sleep(10)
                return 0, 0

    def bms_package_form(num):
        bms_package = {
            "type": "set",
            "id": "new_addr",
            "body": {
                "addr": str(num)
            }
        }
        bms_package_encoded = json.dumps(bms_package)
        bms_package_encoded = "1/1:" + bms_package_encoded
        bms_package_encoded = bytes(bms_package_encoded, 'utf-8')
        return bms_package_encoded

    async def defaults_response(number, message):
        global serial_number, failure
        global dev_test, dev_test_done
        global bms_test, bms_test_check, bms_value, pf_array
        global network_check, network_test, credential_check, credential_test
        global AP_check, AP_test, status_check, status_test, board_ver
        global ethernet_test, ethernet_check, ntg, status_check_2
        connecton_status_tries = 0

        message = str(message)
        print(message)
        if dev_test:
            # print("entered dev test")
            try:
                sn_found = message.index('sn')
                serial_number = message[sn_found + 5:sn_found + 17]
                print("good to go")
                print(serial_number)
                dev_test_done = True
                dev_test = False
            except:
                pass
                # print("failed dev check")

        if bms_test:
            # print("entered bms test")
            try:
                was_suc = message.index('succ')
                # print("got the succ")
                bms_test = False
            except:
                pass
                # print("failed bms write")

        if bms_test_check:
            # print("entered bms test check")
            try:
                was_succ = message.index('{"addr')
                bmsaddress = message[was_succ + 9]
                bms_test_check = False
                if bmsaddress == str(bms_value):
                    pf_array[bms_value - 1] = 1
            except:
                pass
                # print("failed bms check")

        if network_check:
            try:
                print("getting available networks")
                ssid_ind = message.index("LionEnergy")
                print("located LionEnergy wifi network")
                network_check = False
                network_test = True
                sleep(2)
            except:
                print("failed LionEnergy network")
                sleep(4)
                pass

        if credential_check:
            try:
                print("setting wifi credentials")
                succ_ind = message.index("succ")
                print("located succ")
                credential_check = False
                credential_test = True
                sleep(2)
            except:
                print("failed to set wifi cred")
                sleep(4)
                pass

        if AP_check:
            try:
                print("connecting to AP")
                succ_ind = message.index("succ")
                print("located succ")
                AP_check = False
                AP_test = True
                sleep(2)
            except:
                print("failed to connect to AP")
                sleep(4)
                pass

        if status_check:
            try:
                print("getting connection status")
                succ_ind = message.index("succ")
                print("located first succ")
                message.replace("succ", "", 1)
                succ_ind = message.index("succ")
                print("located second succ")
                succ_ind = message.index("LionEnergy")
                print("located LionEnergy")
                succ_ind = message.index("wifi")
                print("located wifi")
                status_check = False
                status_test = True
                sleep(2)
            except:
                print("failed to get connection status")
                sleep(4)
                pass

        if ethernet_check:
            try:
                print("getting ethernet status")
                succ_ind = message.index("succ")
                print("located succ")
                ethernet_check = False
                await asyncio.sleep(10)
                print("I have waited")
                #print("it will now fail")
            except:
                print("failed to get ethernet status")
                sleep(4)
                pass

        if status_check_2:
            try:
                print("getting connection status")
                succ_ind = message.index("succ")
                print("located first succ")
                message.replace("succ", "", 1)
                succ_ind = message.index("succ")
                print("located second succ")
                message.index("eth")
                print("located eth")
                status_check_2 = False
                ethernet_test = True
                sleep(2)
            except:
                print("failed to get connection status")
                sleep(4)
                pass

    # get BMS address package
    dev_package = {
        "type": "get",
        "id": "dev"
    }

    # get BMS address package
    bms_get_package = {
        "type": "get",
        "id": "bms_addr"
    }

    # get the available networks
    network_package = {
        "type": "get",
        "id": "net"
    }

    # set the network credentials
    credential_package = {
        "type": "set",
        "id": "wifi",
        "body": {
            "ssid": "LionEnergy",
            "pwd": "K!ttenP0wer"
        }
    }

    # connect to the AP
    AP_package = {
        "type": "act",
        "id": "cn_ap"
    }

    # get the connection status
    status_package = {
        "type": "get",
        "id": "cn_st"
    }

    # get the ethernet status
    ethernet_package = {
        "type": "act",
        "id": "eth_ini"
    }

    bms_get_package_encoded = encode_package(bms_get_package)
    dev_package_encoded = encode_package(dev_package)
    encoded_network_package = encode_package(network_package)
    encoded_credential_package = encode_package(credential_package)
    encoded_AP_package = encode_package(AP_package)
    encoded_status_package = encode_package(status_package)
    encoded_ethernet_package = encode_package(ethernet_package)

    print("Currently going to get device info")
    print("going to try to connect to mac address: " + str(mac_address))
    count = 0
    main_count = 0
    bms_dont_retry = True

    while True:

        attempts = 0

        # print("discovering devices")
        # all_wcm = []
        # async with BleakScanner() as scanner:
        #     devices = await scanner.discover()
        #     for d in devices:
        #         if "sanctuary_" in str(d):
        #             print(d)
        #             all_wcm.append(str(d))
        # if mac_address in all_wcm:
        #     print("found mac address")
        # else:
        #     print("didn't find mac address")
        try:
            print("attempting...")
            async with BleakClient(mac_address) as client:
                print("connected")
                sleep(7)
                await client.start_notify(read_UUID, defaults_response)

                dev_test = True
                while not dev_test_done and count < 5:
                    await client.write_gatt_char(write_UUID, dev_package_encoded)
                    await asyncio.sleep(7)
                    count += 1
                sleep(1)
                count = 0

                if board_ver == 2:
                    while not network_test and count < 5:
                        print("network testing")
                        network_check = True
                        await client.write_gatt_char(write_UUID, encoded_network_package)
                        await asyncio.sleep(7)
                        count += 1
                    sleep(1)
                    count = 0

                    while not credential_test and count < 5:
                        print("credential testing")
                        credential_check = True
                        await client.write_gatt_char(write_UUID, encoded_credential_package)
                        await asyncio.sleep(7)
                        count += 1
                    sleep(1)
                    count = 0

                    while not AP_test and count < 5:
                        print("AP testing")
                        AP_check = True
                        await client.write_gatt_char(write_UUID, encoded_AP_package)
                        await asyncio.sleep(7)
                        count += 1
                    sleep(1)
                    count = 0

                    while not status_test and count < 6:
                        print("status testing")
                        status_check = True
                        await client.write_gatt_char(write_UUID, encoded_status_package)
                        await asyncio.sleep(7)
                        count += 1
                    sleep(1)
                    count = 0

                print(len(pf_array))
                if bms_dont_retry:
                    for x in range(len(pf_array)):
                        bms_test = True
                        bms_value = x + 1
                        write_attempts = 0
                        scope_attempts = 0
                        while True:
                            await client.write_gatt_char(write_UUID, bms_package_form(x + 1))
                            await asyncio.sleep(1)
                            if bms_test == False:
                                bms_test_check = True
                                Oscope.write("ARM")
                                await asyncio.sleep(2)
                                await client.write_gatt_char(write_UUID, bms_get_package_encoded)
                                await asyncio.sleep(5)
                                [ch1, ch2] = oscope_PKPK_check()
                                channel1_v[x] = ch1
                                channel2_v[x] = ch2
                                print("CH1 Vpp: " + str(ch1))
                                print("CH2 Vpp: " + str(ch2))
                                if ch1 < 1.5 or ch2 < 1.5:
                                    if scope_attempts > 3:
                                        pf_array[x] = 0
                                        break
                                    else:
                                        scope_attempts += 1
                                else:
                                    break
                            else:
                                sleep(5)
                                write_attempts += 1
                                if write_attempts > 2:
                                    break
                    bms_dont_retry = False

                if board_ver == 2:
                    print("ethernet testing")
                    updown, status = ntg.retrieve_data(port=3)
                    print("updown is: " + str(updown) + " status is: " + status)
                    sleep(3)
                    ntg.set_port(port=3, status='enable')
                    print("port enabled")
                    sleep(3)
                    updown, status = ntg.retrieve_data(port=3)
                    print("updown is: " + str(updown) + " status is: " + status)
                    sleep(3)
                    while not ethernet_test and count < 5:
                        print("ethernet testing")
                        ethernet_check = True
                        await client.write_gatt_char(write_UUID, encoded_ethernet_package)
                        await asyncio.sleep(7)
                        status_check_2 = True
                        await client.write_gatt_char(write_UUID, encoded_status_package)
                        await asyncio.sleep(7)
                        count += 1
                    count = 0
                    sleep(1)
                    updown, status = ntg.retrieve_data(port=3)
                    print("updown is: " + str(updown) + " status is: " + status)
                    print("look at the lights sleeping")
                    sleep(5)
                    ntg.set_port(port=3, status='disable')
                    sleep(3)

                await client.stop_notify(read_UUID)
                print('ending')
                await bluetooth_power(False)
                sleep(4)
                await bluetooth_power(True)
                sleep(7)
                break
        except:
            print("there was an error during the test, resetting bluetooth and trying again")
            await bluetooth_power(False)
            sleep(4)
            await bluetooth_power(True)
            sleep(6)
            main_count += 1
            print(main_count)
            if main_count > 3:
                break



while True:
    # turn off the ethernet connection to the WCM
    # ntg.retrieve_data(5)
    # sleep(2)
    # ntg.set_port(5, "disable")

    # read from the text file
    current = open("communication.txt")
    current_string = current.read()
    current.close()
    if len(current_string) > 3:
        pf_array = [0, 0, 0, 0, 0, 0, 0, 0]
        channel1_v = [0, 0, 0, 0, 0, 0, 0, 0]
        channel2_v = [0, 0, 0, 0, 0, 0, 0, 0]
        print("starting test")
        print(current_string)
        current = open("communication.txt", "w")
        current.write("0")
        current.close()
        mac_address = current_string[0:17]
        board_ver = int(current_string[18])
        scope_setup()

        print("testing file thinks mac address is: " + mac_address)
        print("testing file thinks board ver is: " + str(board_ver))

        asyncio.run(full_test())

        crazystring = str(mac_address[-2:len(mac_address)])
        a = crazystring
        b = '2'
        sum_of_hex = hex(int(a, 16) - int(b, 16))
        sum_of_hex = str(sum_of_hex)
        sum_of_hex = sum_of_hex[2:4].upper()
        if len(sum_of_hex) == 1:
            sum_of_hex = '0' + sum_of_hex
        print(sum_of_hex)
        crazystring = str(mac_address[-5:len(mac_address) - 3]).upper()
        device_id = 'sanctuary_' + crazystring + sum_of_hex

        print(pf_array)
        print("channel 1 v's" + str(channel1_v))
        print("channel 2 v's" + str(channel2_v))

        if sum(pf_array) == 8:
            battery_com = True
            print("Battery com good")
        else:
            battery_com = False
            print("Battery com bad")

        if serial_number == 'F01228007068':
            inverter_com = True
            print("Inverter com good")
        else:
            inverter_com = False
            print("Inverter com bad")

        if board_ver == 2:
            if (int(network_test) + int(AP_test) + int(credential_test) + int(status_test)) == 4:
                overall_wifi_com = True
                print("Overall wifi com good")
            else:
                overall_wifi_com = False
                print("Overall wifi com bad")

            if ethernet_test:
                ethernet_com = True
                print("Ethernet com good")
            else:
                ethernet_com = False
                print("Ethernet com bad")
        else:
            overall_wifi_com = True
            ethernet_com = True
            print("not a version 2 board")

        if battery_com:
            battery_comm = 1
        else:
            battery_comm = 2

        if inverter_com:
            inverter_comm = 1
        else:
            inverter_comm = 2

        if overall_wifi_com:
            overall_wifi_comm = 1
        else:
            overall_wifi_comm = 2

        if ethernet_com:
            ethernet_comm = 1
        else:
            ethernet_comm = 2

        if battery_com and inverter_com and overall_wifi_com and ethernet_com:

            payload = str(device_id) + '1' + str(battery_comm) + str(inverter_comm) + str(overall_wifi_comm) + str(ethernet_comm) + str(serial_number)
            Netfile = open('Netinfofile.txt', 'w')
            print("adding Netsuite info (",payload,") to txt file")
            Netfile.writelines(payload)
            Netfile.close()
            # print("THE UPLOAD TO NETSUITE IS COMMENTED OUT")

            # tell the gui what the result was
            current = open("communication.txt", "w")
            current.write("1")
            current.close()

            # reset values
            dev_test_done = False
            network_test = False
            credential_test = False
            AP_test = False
            status_test = False
            ethernet_test = False
            battery_com = False
            inverter_com = False
            overall_wifi_com = False
            ethernet_com = False
            serial_number = ''
            device_id = ''
            pf_array = [0, 0, 0, 0, 0, 0, 0, 0]

        else:

            payload = str(device_id) + '2' + str(battery_comm) + str(inverter_comm) + str(overall_wifi_comm) + \
                      str(ethernet_comm) + str(serial_number)
            Netfile = open('Netinfofile.txt', 'w')
            print("adding Netsuite info (", payload, ") to txt file") #print("TESTING FAILED, DID NOT UPLOAD TO NETSUITE")
            Netfile.writelines(payload)
            Netfile.close()

            # tell the GUI what the result was
            current = open("communication.txt", "w")
            current.write("2")
            current.close()

            # reset values
            bms_test_1_done = False
            dev_test_done = False
            network_test = False
            credential_test = False
            AP_test = False
            status_test = False
            ethernet_test = False
            battery_com = False
            inverter_com = False
            overall_wifi_com = False
            ethernet_com = False
            serial_number = ''
            device_id = ''
            pf_array = [0, 0, 0, 0, 0, 0, 0, 0]
        sleep(5)
        print('end')
