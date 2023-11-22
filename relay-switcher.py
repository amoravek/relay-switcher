import threading
from flask import Flask, render_template, redirect, url_for
from mylux import state
import logging
import traceback
from logging.handlers import TimedRotatingFileHandler
import RPi.GPIO as GPIO

logger = logging.getLogger('app_logger')
logger.setLevel(logging.DEBUG)

handler = TimedRotatingFileHandler('app.log', when='midnight', interval=1, backupCount=5)
handler.suffix = '%Y-%m-%d'
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

app = Flask(__name__)

HEATPUMP_HOST = '192.168.1.192'
HEATPUMP_PORT = 8889
HEATPUMP_HOT_WATER_STATE_NUMBER = 1

UPDATE_DELAY_SECS = 5

RELAY_PIN = 23

relay_closed = True
heatpump_state = 5
state_name = state.get_state_name(heatpump_state)

@app.route('/')
def index():
    global state_name
    
    return render_template('index.html', relay_closed=relay_closed, state=state_name);

@app.route('/toggle', methods=['POST'])
def toggle():
    global relay_closed
    relay_closed = not relay_closed
    return redirect(url_for('index'))

def update_state():
    global heatpump_state, state_name, relay_closed
    heatpump_state = state.get_operational_state(HEATPUMP_HOST, HEATPUMP_PORT)
    state_name = state.get_state_name(heatpump_state)
    logger.info(f'Heatpump state updated ({heatpump_state} -> {state_name})')

    # stop circulation while perparing hot water
    if heatpump_state == HEATPUMP_HOT_WATER_STATE_NUMBER:
        logger.debug("Heatpump is preparing hot water")
        relay_closed = False
    else:
        relay_closed = True

def update_relay_state():
    pin_output = int(relay_closed)
    logger.info(f'Pin{RELAY_PIN}={pin_output}')
    GPIO.output(RELAY_PIN, pin_output)

def start_periodic_task():
    try:
        update_state()
        update_relay_state()
    except Exception as e:
        logger.error(traceback.format_exc())

    threading.Timer(UPDATE_DELAY_SECS, start_periodic_task).start()

if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        GPIO.setup(RELAY_PIN, GPIO.OUT)
        GPIO.output(RELAY_PIN, 0)
        logger.addHandler(handler)
        start_periodic_task()
        app.run(debug=False, host='0.0.0.0', port=8080)
    except Exception as e:
        logger.error(traceback.format_exc())
    finally:
        GPIO.cleanup()
        logger.info('Exited')
