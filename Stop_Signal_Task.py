# Import a bunch of libs
from psychopy import visual, sound, core, event, clock, data, logging, gui
import random
import psychtoolbox as ptb
import os
import numpy as np 
# import pandas as pd
# from datetime import datetime

# Create a gui dialog
exp_info = {
'participant_id':0, 'age':0,
'gender':('male','female','other','prefer not to say')
}
dlg = gui.DlgFromDict(dictionary=exp_info, title='SSRT')
if not dlg.OK:
    core.quit() 

# Directories
set_directory = "/Users/heyodogo/Documents/psychopy tasks/psychopy data/SSRT"
base_dir = os.chdir(set_directory)

# Create window + stimuli
win            =  visual.Window([400, 400], color="white", fullscr = True)
fixation       =  visual.TextStim(win, text="+", color="gray", height = .1)
go_stim_a      =  visual.TextStim(win, text="<<", color="black", height = .5, pos = (0, 0.03))
go_stim_z      =  visual.TextStim(win, text=">>", color="black", height = .5, pos = (0, 0.03))
stop_stim      =  visual.TextStim(win, text="X", color="red", height = .5)
feedback_stim  =  visual.TextStim(win, text="", color="black")

# Sound creation
Beep = sound.Sound('A')

# Create a data handler
participant_id  = exp_info['participant_id']
filename        = f"data/{participant_id}_sst"
this_exp        = data.ExperimentHandler(dataFileName=filename, extraInfo=exp_info)
#logging.LogFile(f"{filename}.log", level=logging.EXP)

# Instructions
def draw_then_waitkeys(x):
    x.draw()
    win.flip()
    event.waitKeys()

# Show instructions
instructions_1 = visual.TextStim(win, text='Press the left key when prompted with the target "<<" and the right key when prompted with ">>". Whenever a red X appears, do not press any key.', color='black')
draw_then_waitkeys(instructions_1)
instructions_2 = visual.TextStim(win, text='Make sure to respond as quickly as possible to the go stimulus, do **not** wait for the stop signal to occur', color='black')
draw_then_waitkeys(instructions_2)
instructions_3 = visual.TextStim(win, text='You will now go through 2 short practice blocks', color='black')
draw_then_waitkeys(instructions_3)

# Functions
def draw_then_wait(x, duration):
    x.draw()
    win.flip()
    core.wait(duration)
    
def three_two_one():
    ready  = visual.TextStim(win, text = 'ready', color = "gray", height = 0.2)
    three  = visual.TextStim(win, text='3', color ="gray", height = 0.2)
    two    = visual.TextStim(win, text='2', color ="gray", height = 0.2)
    one    = visual.TextStim(win, text='1', color ="gray", height = 0.2)
    go     = visual.TextStim(win, text = 'go!', color ="gray", height = 0.3, pos = (0, 0.03))
     
    draw_then_wait(ready, 1)
    draw_then_wait(three, 1)
    draw_then_wait(two, 1)
    draw_then_wait(one, 1)
    draw_then_wait(go, .75)

def block(block_num, num_trials, num_stop_trials):

    # Parameters
    stop_signal_delay             = 0.2   # delay between stimulus presentation and stop signal presentation
    stop_signal_delay_increment   = 0.05  # increments added or subtracted
    # stop_signal_duration          = 0.30  # duration of stop signal
    stimulus_duration             = 1.0   # duration of stimulus
    feedback_duration             = 0.5   # duration of feedback presentation
    fixation_duration             = 0.5   # duration of fixation stimulus
    maximum_stop_signal_delay     = 0.8
    minimum_stop_signal_delay     = 0.1

    np.clip(stop_signal_delay, minimum_stop_signal_delay, maximum_stop_signal_delay)
    
    # Create trials array with go and stop trials + shuffle them
    trials = ["go"] * (num_trials - num_stop_trials) + ["stop"] * num_stop_trials
    random.shuffle(trials)

    # inject uniform conditional probability maybe?
    
    # Initialize reaction time + correct omissions
    rt_list = []
    correct_omissions = 0
    
    for trial_num, trial in enumerate(trials):

        # Select go stimulus
        go_stim = random.choice([go_stim_a, go_stim_z])
        expected_response = "left" if go_stim.text == "<<" else "right"
    
        # Start reaction time clock
        rt_clock = clock.Clock()

        event.clearEvents(eventType = 'keyboard')
        
        # Go stimulus
        draw_then_wait(go_stim, (stop_signal_delay if trial == "stop" else stimulus_duration))
        
        # Stop stimulus (if applicable)
        if trial == "stop":
            stop_stim.draw()
            win.flip()
            nextFlip = win.getFutureFlipTime(clock='ptb')
            
            # Play sound
            Beep.play(when=nextFlip)
            core.wait(stimulus_duration - stop_signal_delay)
    
        # Collect response
        keys = event.getKeys(keyList=["left", "right", "escape"], timeStamped=rt_clock)
    
        # Calculate reaction time
        if keys:
            response_key, rt = keys[0]
        else:
            response_key, rt = None, None

        # Omit negative rt responses
        if rt is not None and rt < 0:
            response_key, rt = None, None

        # Determine accuracy
        if trial == "go":
            accuracy = (response_key == expected_response)
            if rt is not None:
                rt_list.append(rt)
        else:
            accuracy = (response_key is None)
            if response_key is None:
                correct_omissions += 1
        
        # Escape option to abort mid-trial (only for experimenter)
        if "escape" in [key[0] for key in keys]:
            core.quit()
    
        # Provide feedback
        if trial == "go":
            if keys:
                feedback_stim.setText("Correct!" if accuracy else "Incorrect")
            else:
                feedback_stim.setText("No response")
            if rt is not None and rt > .800:
                feedback_stim.setText("Too slow")
        else:
            if keys:
                feedback_stim.setText("Failed to Stop")
                stop_signal_delay -= stop_signal_delay_increment
            else:
                feedback_stim.setText("Stopped Successfully")
                stop_signal_delay += stop_signal_delay_increment
    
        # Draw feedback
        if keys:
            draw_then_wait(feedback_stim, feedback_duration)
        else:
            draw_then_wait(feedback_stim, feedback_duration)

        # Draw fixation
        draw_then_wait(fixation, (fixation_duration)) 
    
        # Store data
        this_exp.addData('block_num', block_num + 1)
        this_exp.addData('trial_num', trial_num + 1)
        this_exp.addData('trial_type', trial)
        this_exp.addData('stimulus', go_stim.text)
        this_exp.addData('expected_response', expected_response)
        this_exp.addData('response_key', response_key)
        this_exp.addData('reaction_time', rt)
        this_exp.addData('accuracy', accuracy)
        this_exp.addData('stop_signal_delay', stop_signal_delay)
        this_exp.nextEntry()
        
    # Calculate the average reaction time for go trials
    if rt_list:
        avg_rt = sum(rt_list) / len(rt_list)
    else:
        avg_rt = float('nan')
    
    # End of block message
    end_message_1 = visual.TextStim(win, text=f"Block {block_num + 1} Complete\nAvg RT: {avg_rt:.2f} s\nCorrect Omissions: {correct_omissions}", color='black')
    end_message_2 = visual.TextStim(win, text =f"Experimenter will now proceed to the next prompt screen", color = 'black')
    
    # Draw end messages #1 and #2
    draw_then_wait(end_message_1, 3)
    draw_then_waitkeys(end_message_2)

# Practice Block #1
for block_num in range(1):
    three_two_one()
    draw_then_wait(fixation, 0.5)  
    block(block_num, 20, 0)
    # block(_, #, _) = number of trials
    # block(_, _, #) = number of stop trials within num_trials
    
    practice_end_message1 = visual.TextStim(win, text=f"Your first practice block is complete!\n\n\nExperimenter will now proceed to the next block!", color='black')
    draw_then_waitkeys(practice_end_message1)

# Practice Block #2
for block_num in range(1):
    three_two_one()
    draw_then_wait(fixation, 0.5) 
    block(block_num, 20, 5)

practice_end_message2 = visual.TextStim(win, text=f"You have now completed your practice blocks!\n\n\nExperimenter will now proceed to the experiment blocks!", color= 'black')
draw_then_waitkeys(practice_end_message2)
    
# Actual Experimental trials    
# number_of_blocks = 5     # number of blocks for experiment section
message3 = visual.TextStim(win, text=f"You will now proceed to the experimental blocks!", color= 'black')
draw_then_waitkeys(message3)

for block_num in range(5):
    three_two_one()
    draw_then_wait(fixation, 0.5) 
    block(block_num, 40, 10)
    # block(_, #, _) = number of trials
    # block(_, _, #) = number of stop trials within num_trials

message4 = visual.TextStim(win, text=f"You have just completed Block {block_num + 1}!", color= 'black')
message5 = visual.TextStim(win, text=f'Experimenter will now proceed to next block.', color='black')
draw_then_waitkeys(message4)
draw_then_waitkeys(message5)
    
# Final end message
final_end_message = visual.TextStim(win, text=f"You're done!\n\n\nThank you for your participation.", color = 'black')
draw_then_wait(final_end_message, 5)

# Save data
this_exp.saveAsWideText(filename + ".csv")
this_exp.saveAsPickle(filename)
logging.flush()

# # Create cleaned version of data
# df = pd.read_csv(filename + ".csv")
# df_clean = df.filter(['block_num', 'trial_num', 'trial_type', 'stimulus', 'expected_response', 'response_key', 'reaction_time', 'accuracy', 'participant_id', 'date'])
# df_clean.to_csv(filename + "_clean.csv", index=False)

# Close the window
win.close()
core.quit()
