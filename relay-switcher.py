import threading
from flask import Flask, request, render_template, redirect, url_for
from mylux import state
import logging
import traceback
from logging.handlers import TimedRotatingFileHandler
#import RPi.GPIO as GPIO
import sys
import socket

logger = logging.getLogger('app_logger')
logger.setLevel(logging.DEBUG)

handler = TimedRotatingFileHandler('app.log', when='midnight', interval=1, backupCount=5, encoding='utf-8')
handler.suffix = '%Y-%m-%d'
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

APP_PORT = 8080

HEATPUMP_HOST = '192.168.1.192'
HEATPUMP_PORT = 8889
HEATPUMP_HOT_WATER_STATE_NUMBER = 1

UPDATE_DELAY_SECS = 5

RELAY_BOARD_IP = '192.168.1.100'
RELAY_BOARD_PORT = 6722
RELAY_NUMBER = '1'
RELAY_OP_CODE_TIMEOUT_SUFFIX = ':' + str(2 * UPDATE_DELAY_SECS)

# RELAY_PIN = 23

relay_opened = False
heatpump_state = 5
state_name = state.get_state_name(heatpump_state)
manual_mode = False

app = Flask(__name__)
timer = None

@app.route('/')
def index():
    return render_template('index.html', relay_opened=relay_opened, state_name=state_name, manual_mode=manual_mode, refresh_rate=UPDATE_DELAY_SECS);

@app.route('/toggle', methods=['POST'])
def toggle():
    global relay_opened, manual_mode, timer

    if 'onoff' in request.form:
        logger.debug('Manual mode')
        relay_opened = not relay_opened
        manual_mode = True
        
        if timer != None:
            logger.debug('Cancelling timer ...')
            if timer.active():
                timer.cancel()
  
        update_relay_state()
    elif 'auto' in request.form:
        logger.debug('Auto mode')
        manual_mode = False
        start_periodic_task()

    return redirect(url_for('index'))

# 1x - on, 2x - off, where x in [1-8]
def switch_relay(op_code):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((RELAY_BOARD_IP, RELAY_BOARD_PORT))
        s.sendall(op_code.encode())

def reload_heatpump_state():
    logger.debug('Reloading heatpump state ...')
    global heatpump_state, state_name, relay_opened
    heatpump_state = state.get_operational_state(HEATPUMP_HOST, HEATPUMP_PORT)
    state_name = state.get_state_name(heatpump_state)
    logger.info(f'Heatpump state reloaded ({heatpump_state} -> {state_name})')

    if not manual_mode:
        # stop circulation while perparing hot water
        if heatpump_state == HEATPUMP_HOT_WATER_STATE_NUMBER:
            logger.debug("Heatpump is preparing hot water")
            relay_opened = True
        else:
            relay_opened = False

def update_relay_state():
    logger.debug('Updating relay state ...')

    # pin_output = int(relay_closed)
    # logger.info(f'Pin{RELAY_PIN}={pin_output}')
    # GPIO.output(RELAY_PIN, pin_output)
    
    if relay_opened:
        op_code = '1' + RELAY_NUMBER
        onoff = 'Opening'

        if RELAY_OP_CODE_TIMEOUT_SUFFIX and not manual_mode:
            op_code += RELAY_OP_CODE_TIMEOUT_SUFFIX
    else:
        op_code = '2' + RELAY_NUMBER
        onoff = 'Closing'

    logger.info(f'{onoff} normally closed circuit (op_code: ' + op_code + ')')
    switch_relay(op_code)

def start_periodic_task():
    global timer

    try:
        reload_heatpump_state()
        update_relay_state()
    except Exception as e:
        logger.error(traceback.format_exc())

    timer = threading.Timer(UPDATE_DELAY_SECS, start_periodic_task).start()

if __name__ == '__main__':
    try:
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(RELAY_PIN, GPIO.OUT)
        # GPIO.output(RELAY_PIN, 0)
        logger.addHandler(handler)
        start_periodic_task()
        app.run(debug=False, host='0.0.0.0', port=APP_PORT)
    except Exception as e:
        logger.error(traceback.format_exc())
    finally:
        # GPIO.cleanup()
        if timer != None and timer.active():
            timer.cancel()
        logger.info('Exited')
