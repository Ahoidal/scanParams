#!/usr/bin/env python
from __future__ import division
import argparse
from psychopy import visual,core,event
import os
import sys
import serial

#PARSE INPUTS
#instead we could use gui.Dlg from psychopy to launch a prompt that takes user input and saves it in an object
parser = argparse.ArgumentParser(description='This script runs a block design finger tapping experiment. It presents 6 experimental blocks (3 right and 3 left) in ABBABA order. Blocks are 8s in length with 15s of fixation in between. By default will start when receiving a scanner trigger, but can be run in testing mode using the space bar to trigger with the --test flag.')
parser.add_argument('--fileName', help='Name of outputted data file. Make sure to include file extension.',required=True)
parser.add_argument('--test',action='store_true',default=False,help="Indicate whether we're testing and should expect scanner triggers. Otherwise start experiment with spacebar.")
args = parser.parse_args()

if '.' not in args.fileName:
    parser.error('No file extension provided!')
else:
    fName = args.fileName

#SET EXPERIMENT GLOBALS
base_dir='/Users/antoniahoidal/Desktop/Cosan/Projects/test_scan_params/Data/'
textColor = 'white'
textFont = 'Arial'
textHeight = .5
testWinSize = (640,480)
expWinSize = (1280, 1024)
testTrigger = 'space'
expTrigger = 'k'
fix_time = 15.0
tap_time = 8.0

#SETUP DATAFILE
if not os.path.exists(base_dir):
    os.mkdir(base_dir)

#Make sure we don't overwrite a file
fPath = os.path.join(base_dir,fName)
if os.path.exists(fPath):
    response = ''
    while response != 'y' and response != 'n':
        response = raw_input("File name already exists. Are you sure you want to overwrite? (y) or (n) ")
    if response == 'n':
        print "Goodbye!\n"
        sys.exit()
    elif response == 'y':
        data_file= open(fPath,'w')
else:
    data_file = open(fPath,'w')

#SETUP DEVICES
if args.test:
    winSize = testWinSize
    fullScr = False
    screen = 0
else:
    winSize = expWinSize
    fullScr = True
    screen = 1
window = visual.Window(size=winSize, fullscr=fullScr, screen=screen, allowGUI = True, color='black', monitor='testMonitor')

clock = core.Clock()

if args.test:
    validTrigger = testTrigger
else:
    validTrigger = expTrigger
    serial_settings = {
        'mount': '/dev/tty.USA19H142P1.1',
        'baud': 115200,
        'timeout': .0001} 
    ser = serial.Serial(serial_settings['mount'], serial_settings['baud'], timeout = serial_settings['timeout'])
    ser.flushInput() #reset_input_buffer()


#CREATE SCREENS
fixation= visual.TextStim(win=window, name='fixation',
    text='+',
    color= textColor,
    font= textFont,
    height= textHeight)

right= visual.TextStim(win=window, name='right',
    text='R',
    color= textColor,
    font= textFont,
    height= textHeight)

left= visual.TextStim(win=window, name='left',
    text='L',
    color= textColor,
    font= textFont,
    height= textHeight)

wait_stim = visual.TextStim(window,name='waitText',
    text="Waiting for scanner", 
    color= textColor,
    font= textFont)

prezOrder = [right, left, left, right, left, right]

#EXPERIMENT START
trigger = ''
wait_stim.draw()
window.flip()

while trigger != validTrigger:
    if args.test:
        trigger = event.getKeys(keyList=['space'])
        if trigger:
            trigger = trigger[0]
    else:
        trigger = ser.read()

experimentStart = clock.getTime()
timer = core.Clock() #for stimulus presentation timing

#Draw initial fization 
fixation.draw()
window.flip()

timer.add(fix_time)
while timer.getTime()<0:
    pass

#Main loop
for i in prezOrder:
    
    #draw right or left tap and wait
    i.draw()
    window.flip()
    preztime = clock.getTime() - experimentStart
    print preztime

    timer.add(tap_time)
    while timer.getTime()<0:
        pass

    #draw fixation and wait
    fixation.draw()
    window.flip()

    timer.add(fix_time)
    while timer.getTime()<0:
        pass

    #write trial name and presentation time to file
    data_file.write(i.name + '\t' + str(preztime) + '\n')

#CLEANUP
data_file.close()
if not args.test:
    ser.close()
window.close()
core.quit()