import time

def time_stamp():
    # Get the current local time
    current_time = time.localtime()

    # Format the time to hour:minute
    timestamp = time.strftime("%H:%M", current_time)
    return timestamp

def get_user_decision(prompt):
    while True:  # This creates an infinite loop
        user_input = input(prompt).lower()  # Convert input to lowercase for consistency
        if user_input == 'y':
            return True
        elif user_input == 'n':
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")

from configparser import ConfigParser
import os
class Configuration:
    def __init__(self):
        # Assuming the config.ini is in the same directory as this script
        # Get the directory of the current file (__file__ is the path to the current script)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to the config.ini file
        self.config_path = os.path.join(current_dir, 'config.ini')
        self.config = ConfigParser()

    def debug(self):
        self.config.read(self.config_path)
        # Debug: Print all sections and options
        for section in self.config.sections():
            print(section, dict(self.config.items(section)))

        # Make sure DEFAULT is included and check its content
        print("DEFAULT", dict(self.config.items('DEFAULT'))) 

    def read_config(self):
        self.config.read(self.config_path)
    
    def save_config(self):
         # Write the changes back to the config file
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

    
    def get_slack_enabled(self):
        self.read_config()
        # Get the SlackEnabled setting from the DEFAULT section
        # Convert it to boolean
        slack_enabled = self.config.getboolean('DEFAULT', 'SlackEnabled')
        
        return slack_enabled
    
    def set_slack_enabled(self, bool):
        self.read_config()
        self.config.set('DEFAULT', 'SlackEnabled', str(bool)
)


