import logging
import serial
from threading import Thread
from emonitor.extensions import events
from .extensions import scheduler

logger = logging.getLogger(__name__)
connected = False
events.addEvent('incoming_serial_data', handlers=[], parameters=['message'])


def handleIncomingData(data):
    events.raiseEvent('incoming_serial_data', message=data)
    logger.info(u"incoming_serial_data: {}{}".format(data))


def readFromPort(ser):
    global connected
    while not connected:
        connected = True

        while True:
           reading = ser.readline().decode()
           handleIncomingData(reading)

    ser.close()


def observeSerialPort(**kwargs):
    
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
            baudrate=baudrate
        )

        if ser.is_open:
            _jobserver = scheduler.add_job(readFromPort,
                                           kwargs={'ser': ser,});
        else:
            logger.info(u"Cannot open port {}".format(port))


    except serial.SerialException as ex:
        logger.error(u"Cannot open port {}: {}".format(port, ex))