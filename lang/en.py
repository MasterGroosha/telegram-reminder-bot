# -*- coding: utf-8 -*-

##################
# COMMON STRINGS #
##################
s_common_welcome_text = (
    'Hello! If you want to set a new reminder, user /newalarm command\n'
    'Please note, maximum of 5 reminders at once is supported for now')

s_common_guide_timezone = (
    'Enter your timezone like +x or -x (only integers supported)\n'
    'Warning! Timezone should be set related to GMT+0\n')

s_common_guide_time = ('Enter reminder time. For example:\n\n'
                       '1. 20:00 - Send reminder today at 20:00\n'
                       '2. 15:57 20.12.2016 - Send reminder at 15:57 20.12.2016\n'
                       'Currently supported dates before 31.12.2016 inclusive')

s_common_is_time_correct = ("I recognized date and time as {0!s}\n"
                            "If that's correct, enter note text.\n"
                            "It you think that I'm mistaken, please, enter /cancel and try again")

s_common_timezone_set = 'Timezone set, thank you!'
s_common_cancel = 'Ok. Let\'s start again'
s_common_note_added = 'Note added. You\'ll recieve reminder {0!s}'


#########################
# ERRORS AND EXCEPTIONS #
#########################

s_error_note_too_long = (
    'Note must be under 1000 characters.\nPlease, shorten your note and try again')
s_error_date_in_past = 'You can\'t set date in the past!'
s_error_timezone_not_recognized = 'I can\'t recognize entered timezone, please try again'
s_error_time_not_recognized = 'I can\'t recognize time. Please, try again.'
s_error_timezone_not_set = (
    'You haven\'t set up timezone. Please, set it with /setoffset command and try again')

s_error_maximum_number_of_notes = (
    'You already have 5 reminders. To prevent flooding, you can\'t set more than 5 reminders at once.\n'
    'If you need to set more than five, write to @Notes_Service\n\n'
    'A list of set reminders is updated every 24 hours.')

s_error_could_not_save_note = 'Failed to save note in database. Please, try again'
s_error_after_2017 = 'Could not set date after 01.01.2017'
s_error_incorrect_input = 'Date/time set incorrectly. Please, try again'
s_error_incorrect_date = 'No such date'