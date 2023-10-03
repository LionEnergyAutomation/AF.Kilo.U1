from win32com.client import Dispatch
import pathlib
import os


class DymoPrinterAPI:
    def __init__(self):
        self._barcode = None
        self._location = None
        self._barcode_template_path = os.path.dirname(os.path.abspath(__file__)) + r'\mac.label'
        self._copies = 1  # Defaults to printing a single copy
        self.printer_com = Dispatch('Dymo.DymoAddIn')
        self.printer_label = Dispatch('Dymo.DymoLabels')

    # Locate online printer
    def locatePrinter(self):
        tempName = self.printer_com.GetDymoPrinters()
        self.numPrinters = tempName.count('|') + 1
        counter = 1
        holderPrint = ''
        self.findPrinter = False
        while counter <= self.numPrinters:
            if not counter == self.numPrinters:
                index = tempName.index('|')
                currentprint = tempName[:index]
                tempName = tempName.replace(tempName[:index] + '|', '')
            else:
                currentprint = tempName
            tempHold = self.printer_com.IsPrinterOnline(currentprint)
            if tempHold:
                holderPrint = currentprint
                print("found online printer:")
                print(holderPrint)
            counter += 1
        if not holderPrint == '':
            self._printer_name = holderPrint
            return True
        else:
            print("NO PRINTER IS ONLINE, PLEASE PLUG IN PRINTER")
            return False
        return

    @property
    def copies(self):
        return self._copies

    @copies.setter
    def copies(self, num_copies):
        self._copies = num_copies

    @property
    def barcode(self):
        return self._barcode

    @barcode.setter
    def barcode(self, new_code):
        self._barcode = new_code

    @property
    def printer_name(self):
        return self._printer_name

    @printer_name.setter
    def printer_name(self, new_name):
        self._printer_name = new_name

    @property
    def template_path(self):
        return self._barcode_template_path

    @template_path.setter
    def template_path(self, new_path):
        self._barcode_template_path = new_path

    def _open_label_template(self):
        self.printer_com.Open(self._barcode_template_path)

    def _connect_printer(self):
        self.printer_com.SelectPrinter(self._printer_name)

    def _barcode_to_template(self):
        self.printer_label.SetField('Barcode', self.barcode)

    def _location_to_template(self):
        self.printer_label.SetField('Text', self._location)

    def get_all_printers(self):
        return self.printer_com.GetDymoPrinters()

    def begin_printjob(self):
        locate_result = self.locatePrinter()
        print(locate_result)
        print(self.barcode)
        if self.barcode and locate_result:
            try:
                self._connect_printer()
                self._open_label_template()
                self._barcode_to_template()
                self._location_to_template()
                self.printer_com.StartPrintJob()
                self.printer_com.Print(self.copies, False)
                self.printer_com.EndPrintJob()
                self._barcode = None
                self._location = None
                return True
            except Exception as e:
                return False
        else:
            return False