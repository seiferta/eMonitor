import platform
# win32print


class PrinterDefinition:

    def __init__(self):
        self.type = None

    def printers(self):
        return self

    def printFile(self, filename):
        print "print", filename


class WindowsPrinters(PrinterDefinition):
    """
    define printers for emonitor for windows
    """
    def __init__(self):
        PrinterDefinition.__init__(self)
        self.type = "windows"

    def printFile(self, filename):
        print "Winprint", filename


class LinuxPrinters(PrinterDefinition):
    def __init__(self):
        PrinterDefinition.__init__(self)
        self.type = "linux"

    def printFile(self, filename):
        print "Linuxprint", filename


class ePrinters:
    app = None

    def __init__(self):
        self.printers = None

    def init_app(self, app):
        ePrinters.app = app
        if platform.system() == 'Windows':
            self.printers = WindowsPrinters()
        else:
            self.printers = LinuxPrinters()

    def printFile(self, filename):
        print "print", filename