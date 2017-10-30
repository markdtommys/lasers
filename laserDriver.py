import time
import serial

class LaserDisplayController(object):
    """
    class to control the laser display via a serial interface
    """

    def __init__(self, comport, baudrate):
        self.seriallink = serial.Serial(comport, baudrate)
        time.sleep(2)

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
            displaytextformatted = displaytextformatted[:displaytextmaxlen]
        modes = {'X':'off','A':'named animation','S':'static', 'M':'marquee', 'F':'flash'}
        animations = ['plane','bicycle','building']
        if len(displaysize) < 2:
            displaysizeformatted = '0' + displaysize
        else:
            displaysizeformatted = displaysize
        
        self.command = displaymode + displaysizeformatted + displaytextformatted + '\n'

    def send_command(self):
        """
        send the command down the serial interface
        """
        time.sleep(1)
        self.seriallink.write(self.command.encode())

    def read_response(self):
        """
        read response from the serial port
        """
        if self.seriallink.in_waiting > 0 :
            return self.seriallink.readline().decode() 
        else :
            return ""
