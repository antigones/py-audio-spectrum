from asyncio import base_events
import queue
import sounddevice as sd
import numpy as np
import math
from reprint import output
from colorama import init, Fore
init()

N_BINS = 10 # the number of bins to divide the frequency interval to
SAMPLE_RATE = 44100 # the recording sample rate
GAIN = 1500 # a gain factor
MAX_BAR_HEIGHT = 50 # cap for magnitude bar height

BASE_COLOR = Fore.BLUE # color for base of the bar
TOP_COLOR = Fore.WHITE # color for bar top
BASE_HEIGHT = 2 # height for bar base

low, high = [0, 22000] # the range of frequencies to capture
delta_f = (high - low) / N_BINS # the frequency span for every bin
fftsize = math.ceil(SAMPLE_RATE / delta_f) # the number of bars resulting from the RFFT * 2
q = queue.Queue() # a queue to put signal input


def audio_callback(indata:np.ndarray, frames, time, status) -> None:
    """The callback function for audio input"""
    q.put(indata)

def generate_sine_wave(freq:int, sample_rate:int, duration:int) -> tuple:
    """A function to test the visualization, increasing frequency should result in increasing bin frequency bar presence"""
    x = np.linspace(0, duration, sample_rate * duration, endpoint=False)
    frequencies = x * freq
    y = np.sin((2 * np.pi) * frequencies)
    return x, y

def get_magnitudes(data:np.ndarray) -> np.ndarray:
    """Computes the rfft of the signal"""
    # _, data = generate_sine_wave(10000, SAMPLE_RATE, 5)
    if any(data):
        magnitudes = np.abs(np.fft.rfft(data[:, 0], n=fftsize))
        magnitudes *= GAIN / fftsize
        return magnitudes


def process_input() -> None:
    """Process input from mic and display the results in a bar-like console interface"""
    with output(initial_len=fftsize, interval=0) as output_list:
        with sd.InputStream(samplerate=SAMPLE_RATE, callback=audio_callback, blocksize=30, channels=1):
            while True:
                data = q.get()
                amplitudes = get_magnitudes(data)
                for i, bin_height in enumerate(amplitudes):
                    if int(bin_height) > 0:
                        int_bin_height = int(bin_height)
                        if int_bin_height > MAX_BAR_HEIGHT:
                            int_bin_height = MAX_BAR_HEIGHT
                        base = "*" * BASE_HEIGHT
                        top = "*" * (int_bin_height - BASE_HEIGHT)
                        output_list[i] = "".join([BASE_COLOR, base, TOP_COLOR, top])
                    else:
                        output_list[i] = "".join([BASE_COLOR, "*"])


if __name__ == "__main__":
    process_input()