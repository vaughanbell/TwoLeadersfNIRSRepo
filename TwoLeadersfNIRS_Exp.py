#!/usr/bin/env python

from psychopy import core, visual, event, logging, gui
from psychopy.visual import gamma

import csv
import random
import time

import nidaqmx
from nidaqmx.constants import (
    LineGrouping)

# Define / initialise variables

# Class that defines structure of record that will appear for each trial in trial_data array
class trial:
    def __init__(self, participant_intention, participant_intention_timestamp, participant_intention_rt,
                 opponent_intention, participant_decision, participant_decision_timestamp, participant_decision_rt,
                 opponent_decision, humanness_rating, humanness_rating_timestamp, humanness_rating_rt, bonus):
        self.participant_intention = participant_intention
        self.participant_intention_timestamp = participant_intention_timestamp
        self.participant_intention_rt = participant_intention_rt
        self.opponent_intention = opponent_intention
        self.participant_decision = participant_decision
        self.participant_decision_timestamp = participant_decision_timestamp
        self.participant_decision_rt = participant_decision_rt
        self.opponent_decision = opponent_decision
        self.humanness_rating = humanness_rating
        self.humanness_rating_timestamp = humanness_rating_timestamp
        self.humanness_rating_rt = humanness_rating_rt
        self.bonus = bonus


trial_data = []
round = 1

peace_choice = 0
war_choice = 1
running_bonus = 0.0

platform = "linux"
fnirs_connected = "no"

participant_id = 'twoleaderstest0000'
participant_age = 0
participant_gender = 'X'

#
# Intialise DAQMx hardware
#
def initialise_digital_output_channels():
    task.do_channels.add_do_chan(
        'Dev1/port0/line0:7', name_to_assign_to_lines="firstchan",
        line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)

    task.do_channels.add_do_chan(
        'Dev1/port1/line0:3', name_to_assign_to_lines="secondchan",
        line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)

    task.write([0, 0], auto_start=True)

#
# Start fNIRS recording
#
def start_fNIRS_acquisition():
    # Signal to send to start fNIRS acquisition
    # Start fNIRS acquisition
    task.write([0, 4], auto_start=True)

#
# Send a marker to fNIRS of a particular value
#
def send_DAQMx_marker(firstval):
    task.write([firstval, 1], auto_start=True)

#
# Add trial record to trial_data array
#
def add_trial_data_template():
    trial_data.append(trial(99,  # participant_intention
                            0,  # participant_intention_timestamp
                            0,  # participant_intention_rt
                            99,  # opponent_intention
                            99,  # participant_decision
                            0,  # participant_decision_timestamp
                            0,  # participant_decision_rt
                            99,  # opponent_decision
                            999,  # humanness_rating
                            0,  # humanness_rating_timestamp
                            0,  # humanness_rating_rt
                            0.0)  # bonus
                      )

#
# Variable wait function
#
def variable_wait():
    fixation_cross = visual.TextStim(
        win=win, color='black', colorSpace='rgb',
        pos=(0.0, 0.0), height=0.2,
        wrapWidth=50, alignHoriz='center',
        text='+')

    wait_text = visual.TextStim(
        win=win, color='black', colorSpace='rgb',
        pos=(0.0, 0.2), height=0.05,
        wrapWidth=50, alignHoriz='center',
        text='Waiting for partner sync')

    fixation_cross.draw()
    wait_text.draw()
    win.flip()

    wait_value = random.uniform(2, 6)
    core.wait(wait_value)


#
# Get opponent intention for the round
#
def get_opponent_intention():
    rand_float = random.uniform(0,1)
    if rand_float < 0.5:
        generated_opponent_intention = 0
    elif rand_float >= 0.5:
        generated_opponent_intention = 1
    return generated_opponent_intention


#
# Get opponent decision for the round
#
def get_opponent_decision():
    rand_float = random.uniform(0,1)
    if rand_float < 0.5:
        generated_opponent_decision = 0
    elif rand_float >= 0.5:
        generated_opponent_decision = 1
    return generated_opponent_decision


#
# Get participant details
#
def get_participant_details():
    myDlg = gui.Dlg(title="Participant details")
    myDlg.addField('Participant ID:')
    myDlg.addField('Age:')
    myDlg.addField('Gender:', choices=["Male", "Female", "Other"])
    myDlg.addField('fNIRS connected:', choices=["yes", "no"])
    myDlg.show()  # show dialog and wait for OK or Cancel

    if myDlg.OK:
        global participant_id
        participant_id = myDlg.data[0]
        global participant_age
        participant_age = myDlg.data[1]
        global participant_gender
        participant_gender = myDlg.data[2]
        global fnirs_connected
        fnirs_connected = myDlg.data[3]
        return 1
    else:
        return 0


#
# Looking for online partner function
#
def looking_for_partner():
    partner_message = visual.TextStim(win=win,
                                      text='Looking for partner...',
                                      height=0.1,
                                      color='black', colorSpace='rgb')
    partner_message.draw()
    win.flip()

    # partner_wait = random.randint(30,61)
    # core.wait(partner_wait)
    # core.wait(0.01)


#
# Show start of round instructions
#
def round_instructions():
    round_str = "Round " + str(round)

    round_message = visual.TextStim(
        win=win, color='navy', colorSpace='rgb',
        pos=(0.0, 0.8), height=0.075,
        wrapWidth=None, alignHoriz='center',
        text=round_str)

    intention_message1 = visual.TextStim(
        win=win, color='black', colorSpace='rgb',
        pos=(0.0, 0.6), height=0.05,
        wrapWidth=50, alignHoriz='center',
        text='You and your neighbouring country are at a political crossroads')

    intention_message2 = visual.TextStim(
        win=win, color='black', colorSpace='rgb',
        pos=(0.0, 0.5), height=0.05,
        wrapWidth=50, alignHoriz='center',
        text='You both have the option to declare your intentions')

    intention_message3 = visual.TextStim(
        win=win, color='black', colorSpace='rgb',
        pos=(0.0, 0.4), height=0.05,
        wrapWidth=50, alignHoriz='center',
        text='Whether you want peace or war')

    intention_message4 = visual.TextStim(
        win=win, color='black', colorSpace='rgb',
        pos=(0.0, 0.3), height=0.05,
        wrapWidth=50, alignHoriz='center',
        text='You will have the choice later on to honour your word or not')

    continue_button_ypos = intention_message4.pos[1] - 0.3

    continue_box = visual.Rect(
        win=win, name='continue_box',
        width=(0.2, 0.2)[0], height=(0.2, 0.2)[1],
        pos=(0, continue_button_ypos), ori=0,
        lineWidth=2, lineColor='grey', lineColorSpace='rgb',
        fillColor=[1, 1, 1], fillColorSpace='rgb',
        opacity=1, depth=-1.0, interpolate=True)

    continue_text = visual.TextStim(win=win, name='continue_text',
                                    text='Continue',
                                    font='Arial',
                                    pos=(0, continue_button_ypos), height=0.05, wrapWidth=None, ori=0,
                                    color='grey', colorSpace='rgb', opacity=1,
                                    depth=-2.0)

    round_message.draw()
    intention_message1.draw()
    intention_message2.draw()
    intention_message3.draw()
    intention_message4.draw()
    continue_box.draw()
    continue_text.draw()
    win.flip()

    mouse = event.Mouse(win=win)
    Pressed = False

    while not Pressed:
        if mouse.isPressedIn(continue_box):
            Pressed = True
    win.flip()


#
# Intention declaration stage
#
def intention_declaration():
    intention_text = visual.TextStim(
        win=win, name='intention_text',
        text='I will communicate my intention for',
        font='Arial',
        pos=(0, 0.5), height=0.07, wrapWidth=None, ori=0,
        color='black', colorSpace='rgb', opacity=1,
        depth=-2.0)

    peace_box = visual.Rect(
        win=win, name='peace_box',
        width=(0.3, 0.3)[0], height=(0.3, 0.3)[1],
        ori=0, pos=(-.3, 0),
        lineWidth=2, lineColor='black', lineColorSpace='rgb',
        fillColor=[1, 1, 1], fillColorSpace='rgb',
        opacity=1, depth=-1.0, interpolate=True)

    peace_text = visual.TextStim(win=win, name='peace_text',
                                 text='Peace',
                                 font='Arial',
                                 pos=(-.3, 0), height=0.07, wrapWidth=None, ori=0,
                                 color='black', colorSpace='rgb', opacity=1,
                                 depth=-2.0)

    war_box = visual.Rect(
        win=win, name='war_box',
        width=(0.3, 0.3)[0], height=(0.3, 0.3)[1],
        ori=0, pos=(.3, 0),
        lineWidth=2, lineColor='black', lineColorSpace='rgb',
        fillColor=[1, 1, 1], fillColorSpace='rgb',
        opacity=1, depth=-1.0, interpolate=True)

    war_text = visual.TextStim(win=win, name='war_text',
                               text='War',
                               font='Arial',
                               pos=(.3, 0), height=0.07, wrapWidth=None, ori=0,
                               color='black', colorSpace='rgb', opacity=1,
                               depth=-2.0)

    mouse = event.Mouse(win=win)
    Pressed = False

    if fnirs_connected == "yes":
        send_DAQMx_marker(100)

    intention_text.draw()
    peace_box.draw()
    peace_text.draw()
    war_box.draw()
    war_text.draw()
    win.flip()

    responseTimer = core.Clock()
    while not Pressed:
        if mouse.isPressedIn(peace_box):
            trial_data[round].participant_intention = peace_choice
            Pressed = True
        elif mouse.isPressedIn(war_box):
            trial_data[round].participant_intention = war_choice
            Pressed = True
    trial_data[round].participant_intention_rt = responseTimer.getTime()
    trial_data[round].participant_intention_timestamp = core.getTime()

    win.flip()


#
# Intention exchange stage
#
def intention_exchange():
    opponent_intention_text = visual.TextStim(
        win=win, name='intention_text',
        text='Your opponent intends',
        font='Arial',
        pos=(0, 0.5), height=0.05, wrapWidth=None, ori=0,
        color='black', colorSpace='rgb', opacity=1,
        depth=-2.0)

    your_intention_text = visual.TextStim(
        win=win, name='intention_text',
        text='You intend',
        font='Arial',
        pos=(0, 0.4), height=0.05, wrapWidth=None, ori=0,
        color='black', colorSpace='rgb', opacity=1,
        depth=-2.0)

    next_stage_prompt_text = visual.TextStim(
        win=win, name='intention_text',
        text='Now it is time for you both to make your final move',
        font='Arial',
        pos=(0, 0.2), height=0.05, wrapWidth=None, ori=0,
        color='black', colorSpace='rgb', opacity=1,
        depth=-2.0)

    continue_button_ypos = next_stage_prompt_text.pos[1] - 0.3

    continue_box = visual.Rect(
        win=win, name='continue_box',
        width=(0.2, 0.2)[0], height=(0.2, 0.2)[1],
        pos=(0, continue_button_ypos), ori=0,
        lineWidth=2, lineColor='black', lineColorSpace='rgb',
        fillColor=[1, 1, 1], fillColorSpace='rgb',
        opacity=1, depth=-1.0, interpolate=True)

    continue_text = visual.TextStim(win=win, name='continue_text',
                                    text='Continue',
                                    font='Arial',
                                    pos=(0, continue_button_ypos), height=0.05, wrapWidth=None, ori=0,
                                    color='grey', colorSpace='rgb', opacity=1,
                                    depth=-2.0)

    trial_data[round].opponent_intention = get_opponent_intention()

    if trial_data[round].opponent_intention == peace_choice:
        opponent_intention_text.text = 'Your partner intends to declare PEACE'
    elif trial_data[round].opponent_intention == war_choice:
        opponent_intention_text.text = 'Your partner intends to declare WAR'

    if fnirs_connected == "yes":
        send_DAQMx_marker(200)

    opponent_intention_text.draw()
    win.flip()

    wait_value = random.uniform(2, 6)
    core.wait(wait_value)

    if trial_data[round].participant_intention == peace_choice:
        your_intention_text.text = 'You intend to declare PEACE'
    elif trial_data[round].participant_intention == war_choice:
        your_intention_text.text = 'You intend to declare WAR'

    #    your_intention_text.draw()
    #    next_stage_prompt_text.draw()
    opponent_intention_text.draw()
    continue_box.draw()
    continue_text.draw()
    win.flip()

    Pressed = False
    mouse = event.Mouse(win=win)

    while not Pressed:
        if mouse.isPressedIn(continue_box):
            Pressed = True
    win.flip()


#
# Decision stage
#
def decision_stage():
    decision_text = visual.TextStim(
        win=win, name='intention_text',
        text='I choose',
        font='Arial',
        pos=(0, 0.5), height=0.07, wrapWidth=None, ori=0,
        color='black', colorSpace='rgb', opacity=1,
        depth=-2.0)

    peace_box = visual.Rect(
        win=win, name='peace_box',
        width=(0.3, 0.3)[0], height=(0.3, 0.3)[1],
        ori=0, pos=(-.3, 0),
        lineWidth=2, lineColor='black', lineColorSpace='rgb',
        fillColor=[1, 1, 1], fillColorSpace='rgb',
        opacity=1, depth=-1.0, interpolate=True)

    peace_text = visual.TextStim(win=win, name='peace_text',
                                 text='Peace',
                                 font='Arial',
                                 pos=(-.3, 0), height=0.07, wrapWidth=None, ori=0,
                                 color='black', colorSpace='rgb', opacity=1,
                                 depth=-2.0)

    war_box = visual.Rect(
        win=win, name='war_box',
        width=(0.3, 0.3)[0], height=(0.3, 0.3)[1],
        ori=0, pos=(.3, 0),
        lineWidth=2, lineColor='black', lineColorSpace='rgb',
        fillColor=[1, 1, 1], fillColorSpace='rgb',
        opacity=1, depth=-1.0, interpolate=True)

    war_text = visual.TextStim(win=win, name='war_text',
                               text='War',
                               font='Arial',
                               pos=(.3, 0), height=0.07, wrapWidth=None, ori=0,
                               color='black', colorSpace='rgb', opacity=1,
                               depth=-2.0)

    mouse = event.Mouse(win=win)
    Pressed = False

    if fnirs_connected == "yes":
        send_DAQMx_marker(300)

    decision_text.draw()
    peace_box.draw()
    peace_text.draw()
    war_box.draw()
    war_text.draw()
    win.flip()

    responseTimer = core.Clock()
    while not Pressed:
        if mouse.isPressedIn(peace_box):
            trial_data[round].participant_decision = peace_choice
            Pressed = True
        elif mouse.isPressedIn(war_box):
            trial_data[round].participant_decision = war_choice
            Pressed = True
    trial_data[round].participant_decision_rt = responseTimer.getTime()
    trial_data[round].participant_decision_timestamp = core.monotonicClock.getTime()
    win.flip()


#
# Decision exchange stage
#
def decision_exchange():
    opponent_choice_text = visual.TextStim(
        win=win, name='opponent_choice_text',
        text='Your opponent chose',
        font='Arial',
        pos=(0, 0.5), height=0.05, wrapWidth=None, ori=0,
        color='black', colorSpace='rgb', opacity=1,
        depth=-2.0)

    your_choice_text = visual.TextStim(
        win=win, name='your_choice_text',
        text='You chose',
        font='Arial',
        pos=(0, 0.4), height=0.05, wrapWidth=None, ori=0,
        color='black', colorSpace='rgb', opacity=1,
        depth=-2.0)

    your_bonus_text = visual.TextStim(
        win=win, name='your_bonus_text',
        text='You win',
        font='Arial',
        pos=(0, 0.2), height=0.05, wrapWidth=None, ori=0,
        color='black', colorSpace='rgb', opacity=1,
        depth=-2.0)

    opponent_bonus_text = visual.TextStim(
        win=win, name='opponent_bonus_text',
        text='Your opponent wins',
        font='Arial',
        pos=(0, 0.1), height=0.05, wrapWidth=None, ori=0,
        color='black', colorSpace='rgb', opacity=1,
        depth=-2.0)

    continue_button_ypos = opponent_bonus_text.pos[1] - 0.3

    continue_box = visual.Rect(
        win=win, name='continue_box',
        width=(0.2, 0.2)[0], height=(0.2, 0.2)[1],
        pos=(0, continue_button_ypos), ori=0,
        lineWidth=2, lineColor='black', lineColorSpace='rgb',
        fillColor=[1, 1, 1], fillColorSpace='rgb',
        opacity=1, depth=-1.0, interpolate=True)

    continue_text = visual.TextStim(win=win, name='continue_text',
                                    text='Continue',
                                    font='Arial',
                                    pos=(0, continue_button_ypos), height=0.05, wrapWidth=None, ori=0,
                                    color='grey', colorSpace='rgb', opacity=1,
                                    depth=-2.0)

    trial_data[round].opponent_decision = get_opponent_decision()

    if trial_data[round].opponent_decision == peace_choice:
        opponent_choice_text.text = 'Your partner chose PEACE'
    elif trial_data[round].opponent_decision == war_choice:
        opponent_choice_text.text = 'Your partner chose WAR'

    if fnirs_connected == "yes":
        send_DAQMx_marker(400)

    opponent_choice_text.draw()
    win.flip()

    wait_value = random.uniform(2, 6)
    core.wait(wait_value)

    if trial_data[round].participant_decision == peace_choice:
        your_choice_text.text = 'You chose PEACE'
    elif trial_data[round].participant_decision == war_choice:
        your_choice_text.text = 'You chose WAR'

    # Calculate bonus
    if (trial_data[round].participant_decision == peace_choice) and (
            trial_data[round].opponent_decision == peace_choice):
        trial_data[round].bonus += 0.05
        your_bonus_text.text = "You win 0.05"
        opponent_bonus_text.text = "Your opponent wins 0.05"
    elif (trial_data[round].participant_decision == war_choice) and (trial_data[round].opponent_decision == war_choice):
        trial_data[round].bonus += 0.02
        your_bonus_text.text = "You win 0.02"
        opponent_bonus_text.text = "Your opponent wins 0.02"
    elif (trial_data[round].participant_decision == war_choice) and (
            trial_data[round].opponent_decision == peace_choice):
        trial_data[round].bonus += 0.10
        your_bonus_text.text = "You win 0.10"
        opponent_bonus_text.text = "Your opponent wins 0.0"
    elif (trial_data[round].participant_decision == peace_choice) and (
            trial_data[round].opponent_decision == war_choice):
        trial_data[round].bonus += 0.0
        your_bonus_text.text = "You win 0.0"
        opponent_bonus_text.text = "Your opponent wins 0.10"

    global running_bonus
    running_bonus = running_bonus + trial_data[round].bonus

    if fnirs_connected == "yes":
        send_DAQMx_marker(500)

    your_choice_text.draw()
    opponent_choice_text.draw()
    your_bonus_text.draw()
    # opponent_bonus_text.draw()

    continue_box.draw()
    continue_text.draw()
    win.flip()

    Pressed = False
    mouse = event.Mouse(win=win)

    while not Pressed:
        if mouse.isPressedIn(continue_box):
            Pressed = True
    win.flip()


#
# Show update to bonus
#
def running_bonus_update():
    running_bonus_text = visual.TextStim(
        win=win, name='running_bonus_text',
        text='Your total winnings are ',
        font='Arial',
        pos=(0, 0.5), height=0.05, wrapWidth=None, ori=0,
        color='black', colorSpace='rgb', opacity=1,
        depth=-2.0)

    continue_button_ypos = running_bonus_text.pos[1] - 0.3

    continue_box = visual.Rect(
        win=win, name='continue_box',
        width=(0.2, 0.2)[0], height=(0.2, 0.2)[1],
        pos=(0, continue_button_ypos), ori=0,
        lineWidth=2, lineColor='black', lineColorSpace='rgb',
        fillColor=[1, 1, 1], fillColorSpace='rgb',
        opacity=1, depth=-1.0, interpolate=True)

    continue_text = visual.TextStim(win=win, name='continue_text',
                                    text='Continue',
                                    font='Arial',
                                    pos=(0, continue_button_ypos), height=0.05, wrapWidth=None, ori=0,
                                    color='grey', colorSpace='rgb', opacity=1,
                                    depth=-2.0)

    running_bonus_text.text = 'Your total winnings are ' + str(running_bonus)

    running_bonus_text.draw()

    continue_box.draw()
    continue_text.draw()
    win.flip()

    Pressed = False
    mouse = event.Mouse(win=win)

    while not Pressed:
        if mouse.isPressedIn(continue_box):
            Pressed = True
    win.flip()


#
# Get humanness rating from slider
#

def get_humanness_rating():
    rating_message = visual.TextStim(
        win=win, color='black', colorSpace='rgb',
        pos=(0.0, 0.6), height=0.06,
        wrapWidth=50, alignHoriz='center',
        text='How sure are you that your partner is a computer or a human?')

    ratingScale = visual.RatingScale(
        win, low=-100, high=100,
        marker='triangle', markerStart=0, markerColor='green',
        pos=(0.0, 0.2), size=0.7, stretch=2, scale=None,
        labels=('Computer', 'Human'), acceptPreText='OK',
        textColor='black', lineColor='gray')

    if fnirs_connected == "yes":
        send_DAQMx_marker(600)

    rating_message.draw()
    win.flip()

    wait_value = random.uniform(2, 6)
    core.wait(wait_value)

    while ratingScale.noResponse:
        rating_message.draw()
        ratingScale.draw()
        win.flip()

    trial_data[round].humanness_rating = ratingScale.getRating()
    trial_data[round].humanness_rating_rt = ratingScale.getRT()


#
# Write data file
#
def write_data_file():
    filename_str = participant_id + '.csv'
    f = open(filename_str, 'w')

    f.write('pid, age, gender, winnings, ')

    count = 0
    for i in trial_data:
        if count == 0:
            count += 1
            continue
        f.write('pintent' + str(count) + ', ')
        f.write('pintent_rt' + str(count) + ', ')
        f.write('pintent_time' + str(count) + ', ')
        f.write('oppintent' + str(count) + ', ')
        f.write('pdec' + str(count) + ', ')
        f.write('pdec_rt' + str(count) + ', ')
        f.write('pdec_time' + str(count) + ', ')
        f.write('oppdec' + str(count) + ', ')
        f.write('phumanness' + str(count) + ', ')
        f.write('phumanness_rt' + str(count) + ', ')
        f.write('phumanness_time' + str(count) + ', ')
        f.write('pbonus' + str(count) + ', ')
        count += 1

    f.write('\r\n')

    f.write(participant_id + ', ')
    f.write(str(participant_age) + ', ')
    f.write(str(participant_gender) + ', ')
    f.write(str(running_bonus) + ', ')

    count = 0
    for i in trial_data:
        if count == 0:
            count += 1
            continue
        f.write(str(trial_data[count].participant_intention) + ', ')
        f.write(str(trial_data[count].participant_intention_rt) + ', ')
        f.write(str(trial_data[count].participant_intention_timestamp) + ', ')
        f.write(str(trial_data[count].opponent_intention) + ', ')
        f.write(str(trial_data[count].participant_decision) + ', ')
        f.write(str(trial_data[count].participant_decision_rt) + ', ')
        f.write(str(trial_data[count].participant_decision_timestamp) + ', ')
        f.write(str(trial_data[count].opponent_decision) + ', ')
        f.write(str(trial_data[count].humanness_rating) + ', ')
        f.write(str(trial_data[count].humanness_rating_rt) + ', ')
        f.write(str(trial_data[count].humanness_rating_timestamp) + ', ')
        f.write(str(trial_data[count].bonus) + ', ')
        count += 1

    f.write('\r\n')
    f.close()

#
# Show 'thanks for participating' screen
#
def experiment_terminated():
    thanks_text = visual.TextStim(
        win=win, color='black', colorSpace='rgb',
        pos=(0.0, 0.2), height=0.07,
        wrapWidth=50, alignHoriz='center',
        text='Thank you for participating')

    thanks_text.draw()
    win.flip()

    core.wait(5)


#################################################
#                                               #
#              Main programme                   #
#                                               #
#################################################

#if get_participant_details() == 0:
#    exit()

# win = visual.Window([1800,1100], monitor = "testMonitor", color=[1,1,1], units="norm")
win = visual.Window([1200, 800], monitor="testMonitor", color=[1, 1, 1], units="norm", winType="pyglet")

logging.console.setLevel(logging.WARNING)
runningLog = logging.LogFile("runningRun.log", level=logging.INFO, filemode='a')

add_trial_data_template()  # Initialise trial array element at pos 0 (not used)

if fnirs_connected == "yes":
    task = nidaqmx.Task()
    initialise_digital_output_channels()
    start_fNIRS_acquisition()

random.seed()

# looking_for_partner()
while round < 21:
    add_trial_data_template()  # Initialise trial array element for this round
    round_instructions()
    variable_wait()
    intention_declaration()
    variable_wait()
    intention_exchange()
    decision_stage()
    variable_wait()
    decision_exchange()
    variable_wait()
    get_humanness_rating()
    write_data_file()
    round += 1

experiment_terminated()
logging.flush()
win.close()
core.quit()

