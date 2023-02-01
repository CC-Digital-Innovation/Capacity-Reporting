import configparser
import pika
from loguru import logger
import logging
import os, sys
import subprocess
import ssl

#globals
cwd = os.path.dirname(__file__)
configdir=os.path.join(cwd,'config')
configpath=os.path.join(configdir,'config.ini')
config = configparser.ConfigParser()
config.read(configpath)
rabbmquser = config.get('messageq', 'rmquser')
rabbmqpass = config.get('messageq', 'rmqpass')
rabbmqip = config.get('messageq', 'rmqip')
rabbmqport = config.get('messageq', 'rmqport')

#logging initialization functions
@logger.catch
def begin_logs(sysname = None, sysport = None):
    logger.info("-----------------------------------------------------------------------------------")
    logger.info(f"Starting a message queue log")
    logger.info(f"logging locally to mq.log")
    if sysname and sysport:
        logger.info(f"Server logging is on and logging to {sysname}:{sysport}")
    logger.info("-----------------------------------------------------------------------------------")

#Initialize logger and logs, individual log levels for various log locations
@logger.catch
def init_logs():
    logger.remove()
    logger.debug('setting console log')
    logger.add(sys.stderr, colorize=True, level="DEBUG")
    logger.debug('logging to file latest.log')
    logfile = os.path.join(cwd, 'mq.log')
    logger.add(logfile, level='DEBUG')
    if "Logging" in config.sections():
        sysname = config.get('Logging', 'SyslogName')
        sysport = config.get('Logging', 'SyslogPort')
        if sysname and sysport:
            syslog = logging.handlers.SysLogHandler(address =(str(sysname), int(sysport)))
            logger.add(syslog)
            logger.enable("")
            begin_logs(sysname, sysport)
    else:
        begin_logs()


def main():
    init_logs()
    creds = pika.PlainCredentials(rabbmquser, rabbmqpass)
    ssl_options = pika.SSLOptions(ssl.create_default_context())
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbmqip, port=rabbmqport, credentials= creds, ssl_options=ssl_options))
    channel = connection.channel()

    #
    channel.queue_declare(queue=config.get('messageq', 'customer'))

    def callback(ch, method, properties, body):
        bodystr = str(body, 'UTF-8')
        print(f'Message recived: {bodystr}')
        if 'Capacity' in bodystr:
            logger.debug(f'running Capacity Report')
            subprocess.call(['python', 'report.py'], shell=True)


    channel.basic_consume(queue=config.get('messageq', 'customer'), on_message_callback=callback, auto_ack=True)

    logger.debug('Waiting for messages.')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)