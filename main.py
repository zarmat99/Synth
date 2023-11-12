# implementare la gestione dell'inviluppo (attack, decay e release automatici e sustain funzione del tempo del tasto)
# cercare di capire come mai il ciclo for esce prima di duration nonostante gli array sono uguali (non cambio nulla)
# provare l'implementazione non periodo per periodo ma magari n periodo per n periodo
# acquistare potenziometro lineare e poi usare la formula completa qua:
#       serial_data                                                              -> [0, 1024]
#       log_serial_data = 1024^(serial_data/1024)                                -> [0, 1024]
#       log_serial_data_20khz = (log_serial_data-1) * (20000-20) / (1024-1) + 20 -> [20, 20000]

import time
import threading
import keyboard
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import PotentiometerWidget
import tkinter as tk
import tkinter.messagebox
import customtkinter

is_playing = False
waveform = "sine"
t = []
rate = 200000
audio_data = np.zeros(0)
frequency = 20
bit = 10
range_max = 2 ** bit
plot_event = 0
duration = 20


def plot_task():
    global t
    global audio_data
    global plot_event

    fig, ax = 0, 0
    plt.ion()

    while plot_event:
        if any(t):
            if not fig and not ax:
                fig, ax = plt.subplots()
            ax.clear()
            ax.plot(t, audio_data[0])
            plt.pause(0.1)
        time.sleep(0.1)

    if fig and ax:
        plt.close(fig)

    plt.ioff()
    print("plot killed")


def sound_task():
    global rate
    global frequency
    global audio_data
    global frequency
    global rate
    global duration

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=rate, output=True)
    # audio_data_old = array_to_matrix(np.zeros(rate * duration), rate / frequency)

    while True:
        if frequency != 0:
            if keyboard.is_pressed("ctrl"):
                audio_data_old = audio_data
                for period_wave in audio_data:
                    if keyboard.is_pressed("ctrl") and np.array_equal(audio_data_old, audio_data):
                        stream.write(np.array(period_wave).tobytes())
                    else:
                        break
                print("complete")
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

    while True:
        pot_value_freq = my_gui.potentiometer_freq.pot_value
        pot_value_fm_mod = my_gui.potentiometer_fm_mod.pot_value - 1
        frequency = map_to_20_20k(pot_value_freq)
        period = 1 / frequency
        period_samples = int(rate * period)
        total_samples = int(rate * duration)
        t = np.linspace(0, duration, total_samples, endpoint=False)

        if waveform == "sine":
            modulated_wave = apply_fm_modulation(pot_value_fm_mod, 1, duration, rate)
            modulated_wave = modulated_wave[:len(t)]
            audio_data = 0.5 * np.sin(2 * np.pi * (frequency + modulated_wave) * t)
        elif waveform == "square":
            audio_data = 0.5 * np.sign(np.sin(2 * np.pi * frequency * t))
        elif waveform == "sawtooth":
            audio_data = 0.5 * (t * frequency - np.floor(0.5 + t * frequency))

        audio_data = array_to_matrix(audio_data, period_samples)

        print(f"pot_value_freq = {pot_value_freq}")
        print(f"pot_value_fm_mod = {pot_value_fm_mod}")
        print(f"frequency: {frequency}")
        print(f"waveform: {waveform}")
        time.sleep(0.01)


def array_to_matrix(input_array, row_length):
    col_length = len(input_array) // row_length
    elements_exceeding = len(input_array) % row_length
    if elements_exceeding != 0:
        input_array = input_array[:-elements_exceeding]
    matrix = np.array(input_array).reshape((col_length, row_length))

    return matrix


def apply_fm_modulation(modulator_freq, modulation_index, duration, sample_rate):
    t = np.arange(0, duration, 1/sample_rate)
    modulator_wave = np.sin(2 * np.pi * modulator_freq * t)
    return modulation_index * modulator_wave


def generate_envelope(attack_time, decay_time, sustain_level, release_time, sample_rate):
    attack = np.linspace(0, 1, int(attack_time * sample_rate), endpoint=False)
    decay = np.linspace(1, sustain_level, int(decay_time * sample_rate), endpoint=False)
    sustain = np.full(int(sample_rate), sustain_level)
    release = np.linspace(sustain_level, 0, int(release_time * sample_rate), endpoint=False)

    envelope = np.concatenate([attack, decay, sustain, release])

    return envelope


def map_to_20_20k(value):
    return int((range_max**(value / range_max) - 1) * (20000 - 20) / (range_max - 1) + 20)


def open_serial_communication(com_port="COM7", baud_rate=9600):
    try:
        ser = serial.Serial(com_port, baud_rate)
        print("serial connection success!")
    except Exception as error:
        print(f"Error: {error}")
        exit(0)
    return ser


class GUI:
    def __init__(self, master):
        self.master = master
        master.title("GUI")

        self.button_sine = tk.Button(master, text="Sine", command=self.button_sine_event)
        self.button_square = tk.Button(master, text="Square", command=self.button_square_event)
        self.button_sawtooth = tk.Button(master, text="Sawtooth", command=self.button_sawtooth_event)
        self.button_plot = tk.Button(master, text="Open Plot", command=self.button_plot_event)
        self.potentiometer_freq = PotentiometerWidget.PotentiometerWidget(root, range_max=2**10,
                                                                     pot_func="linear", radius=50)
        self.potentiometer_fm_mod = PotentiometerWidget.PotentiometerWidget(root, range_max=100,
                                                                     pot_func="linear", radius=50)

        self.button_sine.grid(row=0, column=0, padx=10, pady=10)
        self.button_square.grid(row=0, column=1, padx=10, pady=10)
        self.button_sawtooth.grid(row=0, column=2, padx=10, pady=10)
        self.potentiometer_freq.grid(row=1, column=0)
        self.potentiometer_fm_mod.grid(row=1, column=1)
        self.button_plot.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    def button_sine_event(self):
        global waveform
        waveform = "sine"

    def button_square_event(self):
        global waveform
        waveform = "square"

    def button_sawtooth_event(self):
        global waveform
        waveform = "sawtooth"

    def button_plot_event(self):
        global plot_event

        if plot_event:
            plot_event = 0
            self.button_plot.configure(text="Start Plot")
        else:
            plot_event = 1
            self.button_plot.configure(text="Stop Plot")
            plot_thread = threading.Thread(target=plot_task)
            plot_thread.start()


if __name__ == '__main__':
    root = tk.Tk()
    my_gui = GUI(root)
    sound_thread = threading.Thread(target=sound_task)
    pot_thread = threading.Thread(target=pot_task)
    sound_thread.start()
    pot_thread.start()
    root.mainloop()


'''
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.a = 0
        # ------------------- Connection Page -------------------------------------------------------------------------
        # create page title label
        self.connection_page_title_label = customtkinter.CTkLabel(self, text="Connection Page",
                                                                  font=customtkinter.CTkFont(size=25, weight="bold"))

        # create obs configurations frame
        self.obs_conf_frame = customtkinter.CTkFrame(self)
        self.obs_conf_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.obs_conf_frame.grid_columnconfigure((0, 1), weight=1)
        #   row 0 -> frame label
        self.obs_configuration_label = customtkinter.CTkLabel(self.obs_conf_frame, text="OBS Configurations",
                                                 font=customtkinter.CTkFont(size=20))
        self.obs_configuration_label.grid(row=0, column=0, columnspan=2)
        #   row 1 -> host (label + entry)
        #       host label
        self.host_label = customtkinter.CTkLabel(self.obs_conf_frame, text="Host",
                                                 font=customtkinter.CTkFont(size=15))
        self.host_label.grid(row=1, column=0)
        #       host entry
        host_entry_var = tkinter.StringVar()
        self.host_entry = customtkinter.CTkEntry(self.obs_conf_frame, textvariable=host_entry_var)
        self.host_entry.grid(row=1, column=1)
        #   row 2 -> port (label + entry)
        #       port label
        self.port_label = customtkinter.CTkLabel(self.obs_conf_frame, text="Port",
                                                 font=customtkinter.CTkFont(size=15))
        self.port_label.grid(row=2, column=0)
        #       port entry
        port_entry_var = tkinter.StringVar()
        self.port_entry = customtkinter.CTkEntry(self.obs_conf_frame, textvariable=port_entry_var)
        self.port_entry.grid(row=2, column=1)
        #   row 3 -> password (label + entry)
        #       password label
        self.password_label = customtkinter.CTkLabel(self.obs_conf_frame, text="Password",
                                                     font=customtkinter.CTkFont(size=15))
        self.password_label.grid(row=3, column=0)
        #       password entry
        password_entry_var = tkinter.StringVar()
        self.password_entry = customtkinter.CTkEntry(self.obs_conf_frame, textvariable=password_entry_var)
        self.password_entry.grid(row=3, column=1)

        # create streamdeck configuration frame
        self.streamdeck_conf_frame = customtkinter.CTkFrame(self)
        self.streamdeck_conf_frame.grid_rowconfigure((0, 1, 2), weight=1)
        self.streamdeck_conf_frame.grid_columnconfigure((0, 1), weight=1)
        #   row 0 -> frame label
        self.obs_configuration_label = customtkinter.CTkLabel(self.streamdeck_conf_frame,
                                                              text="StreamDeck Configurations",
                                                              font=customtkinter.CTkFont(size=20))
        self.obs_configuration_label.grid(row=0, column=0, columnspan=2)
        #   row 1 -> com port (label + entry)
        #       com port label
        self.com_port_label = customtkinter.CTkLabel(self.streamdeck_conf_frame, text="Com Port",
                                                     font=customtkinter.CTkFont(size=15))
        self.com_port_label.grid(row=1, column=0)
        #       com port entry
        com_port_var = tkinter.StringVar()
        self.com_port_entry = customtkinter.CTkEntry(self.streamdeck_conf_frame, textvariable=com_port_var)
        self.com_port_entry.grid(row=1, column=1)
        #   row 2 -> baud rate (label + entry)
        #       baud rate label
        self.baud_rate_label = customtkinter.CTkLabel(self.streamdeck_conf_frame, text="Baud Rate",
                                                      font=customtkinter.CTkFont(size=15))
        self.baud_rate_label.grid(row=2, column=0)
        #       port entry
        baud_rate_var = tkinter.StringVar()
        self.baud_rate_entry = customtkinter.CTkEntry(self.streamdeck_conf_frame, textvariable=baud_rate_var)
        self.baud_rate_entry.grid(row=2, column=1)

        # create Connect Button
        self.connect_button = customtkinter.CTkButton(self, text="Connect",
                                                      command=self.connect_event)
        # -------------------------------------------------------------------------------------------------------------

        # ------------------- Page 2 ----------------------------------------------------------------------------------
        self.back_button = customtkinter.CTkButton(self, text="Back",
                                                      command=self.back_button_event)
        # -------------------------------------------------------------------------------------------------------------

        # ------------------- Init ------------------------------------------------------------------------------------
        self.connection_page_grid()

    def connection_page_grid(self):
        # configure window
        self.title("StreamDeck - Connection")
        self.geometry(f"{800}x{400}")

        # configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure((1, 2), weight=1)
        self.grid_rowconfigure(3, weight=0)

        # grid
        self.connection_page_title_label.grid(row=0, column=0, columnspan=2, pady=10)
        self.obs_conf_frame.grid(row=1, column=0, columnspan=2, sticky="nswe", padx=20, pady=(0, 10))
        self.streamdeck_conf_frame.grid(row=2, column=0, columnspan=2, sticky="nswe", padx=20, pady=(10, 10))
        self.connect_button.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="e")

    def connection_page_forget(self):
        self.obs_conf_frame.grid_forget()
        self.streamdeck_conf_frame.grid_forget()
        self.connection_page_title_label.grid_forget()
        self.connect_button.grid_forget()

    def page_2_grid(self):
        # configure window
        self.title("StreamDeck - Page 2")
        self.geometry(f"{800}x{400}")

        # configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # grid
        self.back_button.grid(row=0, column=0)

    def page_2_forget(self):
        self.back_button.grid_forget()

    def connect_event(self):
        self.connection_page_forget()
        self.page_2_grid()

    def back_button_event(self):
        self.page_2_forget()
        self.connection_page_grid()


if __name__ == '__main__':
    customtkinter.set_appearance_mode("Dark")
    customtkinter.set_default_color_theme("dark-blue")
    ser = open_serial_communication()
    plot_thread = threading.Thread(target=plot_task)
    sound_thread = threading.Thread(target=sound_task)
    pot_thread = threading.Thread(target=pot_task)
    plot_thread.start()
    sound_thread.start()
    pot_thread.start()
    app = App()
    app.mainloop()
'''



