from tkinter import *
from tkinter import ttk
import numpy as np
import scipy.signal as signal
import threading
import sounddevice as sd
import soundfile as sf
from tkinter import filedialog

window = Tk()

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window_width = 500
window_height = 500
x_window = int((screen_width - window_width) / 2)
y_window = int((screen_height - window_height) / 2)

window.geometry(f"{window_width}x{window_height}+{x_window}+{y_window}")
window.title("Equalizer")

bands = [(50, 150), (200, 400), (500, 1000), (1100, 2500), (3000, 6000), (6000, 10000)]
gains = [1, 2, 6, 4, 3, 2]

status = StringVar(window)
file_path = r"Audio/CantinaBand60.wav"
playClicked = False


def open_file():
    global file_path
    file_path = filedialog.askopenfilename(defaultextension=".wav",
                                           filetypes=[("Wave Files", "*.wav")])
    update_audio()


def start():
    global playClicked
    playClicked = True
    t1 = threading.Thread(target=update_audio)
    t1.start()


def stop():
    sd.stop()
    status.set("Audio Paused")


def on_scale_changed(value):
    global playClicked
    if playClicked is True:
        sd.stop()
        update_audio()
    else:
        pass


def update_audio():
    # get the value of each scale
    print(file_path)
    audio, sr = sf.read(file_path)
    values = [scale.get() for scale in scales]
    print("Scale values:", values)

    order = 4
    b_coeffs = []
    a_coeffs = []
    for i, band in enumerate(bands):
        f_low, f_high = band
        nyquist = 0.5 * sr
        low = f_low / nyquist
        high = f_high / nyquist
        b, a = signal.butter(order, [low, high], btype='bandpass')
        b_coeffs.append(b * values[i])
        a_coeffs.append(a)

    # Apply each filter to the input signal
    filtered = np.zeros_like(audio)
    for b, a in zip(b_coeffs, a_coeffs):
        filtered += signal.lfilter(b, a, audio)

    # Normalize the filtered signal
    filtered /= np.max(np.abs(filtered))

    # Write the filtered signal to an output file
    sf.write('Audio/filtered_audio_file.wav', filtered, sr)
    print("Done")
    playaudio()


def playaudio():
    filename = 'Audio/filtered_audio_file.wav'
    data, fs = sf.read(filename, dtype='float32')  # load audio file

    sd.play(data, fs)  # play audio file
    status.set("Playing audio")


scales = []
for i in range(len(bands)):
    scale = Scale(window, from_=-12, to=12, orient=HORIZONTAL,
                  length=500, label="{}Hz - {}Hz".format(bands[i][0], bands[i][1]),
                  command=on_scale_changed)
    scale.set(gains[i])

    scale.pack()
    scales.append(scale)
ttk.Button(window, text="Open File", command=open_file).pack()
ttk.Button(window, text="Play Demo", command=start).pack()
ttk.Button(window, text="Stop", command=stop).pack()
ttk.Button(window, text="Start", command=update_audio).pack()
ttk.Label(window, textvariable=status).pack()
window.mainloop()
