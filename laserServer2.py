from flask import Flask, render_template, request
from laserDriver import LaserDisplayController, list_available_scripts, run_custom_display_script
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
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
except :
  laserPort = '/dev/ttyACM1'
  lc = LaserDisplayController(laserPort, 9600)

laserText=""
laserMode=""
laserSize=""
laserCmd=""
laserResponse="xXx Test laserResponse xXx"
laserServices = list_available_scripts()

def read_laser_function():
    global laserResponse   
    response = lc.read_response()
    if len(response) > 0:
        print "DEBUG read_laser_function : " + response
        laserResponse = response

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=read_laser_function,
    trigger=IntervalTrigger(seconds=5),
    id='read_laser_job',
    name='Read laser every five seconds',
    replace_existing=True)

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

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

@app.route('/clock', methods=['GET']) 
def clock():
    response = time.strftime("%A, %d. %B %Y %I:%M:%S %p")
    return response

@app.route('/sendToLaser', methods=['GET', 'POST'])
def sendToLaser():
    laserText = request.form['msg']
    laserMode = request.form['mode'] 
    laserSize = request.form['size'] 
    laserCmd = laserMode + laserSize + laserText
    lc.format_command(laserMode,laserSize,laserText)
    lc.send_command()
    return render_template(request.form['responseTemplate'], lastCommand=laserCmd, laserPort=laserPort, laserText=laserText, laserMode=laserMode, laserSize=laserSize,laserServices=laserServices)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)
