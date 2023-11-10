import time
import threading
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import serial
import keyboard

t = []
audio_data = np
rate = 200000
frequency = 0
range_max = 1024

def plot_task():
    global t
    global audio_data
    fig = 0
    ax = 0

    plt.ion()
    while True:
        if any(t):
            if not fig and not ax:
                fig, ax = plt.subplots()
            ax.clear()
            ax.plot(t, audio_data)
            plt.pause(0.1)

    plt.ioff()
    plt.show()


def sound_task():
    global rate
    global frequency
    global audio_data

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=rate,
                    output=True)
    while True:
        while keyboard.is_pressed("space"):
            if frequency != 0:
                stream.write(np.array(audio_data).tobytes())
                # time.sleep(1 / frequency)

    stream.stop_stream()
    stream.close()
    p.terminate()


def pot_task():
    global t
    global audio_data
    global rate
    global frequency
    global ser

    waveform = "sine"
    while True:
        serial_data = ser.readline()
        frequency = int((int(serial_data.decode()) - 1) * (20000 - 20) / (range_max - 1) + 20)
        period = 1 / frequency

        print(f"frequency: {frequency}")

        num_samples = int(rate * period)

        t = np.linspace(0, period, num_samples, endpoint=False)
        audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)


def open_serial_communication(com_port="COM7", baud_rate=9600):
    try:
        ser = serial.Serial(com_port, baud_rate)
        print("serial connection success!")
    except Exception as error:
        print(f"Error: {error}")
        exit(0)
    return ser


if __name__ == '__main__':
    ser = open_serial_communication()
    plot_thread = threading.Thread(target=plot_task)
    sound_thread = threading.Thread(target=sound_task)
    pot_thread = threading.Thread(target=pot_task)
    # plot_thread.start()
    sound_thread.start()
    pot_thread.start()

