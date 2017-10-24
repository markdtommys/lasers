import time
import serial
import sys

class LaserDisplayController(object):
    """
    class to control the laser display via a serial interface
    """

    def __init__(self, comport, baudrate):
        try:
            print 'connecting to serial port - ' + comport
            self.seriallink = serial.Serial(comport, baudrate)
            time.sleep(2)
            print 'connection ready'
        except Exception as error:
            print 'could not connect to the serial port'
            print error

    def format_command(self, displaymode, displaysize, displaytext):
        """
        format the command before it is sent down the serial interface
        """
        displaytextmaxlen = 25
        displaytext = displaytext.upper()
        allowedchars = [' ', '.', '!', '?', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                        'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        newdisplaytextlist = []
        for character in displaytext:
            if character in allowedchars:
                newdisplaytextlist.append(character)
        displaytextformatted = ''.join(newdisplaytextlist)
        if len(displaytextformatted) > displaytextmaxlen:
            print 'text is too long! reduced to under ' + str(displaytextmaxlen) + ' chars'
            displaytextformatted = displaytextformatted[:displaytextmaxlen]
        modes = {'X':'off','A':'named animation','S':'static', 'M':'marquee', 'F':'flash'}
        if displaymode not in modes.keys():
            print 'invalid mode selected'
            print 'valid modes are:'
            for mode in modes:
                print mode + ' = ' + modes[mode]
        animations = ['plane','bicycle','building']
        if len(displaysize) < 2:
            displaysizeformatted = '0' + displaysize
        else:
            displaysizeformatted = displaysize
        
        self.command = displaymode + displaysizeformatted + displaytextformatted + '\n'
        print 'command to send - ' + self.command

    def send_command(self):
        """
        send the command down the serial interface
        """
        time.sleep(1)
        self.seriallink.write(self.command)
        while True:
            print self.seriallink.readline()

lc = LaserDisplayController('/dev/ttyACM0', 9600)
if sys.argv[1] == 'test':
    testtext = 'Hello World#$%^*! 3133743620745988814896742598672854976058713489572549867204873455'
    lc.format_command('M', "9", testtext)
    lc.send_command()
else:
    lc.format_command(sys.argv[1],sys.argv[2],sys.argv[3])
    lc.send_command()

