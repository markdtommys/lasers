import argparse
import importlib
import os
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
        if displaymode == 'M':
            displaytextmaxlen = 128
        else:
            displaytextmaxlen = 30
        displaytext = displaytext.upper()
        allowedchars = [' ', ':','[',']','/','.', '!', '?', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                        'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', ',']
        newdisplaytextlist = []
        for character in displaytext:
            if character in allowedchars:
                newdisplaytextlist.append(character)
        displaytextformatted = ''.join(newdisplaytextlist)
        if len(displaytextformatted) > displaytextmaxlen:
            displaytextformatted = displaytextformatted[:displaytextmaxlen]
        modes = {'X':'off','I':'repeat interval','A':'named animation','2':'2line','S':'static', 'M':'marquee', 'F':'merge','P':'presents','H':'horizontalSpin','V':'verticalSpin'}
        animations = ['PLANE','BUILDING','LASERSHOW','COUNTDOWN','CIRCLEINSQUARE']
        if displaymode not in modes.keys():
            return 'invalid display mode selected'
        if displaymode == 'A' and displaytext not in animations:
            return 'invalid animation selected'
        if displaymode != 'I':
            if len(displaysize) < 2:
                displaysizeformatted = '0' + displaysize
            else:
                displaysizeformatted = displaysize
        else:
            displaysizeformatted = ''
        self.command = displaymode + displaysizeformatted + displaytextformatted + '\n'
        self.command = self.command.encode()
        return 'command format OK'

    def get_command(self):
        """
        get the command
        """
        if self.command:
            cmd = self.command
        else:
            cmd = "No command generated"
        return cmd

    def send_command(self):
        """
        send the command down the serial interface
        """
        try:
            time.sleep(1)
            self.seriallink.write(self.command)
            return 'sent OK'
        except Exception as error:
            return 'ERROR unable to send the command - ' + str(error)

    def send_cr(self):
        """
        send <CR> down the serial interface
        """
        try:
            time.sleep(1)
            self.seriallink.write("\n")
            return 'sent <CR> OK'
        except Exception as error:
            return 'ERROR unable to send the command - ' + str(error)

    def read_response(self):
        """
        read response from the serial port
        NB Must not block!
        """
        try:
            if self.seriallink.in_waiting > 0 :
                return self.seriallink.readline().decode() 
            else :
                return ""
        except Exception as error:
            return 'ERROR unable to read from the serial interface - ' + str(error)

def list_available_scripts():
        """
        go to the scripts folder and look at its contents
        return a list of all the names of the scripts excluding file extensions
        """
        availablescripts = []
        scriptsdircontents = os.listdir('laserinputs')
        for i in scriptsdircontents:
            if i.endswith('.py') and not i.endswith('.pyc') and i != '__init__.py':
                availablescripts.append(i.rstrip('.py'))
        return availablescripts

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
    parser.add_argument('-b', dest='baudrate', help='set baudrate, if not specified default is 9600 baud', type=int, default=115200)
    parser.add_argument('-d', dest='serialdevice', help='specify serial device, default is auto', default='auto')
    parser.add_argument('-s', dest='displaysize', help='size of the display', default='25')
    parser.add_argument('-m', dest='mode', help='mode to select', default='M')
    group.add_argument('-i', dest='input', help='custom input, must be the name of a script in the inputs folder')
    group.add_argument('-t', dest='displaytext', help='text to display')
    group.add_argument('-in', dest='interval', help='interval between repeats')
    parser.add_argument('-de', action='store_true', dest='debug', help='send 1 command then constantly listen for messages on the serial interface')
    args = parser.parse_args()

    if args.input:
        lasertext = run_custom_display_script(args.input)
    elif args.displaytext:
        lasertext = args.displaytext
    elif args.interval:
        lasertext = args.interval
    else:
        parser.print_help()
        sys.exit(1)

    if args.serialdevice == 'auto':
        try:
            laserPort = '/dev/ttyACM0'
            lc = LaserDisplayController(laserPort, args.baudrate)
        except :
            laserPort = '/dev/ttyACM1'
            lc = LaserDisplayController(laserPort, args.baudrate)
    else:
        lc = LaserDisplayController(args.serialdevice, args.baudrate)
    res = lc.format_command(args.mode, args.displaysize, lasertext)
    print "Format command : " + res
    res = lc.send_command()
    print "Send Command : " + res
    cmd = lc.get_command()
    print("Sending command : " + cmd)
    if args.debug:
        while 1:
            response = lc.read_response()
            if len(response) > 0:
                print(response)
    else:
        response = lc.read_response()
        print(response)

if __name__ == '__main__':
    main()
