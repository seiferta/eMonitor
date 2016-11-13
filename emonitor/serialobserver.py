import logging
import serial
import re
import datetime
from emonitor.extensions import events
from .extensions import scheduler

logger = logging.getLogger(__name__)
connected = False
events.addEvent('incoming_serial_data', handlers=[], parameters=['out.text'])


def handleIncomingData(data):
    events.raiseEvent('incoming_serial_data', text=data)

    # alarm_fields = dict()
    #
    # alarmmessage = re.search(b'\x02([\s\S]*)\x03', data, re.MULTILINE)
    # if alarmmessage:
    #     logger.info(u"Received valid alarmmessage from serial: {}".format(alarmmessage.groups()))
    #     strippedMessage = alarmmessage.group(1).strip()
    #     stringParts = strippedMessage.split(":")
    #     if len(stringParts) == 2:
    #         logger.info(u"Key: {}".format(stringParts[0]))
    #         alarm_fields['key'] = stringParts[0]
    #         addressParts = stringParts[1].split(",")
    #         if len(addressParts) == 5:
    #             alarm_fields['city'] = addressParts[0]
    #             fullAddressParts = addressParts[1].split(' ')
    #             streetname = fullAddressParts[0]
    #             if len(streetname) == 1:
    #                 alarm_fields['address'] = addressParts[1]
    #             else:
    #                 housenumber = fullAddressParts[1]
    #                 alarm_fields['address'] = streetname
    #                 alarm_fields['streetno'] = housenumber
    #
    #             alarm_fields['address2'] = addressParts[2]
    #             alarm_fields['remark'] = addressParts[4]
    #
    #         else:
    #             logger.error("Invalid message received")
    #     else:
    #         logger.error("Invalid message received")
    # else:
    #     logger.info("Received invalid alarm message from serial")
    #
    # uhrzeit = re.search(b'\x03([\s\S]*)\\r\\n', data, re.MULTILINE | re.DOTALL)
    # if uhrzeit:
    #     logger.info(u"Received valid datetime from serial {}".format(uhrzeit.group(1).strip()))
    #     try:
    #         t = datetime.datetime.strptime(uhrzeit.group(1).strip(), '%d.%m.%Y %H:%M:%S')
    #     except ValueError:
    #         t = datetime.datetime.now()
    #     alarm_fields['time'] = t
    #
    # events.raiseEvent('incoming_serial_data', message=alarm_fields)


def readFromPort(ser):
    global connected
    while not connected:
        connected = True
        while connected:
            firstData = ser.read(1);
            bytesToRead = ser.inWaiting()
            if bytesToRead > 0:
                handleIncomingData(firstData + ser.read(bytesToRead))

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