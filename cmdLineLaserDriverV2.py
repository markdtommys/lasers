from laserDriver import LaserDisplayController
import sys

lc = LaserDisplayController('/dev/ttyACM1', 9600)
if sys.argv[1] == 'test':
    testtext = 'Hello World#$%^*! 3133743620745988814896742598672854976058713489572549867204873455'
    lc.format_command('M', "9", testtext)
    lc.send_command()
else:
    lc.format_command(sys.argv[1],sys.argv[2],sys.argv[3])
    lc.send_command()
while True:
    print( lc.read_response() )
