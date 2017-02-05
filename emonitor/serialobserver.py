import logging
import serial
import time
from emonitor.extensions import events
from flask import current_app
from .extensions import scheduler

logger = logging.getLogger(__name__)
connected = False
events.addEvent('incoming_serial_data', handlers=[], parameters=['out.text'])


def handleIncomingData(data):
    timestr = "alarm{}.log".format(time.strftime("%Y%m%d-%H%M%S"))
    fname = "{}{}".format(current_app.config.get('PATH_DATA'), timestr)
    text_file = open(fname, "w")
    text_file.write(data)
    text_file.close()
    logger.debug('Incoming serial alarm message: {}'.format(data))
    events.raiseEvent('incoming_serial_data', text=data)

def readFromPort(ser):
    global connected
    data = ''
    while connected:
        data += ser.read(1)
        if data.endswith('\x03'):
            handleIncomingData(data)
            data =''
        #firstData = ser.read(1);
        #bytesToRead = ser.inWaiting()
        #if bytesToRead > 0:
        #    handleIncomingData(firstData + ser.read(bytesToRead))

    ser.close()


def observeSerialPort(**kwargs):
    global connected
    if 'port' in kwargs:
        port = kwargs['port']
    else:
        return
    
    if 'baudrate' in kwargs:
        baudrate = kwargs['baudrate']
    else:
        return
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=None,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            rtscts=0,
            dsrdtr=0,
            xonxoff=0
        )

        if ser.is_open:
            connected = True
            logger.info(u"Port {} successfully opened".format(port))
            _jobserver = scheduler.add_job(readFromPort,
                                           kwargs={'ser': ser,});
        else:
            logger.info(u"Cannot open port {}".format(port))


    except serial.SerialException as ex:
        logger.error(u"Cannot open port {}: {}".format(port, ex))