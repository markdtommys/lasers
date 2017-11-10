from flask import Flask, render_template, request
from laserDriver import LaserDisplayController, list_available_scripts, run_custom_display_script
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import RPi.GPIO as GPIO 
import time
import atexit

app = Flask(__name__)

"""
  try ttyACM0 and ttyACM1 as Arduino seems to be arbitrarily on
  one of these but not always the same one
"""
try:
  laserPort = '/dev/ttyACM0'
  lc = LaserDisplayController(laserPort, 9600)
except Exception as error:
  print "Failed to connect to /dev/ttyACM0 : " + str(error)
  try:
    laserPort = '/dev/ttyACM1'
    lc = LaserDisplayController(laserPort, 9600)
  except Exception as error:
    print "Failed to connect to /dev/ttyACM1 : " + str(error)  

"""
  Configure GPIO in BCM mode and BCM6 as an output
  (This is connected to the Green LED in the power button)
"""
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(6, GPIO.OUT)
"""
  Turn the Green LED on - Indicates Web server is ready
"""
GPIO.output(6, GPIO.LOW)

laserText=""
laserMode="S"
laserSize="25"
laserCmd=""
laserScript=""
laserRepeat=False
laserInterval="1000"
laserResponse="xXx laserResponse xXx"
formatResponse=""
sendResponse=""
stringSent=""
laserServices = list_available_scripts()

def read_laser_function():
    global laserResponse   
    response = lc.read_response()
    if len(response) > 0:
        print "DEBUG read_laser_function : " + response
        laserResponse = response

def repeat_service_call():
    global laserMode,laserSize,laserCmd
    if ( laserRepeat ):
        laserText = run_custom_display_script(laserScript)
        laserCmd = laserMode + laserSize + laserText
        res = lc.format_command(laserMode,laserSize,laserText)
        print "DEBUG repeat_service_call.format : " + res
        res = lc.send_command()
        print "DEBUG repeat_service_call.send : " + res
        
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=read_laser_function,
    trigger=IntervalTrigger(seconds=3),
    id='read_laser_job',
    name='Read laser every three seconds',
    replace_existing=True)
scheduler.add_job(
    func=repeat_service_call,
    trigger=IntervalTrigger(seconds=30),
    id='repeat_service_call_job',
    name='Repeat last service cript every thirty seconds',
    replace_existing=True)

# Shut down the scheduler when exiting the app
@atexit.register
def goodbye():
    scheduler.shutdown()
    print "Switch Laser Off"
    res = lc.format_command('X','25','OFF')
    print "Format response : " + res
    res = lc.send_command()
    print "Send response : " + res
    GPIO.output(6, GPIO.HIGH)
    GPIO.cleanup()

"""
  To run this 
  python laserServer2.py
 
  Now on your PC Browser, enter
  http://raspiteam4:5000

  You should see the Laser Projector Configurator page ...
"""

@app.route('/', methods=['GET', 'POST'])
def form():
    return render_template('lasers.html',laserPort=laserPort,laserServices=laserServices) 

@app.route('/mobile', methods=['GET', 'POST'])
def formMobile():
    return render_template('lasersMobile.html',laserPort=laserPort,laserServices=laserServices) 

@app.route('/laserResponse', methods=['GET']) 
def lastResponse():
    global laserResponse
    return laserResponse

@app.route('/formatResponse', methods=['GET']) 
def fmtResponse():
    global formatResponse
    return formatResponse

@app.route('/sendResponse', methods=['GET']) 
def sndResponse():
    global sendResponse
    return sendResponse

@app.route('/stringSent', methods=['GET']) 
def strResponse():
    global stringSent
    return stringSent

@app.route('/clock', methods=['GET']) 
def clock():
    response = time.strftime("%A, %d. %B %Y %I:%M:%S %p")
    return response

@app.route('/sendToLaser', methods=['GET', 'POST'])
def sendToLaser():
    global laserInterval,laserRepeat,laserScript,laserMode,laserSize,laserCmd,formatResponse,sendResponse,stringSent
    laserText = request.form['msg']
    laserMode = request.form['mode'] 
    laserSize = request.form['size']

    if ( laserMode == 'I' ):
        laserInterval = laserText 
    elif ( laserMode == 'R'):
        laserRepeat=True
        laserMode=request.form['smode']
        laserScript = laserText
        laserText = run_custom_display_script(laserScript)
    else:
        laserRepeat=False

    laserCmd = laserMode + laserSize + laserText
    laserCmd = str(len(laserCmd)) + ":" + laserCmd

    res = lc.format_command(laserMode,laserSize,laserText)
    formatResponse = res
    res = lc.send_command()
    sendResponse = res
    stringSent = lc.get_command()
    return render_template(request.form['responseTemplate'], laserInterval=laserInterval, lastCommand=laserCmd, laserPort=laserPort, laserText=laserText, laserMode=laserMode, laserSize=laserSize, laserServices=laserServices)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)
