import argparse

parser = argparse.ArgumentParser(
    description="audiotimer runs a timer, as long as audio is present on the input microphone."
)

parser.add_argument(
    "-t",
    "--threshold",
    help="optionally set threshold value of microphone. Use to change sensititivy of the timer. Default is 1000",
    type=int,
    default=1000
)

parser.add_argument(
    "-b", 
    "--buffertime", 
    help="optionally set the time the script runs under the threshold, before ending the timer. Defaults to 3 seconds.",
    type=int,
    default=3 
)

# example of a true/false if present flag, that does not take an input.
parser.add_argument(
    "-v",
    "--verbose",
    help="NOT IMPLEMENTED: outputs the time stamp of the timer runningly.",
    action="store_true"
)

# Parse the arguments
args = parser.parse_args()