from barcode_printer import DymoPrinterAPI
from time import sleep
dymo = DymoPrinterAPI()

def printer_main():
    while True:
        comm_file = open('to_print.txt', 'r')
        message = comm_file.read()
        comm_file.close()
        print(message)
        if str(message) != 'Ready':
            print_the_barcode(str(message[:17]))
            comm_file = open('to_print.txt', 'w')
            comm_file.write('Ready')
            comm_file.close()
        else:
            print("passing")
            sleep(20)

def print_the_barcode(barc):
    global dymo
    dymo.barcode = barc
    dymo._location = ''
    while True:
        print_result = dymo.begin_printjob()
        if print_result:
            break
        else:
            print("waiting for couple seconds and trying again")
            sleep(5)


printer_main()