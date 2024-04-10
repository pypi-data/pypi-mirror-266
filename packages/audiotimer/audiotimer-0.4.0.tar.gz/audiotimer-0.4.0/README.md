# Audio timer
Github: https://github.com/ARanch/audiotimer

This small program starts listening for an audio input on the system microphone. When a set audio level threshold is reached, a timer is started. When the audio level is reduced below the threshold, the timer is stopped after a short countdown, and the timespan is logged.

`python -m pip install audiotimer`

install requirements:
`pip install -r requirements.txt`

Note: on Mac OS you need [Portaudio](https://www.portaudio.com/) installed, otherwise you will get the error `ERROR: Failed building wheel for PyAudio`. Install it using:
`brew install portaudio` before installing requirements.


run using: 
`python -m audiotimer`

see -h flag for run-time options.

Eample usage:
Run using a treshold of "50" and a buffertime of 30 seconds:
`python -m audiotimer -t 50 -b 30`

## Use case
The program is intended to be used as a way of testing the battery life of battery powered loudspeakers. Set the speaker to play a pink noise at a certain level, and leave a laptop with the speaker to listen for when it dies out. 
