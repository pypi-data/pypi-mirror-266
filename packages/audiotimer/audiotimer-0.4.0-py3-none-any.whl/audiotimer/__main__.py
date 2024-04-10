def main():
    import pyaudio
    import numpy as np
    import time
    import math
    from pynput import keyboard
    from slack_ping import Slack



    # TODO: make more elegant? 
    if __name__ == "__main__":
        # import default flag values when run as script
        from flags import args
        from slack_ping import Slack
        from helpers import time_stamp, Configuration
    else:
        # import flag values when run as module
        from .flags import args # . notation ensures import from local package
        from .slack_ping import Slack
        from .helpers import time_stamp, Configuration

    # import message client for Slack.
    slack = Slack() 

    # config = Configuration()
    # Constants
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    THRESHOLD = args.threshold  # Audio level threshold for detecting sound. Defaults to 1000.
    MAX_LEVEL = 32768  # Max level for 16-bit audio
    BUFFER_TIME = args.buffertime  # Buffer time in seconds for countdown
    BAR_LENGTH = 50  # Length of the volume bar
    UPDATE_INTERVAL = 0.1  # Interval for updating the volume bar in seconds
    
    # TODO: add pink noise output.

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open stream for audio input
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("Listening for audio... Press 'q' to quit early.")
    test_note = input("Add a note to the test measurement:")
    slack.post_message(f'Test started at {time_stamp()}')

    def on_press(key):
        try:
            # Stop the listener if 'q' is pressed
            if key.char == 'q':
                return False
        except AttributeError:
            pass


    def create_volume_bar(level, max_level, bar_length, threshold):
        """Create a graphical representation of the volume level with logarithmic scaling."""
        # check that level is non negative (can happen on windows 11)
        if level < 0:
            level = 0
        # Apply logarithmic scaling
        log_level = math.log1p(level) / math.log1p(max_level)
        log_threshold = math.log1p(threshold) / math.log1p(max_level)

        threshold_index = int(bar_length * log_threshold)
        volume_index = int(bar_length * log_level)
        bar = [' '] * bar_length
        for i in range(bar_length):
            if i < volume_index:
                bar[i] = '='
            if i == threshold_index:
                bar[i] = '|'
        return ''.join(bar)

    # Start a keyboard listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    start_time = None
    audio_detected = False
    buffer_start = None
    last_update_time = time.time()

    try:
        while True:
            # Check if the stream is active
            if not stream.is_active():
                raise RuntimeError("Audio stream is not active. Please check your microphone.")

            current_time = time.time()

            # Read data from the audio stream
            data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
            current_level = np.max(data)

            # Update the volume bar only every UPDATE_INTERVAL seconds
            if current_time - last_update_time >= UPDATE_INTERVAL:
                volume_bar = create_volume_bar(current_level, MAX_LEVEL, BAR_LENGTH, THRESHOLD)
                last_update_time = current_time

                if audio_detected and current_level < THRESHOLD:
                    if buffer_start is None:
                        buffer_start = time.time()  # Start buffer timer
                    else:
                        remaining_time = BUFFER_TIME - (time.time() - buffer_start)
                        if remaining_time <= 0:
                            end_time = time.time()
                            end_time_stamp = time_stamp() 
                            break
                        countdown_msg = f" - Countdown: {int(remaining_time)}s"
                else:
                    countdown_msg = ""

                print(f"Volume: [{volume_bar}] {countdown_msg}", end='\r')

            # Check if the current audio level exceeds the threshold
            if current_level > THRESHOLD:
                if not start_time:
                    print("\nAudio detected. Starting timer...")
                    start_time = time.time()
                    start_time_stamp = time_stamp()
                audio_detected = True
                buffer_start = None  # Reset buffer timer

            # Check for keypress to quit early
            if not listener.running and start_time:
                end_time = time.time()
                end_time_stamp = time_stamp()
                break
    except KeyboardInterrupt:
        end_time = time.time()
    except RuntimeError as e:
        print(e)
    finally:
        # Close the audio stream and terminate PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()

    # Calculate and print the duration if audio was detected
    if start_time:
        duration = end_time - start_time
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_duration = f"{int(hours)}h:{int(minutes):02d}m:{int(seconds):02d}s"
        print(f"\nDuration: {formatted_duration}")
        slack.post_message(
            f"Battery test ended at {end_time_stamp}\n"
            f"Duration was: {formatted_duration}\n"
            f"Test note: {test_note}"
            )


        # Write the duration to a file
        with open("duration.txt", "w") as file:
            file.write(
                f"Duration: {formatted_duration}\n"
                f"Start time: {start_time_stamp}\n"
                f"End time: {end_time_stamp}\nq"
                f"Note: {test_note}"
                )
    else:
        print("No audio detected.")

if __name__=="__main__":
    main()
