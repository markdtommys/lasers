import argparse
import importlib
import time
import serial
import sys

import laserinputs

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
        animations = ['PLANE','BIKE','BUILDING']
        if displaymode not in modes.keys():
            return 'invalid display mode selected'
        if displaymode == 'A' and displaytext not in animations:
            return 'invalid animation selected'
        if len(displaysize) < 2:
            displaysizeformatted = '0' + displaysize
        else:
            displaysizeformatted = displaysize
        self.command = displaymode + displaysizeformatted + displaytextformatted + '\n'
        return 'command format OK'

    def send_command(self):
        """
        send the command down the serial interface
        """
        try:
            time.sleep(1)
            self.seriallink.write(self.command.encode())
            return 'sent OK'
        except Exception as error:
            return 'ERROR unable to send the command - ' + str(error)

    def read_response(self):
        """
        read response from the serial port
        """
        try:
            return self.seriallink.readline().decode() 
        except Exception as error:
            return 'ERROR unable to read from the serial interface - ' + str(error)


def run_custom_display_script(scriptname):
    """
    provide a name of a script in the inputs folder excluding the .py extension
    this function will import the module and run the scripts performactions function
    it will return the results of that function as a string
    """
    mod = importlib.import_module('laserinputs.' + scriptname)
    resultstring = mod.performactions()
    return resultstring

def main():
    """
    command line interface to the laser controller.
    run this if script is run directly, i.e NOT IMPORTED
    """
    parser = argparse.ArgumentParser(description='command line app to send commands to the laser projector')
    group = parser.add_mutually_exclusive_group()
    parser.add_argument('-b', dest='baudrate', help='set baudrate, if not specified default is 9600 baud', type=int, default=9600)
    parser.add_argument('-d', dest='serialdevice', help='specify serial device, default is /dev/ttyACM1', default='/dev/ttyACM1')
    parser.add_argument('-s', dest='displaysize', help='size of the display', default='5')
    parser.add_argument('-a', dest='animation', help='animation to select', default='S')
    group.add_argument('-i', dest='input', help='custom input, must be the name of a script in the inputs folder')
    group.add_argument('-t', dest='displaytext', help='text to display')
    parser.add_argument('-de', action='store_true' dest='debug', help='send 1 command then constantly listen for messages on the serial interface')
    args = parser.parse_args()

    if args.input:
        lasertext = run_custom_display_script(args.input)
    elif args.displaytext:
        lasertext = args.displaytext
    else:
        parser.print_help()
        sys.exit(1)
    lc = LaserDisplayController(args.serialdevice, args.baudrate)
    lc.format_command(args.animation, args.displaysize, lasertext)
    lc.send_command()
    if args.debug:
        while 1:
            response = lc.read_response()
            print(response)
    else:
        response = lc.read_response()
        print(response)

if __name__ == '__main__':
    main()
