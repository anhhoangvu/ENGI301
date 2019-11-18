WEARABLE METRONOME
by HOANG VU

Project for PocketBeagle which uses Python to create an interface for an arm-mounted metronome using vibrational motors to create rhythms and interacting with surrounding sound.
Please visit https://www.hackster.io/eric-voigt/instrument-glove-4537b7 for a complete tutorial and build instructions.

IMPLEMENTATION FILES:
wearable_metronome.py -- the main program which runs the wearable metronome
run.sh -- startup script which runs wearable_metronome on reboot

To autoboot run.sh, install these files and then add line to crontab using >> sudo crontab -e
@reboot sleep 30 && sh /var/lib/cloud9/project_01/run.sh > /var/lib/cloud9/project_01/logs/cronlog 2>&1


INSTRUCTIONS FOR USE:
1. Clone this repository in /var/lib/cloud9/ for the PocketBeagle
2. Assemble the metronome and connections to PocketBeagle
3. Run wearable_metronome.py on PocketBeagle, set the tempo through the button and lcd screen.
4. Enjoy the rhythms!
