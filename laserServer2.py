from flask import Flask, render_template, request
from laserDriver import LaserDisplayController
import time
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

laserText="HELLO"
laserMode="M"
laserSize="25"
laserCmd="M25HELLO"

"""
  To run this 
  python laserServer2.py
 
  Now on your PC Browser, enter
  http://raspiteam4:5000

  You should see the Laser Projector Configurator page ...
"""

@app.route('/', methods=['GET', 'POST'])
def form():
    return render_template('lasers.html',laserPort=laserPort) 

@app.route('/laserResponse', methods=['GET']) 
def lastResponse():
    response = lc.read_response() 
    return render_template('laserResponse.html',laserResponse=response)

@app.route('/sendToLaser', methods=['GET', 'POST'])
def sendToLaser():
    laserText = request.form['msg']
    laserMode = request.form['mode'] 
    laserSize = request.form['size'] 
    laserCmd = laserMode + laserSize + laserText
    lc.format_command(laserMode,laserSize,laserText)
    lc.send_command()
    return render_template('lasers.html', lastCommand=laserCmd, laserPort=laserPort)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)
