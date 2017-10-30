from flask import Flask, render_template, request
from laserDriver import LaserDisplayController
import time
app = Flask(__name__)
lc = LaserDisplayController('/dev/ttyACM1', 9600)
laserText="HELLO"
laserMode="M"
laserSize="25"
laserCmd="M25HELLO"

"""
  To run this you need to use the flask program (not python)

  Tell flask which code to run ...
  export FLASK_APP=laserServer.py

  Run with flask as follows ...
  flask run --host=0.0.0.0

  (0.0.0.0 tells flask to make the app visible on the pi's external network interface)
  
  Now on your PC Browser, enter
  http://raspi1b:5000

  You should see the Laser Projector Configurator page ...
"""

@app.route('/', methods=['GET', 'POST'])
def form():
    msg="Hello World!"
    mode="M"
    size="50"
    return render_template('form.html')

@app.route('/laserResponse', methods=['GET'])
def lastResponse():
    response = lc.read_response()
    return render_template('laserResponse.html',laserResponse=response)

@app.route('/sendToLaser', methods=['GET', 'POST'])
def sendToLaser():
    testtext="Hello world - welcome to the Laser Projector"

    laserText = request.form['msg']
    laserMode = request.form['mode'] 
    laserSize = request.form['size'] 
    laserCmd = laserMode + laserSize + laserText
    lc.format_command(laserMode,laserSize,laserText)
    lc.send_command()
    time.sleep(5)
    response = lc.read_response() 
    return render_template('form.html', lastResponse=response, laserCmd=laserCmd)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)
