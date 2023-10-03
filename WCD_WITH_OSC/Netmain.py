from time import sleep
from NetsuiteAPI import NetsuiteAPI

wcd_fw_version = 'v2.0.0'
wcd_hw_version = 'v2.0.0'

def Check_for_upload():
    while True:
        net_file = open('Netinfofile.txt', 'r')
        message = net_file.read()
        net_file.close()
        print("text string is", message)
        if str(message) != 'waiting':
            upload_to_netsuite(str(message[:35]))
            net_file = open('Netinfofile.txt', 'w')
            net_file.write('waiting')
            net_file.close()
        else:
            print("waiting for a change in the txt file")
            sleep(20)


def upload_to_netsuite(upload):
    global wcd_fw_version
    global wcd_hw_version
    ns = NetsuiteAPI()

    device_id = upload[:14]
    pf = upload[14:15]
    battery_comm = upload[15:16]
    inverter_comm = upload[16:17]
    overall_wifi_comm = upload[17:18]
    ethernet_comm = upload[18:19]
    serial = upload[19:]
    print(device_id,pf, battery_comm,inverter_comm,overall_wifi_comm,ethernet_comm,serial)

    while True:
        if battery_comm:
            battery_comm = 1
        else:
            battery_comm = 2

        if inverter_comm:
            inverter_comm = 1
        else:
            inverter_comm = 2

        if overall_wifi_comm:
            overall_wifi_comm = 1
        else:
            overall_wifi_comm = 2

        if ethernet_comm:
            ethernet_comm = 1
        else:
            ethernet_comm = 2

        # WCD NETSUITE upload
        payload = {
            'custrecord_item': 4965,
            'custrecord_serial_number': device_id,
            'custrecord_wcd_id': device_id,
            'custrecord_machine_id': 'AF.Kilo.U1',
            'custrecord_test_result': pf,
            'custrecord_wcd_firmware_v': wcd_fw_version,
            'custrecord_inverter_serial': serial,
            'custrecord_wcd_hardware_version': wcd_hw_version,
            'custrecord_comms_with_battery': battery_comm,
            'custrecord_comms_with_inverter': inverter_comm,
            'custrecord_comms_with_wifi': overall_wifi_comm,
            'custrecord_comms_with_ethernet': ethernet_comm
        }
        net_file = open('Netinfofile.txt', 'w')
        net_file.write('waiting')
        net_file.close()
        try:
            res = ns.create_testing_record(payload)
            print(res)
            if res:
                break
            if res['status_code'] != 200:
                print('XXXX NETSUITE UPLOAD ERROR XXXX\nTrying again in 5 seconds', end='\n\n')
                print(res)
                sleep(5)
                #upload_to_netsuite(device_id, pf, battery_comm, inverter_comm, overall_wifi_comm, ethernet_comm, serial)
            else:
                print('Successful WCD Upload for the device: ' + device_id)
        except:
            print("NetSuite error!")
            sleep(5)
            #upload_to_netsuite(device_id, pf, battery_comm, inverter_comm, overall_wifi_comm, ethernet_comm, serial)

Check_for_upload()