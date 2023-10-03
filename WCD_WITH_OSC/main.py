import os
import subprocess
import tkinter as tk
from tkinter import scrolledtext
import serial
import csv
from datetime import date
import serial.tools.list_ports
from NetsuiteAPI import NetsuiteAPI
import time
import asyncio
from bleak import BleakScanner
from bleak import BleakClient
import json

wcd_fw_version = 'V1.0.0'
this_device_id = ''

device_ver = 2

window = tk.Tk()
window.title('WCD Uploader')
window.geometry('450x300')
window.propagate(False)
com_port = 'COM0'
ser = serial

headerFrame = tk.Frame(window)
headerFrame.config(background='yellow')

topFrame = tk.Frame(window)
bottomFrame = tk.Frame(window)

firstFrame = tk.Frame(topFrame)
secondFrame = tk.LabelFrame(topFrame, text='step 1', height=250, width=400)
thirdFrame = tk.LabelFrame(topFrame, text='step 2', height=250, width=400)
fourthFrame = tk.LabelFrame(bottomFrame, text='step 3', height=250, width=400)
fifthFrame = tk.LabelFrame(bottomFrame, text='step 4', height=250, width=400)
sixthFrame = tk.LabelFrame(bottomFrame, text='step 5', height=250, width=400)

headerFrame.pack(side='top')
topFrame.pack()
bottomFrame.pack()
firstFrame.pack(side='left', fill='both')
secondFrame.pack(side='left', fill='both')
thirdFrame.pack(side='left', fill='both')
fourthFrame.pack(side='left')
fifthFrame.pack(side='left')
sixthFrame.pack(side='left')

firstFrame.pack_propagate(False)
secondFrame.pack_propagate(False)
thirdFrame.pack_propagate(False)
fourthFrame.pack_propagate(False)
fifthFrame.pack_propagate(False)
sixthFrame.pack_propagate(False)

greeting = tk.Label()
com_label = tk.Label()
ser_err_label = tk.Label()
status_label = tk.Label()
instr_label = tk.Label()
instr2_label = tk.Label()
upload_label = tk.Label()
success_label = tk.Label()
upload_status = tk.Label()
refresh_label = tk.Label()
rst_button = tk.Button()
upload_button = tk.Button()
open_button = tk.Button()
send_button = tk.Button()
run_button = tk.Button()
erase_button = tk.Button()
starter_label = tk.Label()
starter_label2 = tk.Label()
log = tk.Label()
done_boot_button = tk.Button()
success_boot_label = tk.Label()
done_LED_button = tk.Button()
run_label = tk.Label()
rst_otherButton = tk.Button()
success_frame5 = tk.Label()
com2_label = tk.Label()
com2_entry = tk.Entry()
enter_button = tk.Button()
mac_address = ""
get_button = tk.Button()
rst_label = tk.Label()

def upload_to_netsuite(device_id, pf):
    global wcd_fw_version
    ns = NetsuiteAPI()
    # WCD NETSUITE upload
    payload = {
        'custrecord_item': 4965,
        'custrecord_serial_number': device_id,
        'custrecord_machine_id': 'WCD.1',
        'custrecord_test_result': pf,
        'custrecord_wcd_firmware_v': wcd_fw_version,
        'custrecord_inverter_serial': 'something',
        'custrecord_wcd_hardware_version': 'V1.2.0',
        'custrecord_comms_with_inverter': pf,
        'custrecord_comms_with_battery': pf
    }
    res = ns.create_testing_record(payload)
    if res['status_code'] != 200:
        print('XXXX NETSUITE UPLOAD ERROR XXXX\nTrying again in  seconds', end='\n\n')
        print(res)
        upload_to_netsuite(device_id)
    else:
        print('Successful WCD Upload')


def start():
    global window
    global open_button
    global com_label
    global ser_err_label
    global com2_label
    global com2_entry
    global enter_button
    # Create the initial welcome window
    starter_label = tk.Label(firstFrame, text='\n\n\n\nFollow these 5 steps to', fg='black', font=('Times New Roman', 14))
    starter_label2 = tk.Label(firstFrame, text='upload to the WI-FI board', fg='black', font=('Times New Roman', 14))
    greeting = tk.Label(headerFrame, text='Welcome to the Lion Energy WCD Uploader', fg='black',
                        font=('Times New Roman', 18))
    com_label = tk.Label(secondFrame, text='\nIf there is only one COM,\npress Open to open available COM', fg='black',
                         font=('Times New Roman', 14))
    open_button = tk.Button(secondFrame, text='Open', bg='green', fg='white', command=ser_open)
    com2_label = tk.Label(secondFrame, text='\nTo enter COM manually,\ninput COM below and press Enter', fg='black',
                         font=('Times New Roman', 14))
    com2_entry = tk.Entry(secondFrame)
    enter_button = tk.Button(secondFrame, text='Enter', fg='white', bg='green', command=ser_open2)

    greeting.pack()
    starter_label.pack(padx=0, pady=0)
    starter_label2.pack(padx=0, pady=0)
    com_label.pack(anchor='center')
    open_button.pack(anchor='center')
    com2_label.pack()
    com2_entry.pack()
    enter_button.pack()
    bottomFrame.pack_forget()
    topFrame.pack()
    firstFrame.pack_forget()
    thirdFrame.pack_forget()
    fourthFrame.pack_forget()
    fifthFrame.pack_forget()
    sixthFrame.pack_forget()
    window.mainloop()


def refresh():
    global refresh_label
    global instr_label
    global instr2_label
    global upload_button
    global rst_otherButton
    global com_label
    global ser_err_label
    global rst_label
    global rst_button
    global open_button
    global send_button
    global run_button
    global log
    global upload_status
    global erase_button
    global success_frame5
    global success_boot_label
    global run_label
    global get_button

    rst_label.pack_forget()
    rst_button.pack_forget
    get_button.pack_forget()
    run_label.pack_forget()
    success_boot_label.pack_forget()
    success_frame5.pack_forget()
    rst_otherButton.pack_forget()
    com_label.pack_forget()
    ser_err_label.pack_forget()
    status_label.pack_forget()
    instr_label.pack_forget()
    instr2_label.pack_forget()
    rst_button.pack_forget()
    upload_button.pack_forget()
    open_button.pack_forget()
    send_button.pack_forget()
    run_button.pack_forget()
    log.pack_forget()
    upload_status.pack_forget()
    instr2_label.pack_forget()
    erase_button.pack_forget()
    instr2_label.pack()
    done_boot_button.pack(pady=10)
    thirdFrame.pack()
    bottomFrame.pack_forget()
    topFrame.pack()
    firstFrame.pack_forget()
    secondFrame.pack_forget()
    fourthFrame.pack_forget()
    fifthFrame.pack_forget()
    sixthFrame.pack_forget()


def main():
    # Ensure user has necessary packages installed
    os.system('pip install esptool')
    os.system('pip install --upgrade esptool==v3.3')
    os.system('pip install pyserial')
    start()


# async def run_tk(root, interval=0.1):
#     try:
#         while True:
#             root.update()
#             yield from asyncio.sleep(interval)
#     except tk.TclError as e:
#         if "application has been destroyed" not in e.args[0]:
#             raise


async def reset_bms_addr(bms_addr):
    read_UUID = '2d14e53e-aeb7-11ec-b909-0242ac120002'
    write_UUID = 'c2e938b6-ac7e-11ec-b909-0242ac120002'
    global mac_address

    async def defaults_response(number, message):
        message = str(message)
        print(message)
        try:
            was_fail = message.index('fail')
            print("couldn't reset bms address because there was a fail")
            return
        except:
            pass

    if bms_addr == 1:
        # set BMS address to 1 package
        package = {
            "type": "set",
            "id": "new_addr",
            "body": {
                "addr": "1"
            }
        }
        print("Setting BMS address to 1")
    else:
        # set BMS address to 2 package
        package = {
            "type": "set",
            "id": "new_addr",
            "body": {
                "addr": "2"
            }
        }
        print("Setting BMS address to 2")
    package_encoded = json.dumps(package)
    package_encoded = "1/1:" + package_encoded
    package_encoded = bytes(package_encoded, 'utf-8')
    print("going to try to connect to mac address: " + str(mac_address))
    counter = 0
    if mac_address == '70:b8:f6:c4:84:2A':
        print("yes they are the same")
        mac_address = '70:b8:f6:c4:84:2A'
    else:
        print("no they are different")
    while True:
        try:
            time.sleep(1)
            async with BleakClient(mac_address) as client:
                time.sleep(3)
                print("connected")
                await client.start_notify(read_UUID, defaults_response)
                await client.write_gatt_char(write_UUID, package_encoded)
                await asyncio.sleep(4)
                await client.stop_notify(read_UUID)
                time.sleep(1)
                await client.disconnect()
                # time.sleep(7)
                print("success setting BMS")
                break
        except:
            time.sleep(5)
            print("there was an error setting BMS address, trying again")
            counter += 1
            if counter > 5:
                break
    return


async def get_bms_addr():
    read_UUID = '2d14e53e-aeb7-11ec-b909-0242ac120002'
    write_UUID = 'c2e938b6-ac7e-11ec-b909-0242ac120002'
    global mac_address

    async def bms_response(number, message):
        message = str(message)
        print("the following is the response for getting bms address:")
        print(message)
        try:
            was_fail = message.index('fail')
            print("could't reset bms address because there was a fail")
            await get_bms_addr()
        except:
            pass

    # get BMS address package
    package = {
        "type": "get",
        "id": "bms_addr"
    }
    print("Currently going to GET BMS address")

    package_encoded = json.dumps(package)
    package_encoded = "1/1:" + package_encoded
    package_encoded = bytes(package_encoded, 'utf-8')
    print("going to try to connect to mac address: " + str(mac_address))
    while True:
        try:
            async with BleakClient(mac_address) as client:
                time.sleep(3)
                print("connected")
                await client.start_notify(read_UUID, bms_response)
                await client.write_gatt_char(write_UUID, package_encoded)
                await asyncio.sleep(4)
                await client.stop_notify(read_UUID)
                time.sleep(1)
                await client.disconnect()
                print("success getting BMS address")
                time.sleep(7)
                break
        except:
            print("there was an error getting BMS address, trying again")


async def get_device_info():
    read_UUID = '2d14e53e-aeb7-11ec-b909-0242ac120002'
    write_UUID = 'c2e938b6-ac7e-11ec-b909-0242ac120002'
    global mac_address

    async def defaults_response(number, message):
        message = str(message)
        print("the following is the response for getting device info:")
        print(message)
        try:
            was_fail = message.index('fail')
            print("could not get device info because there was a fail")
            await get_device_info()
        except:
            pass

    # get BMS address package
    package = {
      "type": "get",
      "id": "dev"
    }
    print("Currently going to get device info")

    package_encoded = json.dumps(package)
    package_encoded = "1/1:" + package_encoded
    package_encoded = bytes(package_encoded, 'utf-8')
    print("going to try to connect to mac address: " + str(mac_address))
    while True:
        try:
            async with BleakClient(mac_address) as client:
                print("connected")
                time.sleep(2)
                await client.start_notify(read_UUID, defaults_response)
                await client.write_gatt_char(write_UUID, package_encoded)
                await asyncio.sleep(4)
                await client.stop_notify(read_UUID)
                time.sleep(1)
                await client.disconnect()
                print("success getting device info")
                time.sleep(7)
                break
        except:
            print("there was an error getting device info, trying again")


def run_battery():
    global com_port
    global ser
    global send_button
    global run_label
    global run_button
    global window
    global rst_label
    global rst_button

    run_button.pack_forget()
    run_button.update()
    rst_label.pack_forget()
    rst_label.update()
    rst_button.pack_forget()
    rst_button.update()

    run_label.configure(text="\n\n\n\nTESTING BATTERY COMMUNICATION...\n", fg='blue', font=("Times New Roman", 15))
    run_label.update()

    # write the mac address to the text file
    current = open("communication.txt", "w")
    current.write(mac_address + " " + str(device_ver))
    current.close()
    time.sleep(5)
    # wait for it to finish
    while True:
        # read from text file
        current = open("communication.txt")
        the_result = current.read()
        current.close()
        if (the_result == "2") or (the_result == "1"):
            current = open("communication.txt", "w")
            current.write("0")
            current.close()
            break

    # first_bms = 0
    # second_bms = 0
    # third_bms = 0
    #
    # print("destroying the window")
    # window.destroy()
    # time.sleep(5)
    #
    # asyncio.run(reset_bms_addr(1))
    # ans = True
    # print("entering the if statements")
    # if ans:
    #     first_bms = asyncio.run(get_bms_addr())
    #     ans = asyncio.run(reset_bms_addr(2))
    #     if ans:
    #         second_bms = asyncio.run(get_bms_addr())
    #         ans = asyncio.run(reset_bms_addr(1))
    #         if ans:
    #             third_bms = asyncio.run(get_bms_addr())
    #
    if the_result == '1':
        run_label.configure(text="\nSUCCESS!!", font=("Times New Roman", 18), fg="green")
        rst_label.pack()
        rst_label.update()
        rst_button.pack()
        rst_button.update()
        # upload_to_netsuite(this_device_id, 1)
    else:
        run_label.configure(text="\nFAIL! TRY AGAIN\n", font=("Times New Roman", 15), fg="red")
        # upload_to_netsuite(this_device_id, 2)
        run_button.pack_forget()
        rst_button.pack_forget()
        rst_label.pack_forget()
        run_button = tk.Button(sixthFrame, text='RUN COMMS', bg='green', fg='black', command=run_battery,
                               font=("Times New Roman", 12))
        rst_label = tk.Label(sixthFrame, text="\nRestart WCD upload\n", font=("Times New Roman", 15))
        rst_button = tk.Button(sixthFrame, text='RESTART', bg='red', fg='black', command=refresh,
                               font=("Times New Roman", 12))
        run_label.pack()
        run_button.pack()
        rst_label.pack()
        rst_button.pack()

def done_with_bootreset():
    global instr2_label
    global done_boot_button
    global success_boot_label
    global upload_label
    global upload_button
    global erase_button

    instr2_label.forget()
    done_boot_button.forget()

    success_boot_label = tk.Label(thirdFrame, text='\n\n\nSuccess', font=('Times New Roman', 18))
    upload_label = tk.Label(fourthFrame, text='\n\nPress the Begin Upload button to begin upload\nThe Erase '
                                 'button may be used \nwhen there has been a failed upload', font=('Times New Roman', 13))
    upload_button = tk.Button(fourthFrame, text='Begin Upload', bg='green', fg='white', command=upload_begin)
    erase_button = tk.Button(fourthFrame, text='Erase', bg='yellow', fg='black', command=erase)

    success_boot_label.pack()
    upload_label.pack()
    upload_button.pack(pady=8)
    erase_button.pack(pady=8)
    fourthFrame.pack()
    topFrame.pack_forget()
    bottomFrame.pack()
    firstFrame.pack_forget()
    secondFrame.pack_forget()
    thirdFrame.pack_forget()
    fifthFrame.pack_forget()
    sixthFrame.pack_forget()


def LED_show():
    global run_label
    global get_button
    global rst_button
    global done_LED_button
    global instr_label
    global success_frame5
    global run_button
    global rst_label

    run_label.pack_forget()
    done_LED_button.pack_forget()
    instr_label.pack_forget()

    run_label = tk.Label(sixthFrame, text="\nRun battery communication program\n", font=("Times New Roman", 15))
    run_button = tk.Button(sixthFrame, text='RUN COMMS', bg='green', fg='black', command=run_battery,
                           font=("Times New Roman", 12))
    rst_label = tk.Label(sixthFrame, text="\nRestart WCD upload\n", font=("Times New Roman", 15))
    rst_button = tk.Button(sixthFrame, text='RESTART', bg='red', fg='black', command=refresh,
                           font=("Times New Roman", 12))
    success_frame5 = tk.Label(fifthFrame, text='\n\n\nSuccess', font=('Times New Roman', 18))

    success_frame5.pack()
    run_label.pack()
    run_button.pack()
    rst_label.pack()
    rst_button.pack()
    sixthFrame.pack()
    topFrame.pack_forget()
    bottomFrame.pack()
    firstFrame.pack_forget()
    secondFrame.pack_forget()
    thirdFrame.pack_forget()
    fourthFrame.pack_forget()
    fifthFrame.pack_forget()


def upload_begin():
    global com_port
    global ser
    global upload_button
    global send_button
    global run_button
    global window
    global instr_label
    global rst_button
    global log
    global upload_status
    global upload_label
    global erase_button
    global done_LED_button
    global rst_otherButton
    global mac_address
    global this_device_id
    global device_ver

    upload_label.configure(text="\n\n\n\nFLASHING FIRMWARE...\n", fg='blue', font=("Times New Roman", 15))
    upload_label.update()
    upload_button.pack_forget()
    upload_button.update()
    erase_button.pack_forget()
    erase_button.update()

    ser.close()

    bootloader_path = r'"bootloader_dio_40m.bin" '
    partition_path = r'"partitions.bin" '
    boot_app0_path = r'"boot_app0.bin" '
    if device_ver == 1:
        firmware_path = r'"1.0FIRMWARE\\firmware.bin" '  # THIS IS FOR 1.0 VERSION!!!
    elif device_ver == 2:
        firmware_path = r'"2.0FIRMWARE\\firmware.bin" '  # THIS IS FOR 2.0 VERSION!!!
    print(firmware_path)
    spiffs_path = r'"spiffs.bin"'

    # Build the command string (broken up for ease of modification
    cmd_str = 'esptool --chip esp32 --port ' + com_port + ' --baud 460800 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 40m --flash_size detect '
    cmd_str += r'0x1000 ' + bootloader_path
    cmd_str += r'0x8000 ' + partition_path
    cmd_str += r'0x1e000 ' + boot_app0_path
    cmd_str += r'0x20000 ' + firmware_path
    cmd_str += r'0x9a0000 ' + spiffs_path

    # Run the upload command and log the output
    # process = os.system(cmd_str)
    # print("the result is: " + str(process))

    # instead of os.system
    counter = 0
    process = 1
    while counter < 5 and process != 0:
        process = 1
        result_string = subprocess.run(cmd_str, capture_output=True).stdout
        try:
            # process = 1
            # result_string = subprocess.run(cmd_str, capture_output=True).stdout
            result_string = str(result_string)
            print("This is the result string: " + result_string)
            try:
                this_index = result_string.index('MAC:')
                print(this_index)
                mac_address = result_string[this_index + 5: this_index + 22]
                crazystring = str(mac_address[-2:len(mac_address)])
                a = crazystring
                crazystring = str(mac_address[-5:len(mac_address)])
                crazystring = crazystring.replace(':', '')
                this_device_id = 'sanctuary_' + crazystring
                b = "2"
                # Calculating hexadecimal value using function
                sum_of_hex = hex(int(a, 16) + int(b, 16))
                sum_of_hex = str(sum_of_hex)
                sum_of_hex = sum_of_hex[2:4].upper()
                if len(sum_of_hex) == 1:
                    sum_of_hex = '0' + sum_of_hex
                print(sum_of_hex)
                mac_address = mac_address[0:15] + sum_of_hex
                print('The mac address is: ' + mac_address)
                comm_file = open('to_print.txt', 'w')
                print("printing mac address")
                comm_file.write(mac_address)
                comm_file.close()
                process = 0
            except:
                process = 1
                print('was not able to upload fw to WCD')
        except:
            print('major error occured, trying again')
            counter += 1
            time.sleep(1)
    upload_label.pack_forget()
    upload_label.update()
    if process == 0:
        #upload_to_netsuite(this_device_id)
        log = tk.Label(fourthFrame, font=('Times New Roman', 16), text='\n\n\nSuccess')
        upload_status = tk.Label(fourthFrame, font=('Times New Roman', 12), text='Upload completed')
        instr_label = tk.Label(fifthFrame,
                               text='\n\n\n\n\nPress RESET (red button) and wait for LED on WI-FI board\nthen press the Done button',
                               fg='black')
        done_LED_button = tk.Button(fifthFrame, text='Done', bg='green', fg='white', command=LED_show)

        log.pack()
        upload_status.pack()
        instr_label.pack()
        done_LED_button.pack(pady=10)
        fifthFrame.pack()
        topFrame.pack_forget()
        bottomFrame.pack()
        firstFrame.pack_forget()
        secondFrame.pack_forget()
        thirdFrame.pack_forget()
        fourthFrame.pack_forget()
        sixthFrame.pack_forget()

    else:
        log = tk.Label(fourthFrame, font=('Times New Roman', 16), text='\n\n\nError!')
        log.pack()
        rst_otherButton = tk.Button(fourthFrame, text='RESTART', bg='red', command=refresh)
        rst_otherButton.pack()


def erase():
    global erase_button
    global com_port
    global ser
    global upload_button
    global send_button
    global run_button
    global window
    global instr_label
    global rst_button
    global log
    global upload_status
    global rst_otherButton
    global upload_label

    upload_label.pack_forget()
    upload_button.pack_forget()
    erase_button.pack_forget()

    ser.close()
    cmd_str = 'esptool --chip esp32 --port ' + com_port + ' erase_flash'
    # Run the upload command and log the output to a scrolled text window
    # Run the upload command and log the output
    process2 = os.system(cmd_str)
    print("the result is: " + str(process2))

    if process2 == 0:
        log = tk.Label(fourthFrame, font=('Times New Roman', 16), text='\n\nSuccess')
        upload_status = tk.Label(fourthFrame, font=('Times New Roman', 12), text='Erase completed\nPress RESTART')
        rst_otherButton = tk.Button(fourthFrame, text='RESTART', bg='red', command=refresh)
        log.pack()
        upload_status.pack()
        rst_otherButton.pack()
        fourthFrame.pack()
        topFrame.pack_forget()
        bottomFrame.pack()
        firstFrame.pack_forget()
        secondFrame.pack_forget()
        thirdFrame.pack_forget()
        fifthFrame.pack_forget()
        sixthFrame.pack_forget()

    else:
        log = tk.Label(fourthFrame, font=('Times New Roman', 16), text='\n\n\nError!')
        log.pack()
        rst_otherButton = tk.Button(fourthFrame, text='RESTART', bg='red', command=refresh)
        rst_otherButton.pack()
        fourthFrame.pack()
        topFrame.pack_forget()
        bottomFrame.pack()
        firstFrame.pack_forget()
        secondFrame.pack_forget()
        thirdFrame.pack_forget()
        fifthFrame.pack_forget()
        sixthFrame.pack_forget()


def ser_open2():
    global com_port
    global ser
    global upload_button
    global open_button
    global ser_err_label
    global instr2_label
    global success_label
    global erase_button
    global done_boot_button
    global com2_label
    global com2_entry
    global enter_button

    ser_err_label.pack_forget()

    ser_err_label = tk.Label(secondFrame, text='Failed to Open Serial Port, check ports and Try Again')
    # Get available COM port
    com_port = 'COM' + str(com2_entry.get())
    ser = serial.Serial(com_port, 9600)  # open serial port
    try:
        # ser = serial.Serial(com_port, 9600)  #  open serial port
        print("opened")
    except:
        ser_err_label.forget()
        ser_err_label.pack()
    else:
        ser_err_label.pack_forget()
        open_button.pack_forget()
        com_label.pack_forget()
        com2_label.pack_forget()
        com2_entry.pack_forget()
        enter_button.pack_forget()
        success_label = tk.Label(secondFrame, text='\n\n\nSuccess\n' + com_port + ' chosen', font=('Times New Roman', 16))
        instr2_label = tk.Label(thirdFrame, text='\n\n\n1) Connect new WI-FI board\n'
                                                 '2) Hold BOOT(yellow button) on uploader\n'
                                                 '3) CLICK RESET(red button) ONCE\n'
                                                 '4) Release BOOT (yellow button)\n'
                                                 '5) Press the done button on the screen', fg='black', font=('Times New Roman', 13))
        done_boot_button = tk.Button(thirdFrame, text='Done', bg='green', fg='white', command=done_with_bootreset)
        success_label.pack()
        instr2_label.pack()
        done_boot_button.pack(pady=10)
        thirdFrame.pack()
        bottomFrame.pack_forget()
        topFrame.pack()
        firstFrame.pack_forget()
        secondFrame.pack_forget()
        fourthFrame.pack_forget()
        fifthFrame.pack_forget()
        sixthFrame.pack_forget()

        ser.close()  # Ensure previous serial port is closed in preparation for flashing


def ser_open():
    global com_port
    global ser
    global upload_button
    global open_button
    global ser_err_label
    global instr2_label
    global success_label
    global erase_button
    global done_boot_button
    global com2_label
    global com2_entry
    global enter_button

    ser_err_label.pack_forget()

    ser_err_label = tk.Label(secondFrame, text='Failed to Open Serial Port, check ports and Try Again')
    # Get available COM port
    ports = serial.tools.list_ports.comports()
    counter = 0
    port_status = 1
    if ports:
        for port, desc, hwid in sorted(ports):
            newstring = "{}: {} [{}]".format(port, desc, hwid)
            print(newstring)
            if "USB Serial Port (COM" in desc:
                com_port = newstring[0:4]
                counter += 1
    else:
        port_status = 0
    print("counter is: " + str(counter))
    print("comport is: " + com_port)
    print("port status is: " + str(port_status))
    if port_status == 0 or counter > 1:
        ser_err_label.forget()
        ser_err_label.pack()
    else:
        try:
            ser = serial.Serial(com_port, 9600)  # open serial port
            print("opened the serial port")
        except:
            ser_err_label.forget()
            ser_err_label.pack()
        else:
            ser_err_label.pack_forget()
            open_button.pack_forget()
            com_label.pack_forget()
            com2_label.pack_forget()
            com2_entry.pack_forget()
            enter_button.pack_forget()
            success_label = tk.Label(secondFrame, text='\n\n\nSuccess\n' + com_port + ' chosen', font=('Times New Roman', 16))
            instr2_label = tk.Label(thirdFrame, text='\n\n1) Connect new WI-FI board\n'
                                                     '2) Hold BOOT(yellow button) on uploader\n'
                                                     '3) Click RESET(red button)\n'
                                                     '4) Release both buttons\n'
                                                     '5) Press the done button on the screen', fg='black', font=('Times New Roman', 13))
            done_boot_button = tk.Button(thirdFrame, text='Done', bg='green', fg='white', command=done_with_bootreset)
            success_label.pack()
            instr2_label.pack()
            done_boot_button.pack(pady=10)
            thirdFrame.pack()
            bottomFrame.pack_forget()
            topFrame.pack()
            firstFrame.pack_forget()
            secondFrame.pack_forget()
            fourthFrame.pack_forget()
            fifthFrame.pack_forget()
            sixthFrame.pack_forget()

            ser.close()  # Ensure previous serial port is closed in preparation for flashing


if __name__ == '__main__':
    main()
