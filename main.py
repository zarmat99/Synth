# acquistare potenziometro lineare e poi usare la formula completa qua:
# serial_data                                                              -> [0, 1024]
# log_serial_data = 1024^(serial_data/1024)                                -> [0, 1024]
# log_serial_data_20khz = (log_serial_data-1) * (20000-20) / (1024-1) + 20 -> [20, 20000]

import time
import threading
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import serial
import PotentiometerWidget
import tkinter as tk
import tkinter.messagebox
import customtkinter

waveform = "sine"
t = []
audio_data = np
rate = 200000
frequency = 20
bit = 10
range_max = 2 ** bit
plot_event = 0


def plot_task():
    global t
    global audio_data
    global plot_event

    fig = 0
    ax = 0

    plt.ion()
    while plot_event:
        if any(t):
            if not fig and not ax:
                fig, ax = plt.subplots()
            ax.clear()
            ax.plot(t, audio_data)
            plt.pause(0.1)
        time.sleep(1)

    if fig and ax:
        plt.close(fig)

    plt.ioff()
    print("plot killed")


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
        if frequency != 0:
            stream.write(np.array(audio_data).tobytes())
            # time.sleep(1 / frequency)

    stream.stop_stream()
    stream.close()
    p.terminate()


def map_to_20_20k(value):
    return int((value - 1) * (20000 - 20) / (range_max - 1) + 20)


def pot_task():
    global t
    global audio_data
    global rate
    global frequency
    global ser

    while True:
        serial_data = int(ser.readline().decode().strip())
        frequency = map_to_20_20k(serial_data)
        period = 1 / frequency

        print(f"serial_data = {serial_data}")
        print(f"frequency: {frequency}")
        print(f"waveform: {waveform}")
        num_samples = int(rate * period)

        t = np.linspace(0, period, num_samples, endpoint=False)
        if waveform == "sine":
            audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)
        elif waveform == "square":
            audio_data = 0.5 * np.sign(np.sin(2 * np.pi * frequency * t))
        elif waveform == "sawtooth":
            audio_data = 2 * (t * frequency - np.floor(0.5 + t * frequency))


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
        self.potentiometer = PotentiometerWidget.PotentiometerWidget(root, ser="COM8", range_max=2**10,
                                                                     pot_func="exp", radius=100)

        self.button_sine.grid(row=0, column=0, padx=10, pady=10)
        self.button_square.grid(row=0, column=1, padx=10, pady=10)
        self.button_sawtooth.grid(row=0, column=2, padx=10, pady=10)
        self.potentiometer.grid(row=1, column=0, columnspan=3)
        self.button_plot.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    def button_sine_event(self):
        global waveform
        waveform = "sine"
        self.potentiometer.send_pot_value_to_serial(self.potentiometer.angle_degrees_limit)

    def button_square_event(self):
        global waveform
        waveform = "square"
        self.potentiometer.send_pot_value_to_serial(self.potentiometer.angle_degrees_limit)

    def button_sawtooth_event(self):
        global waveform
        waveform = "sawtooth"
        self.potentiometer.send_pot_value_to_serial(self.potentiometer.angle_degrees_limit)

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
    ser = open_serial_communication()
    sound_thread = threading.Thread(target=sound_task)
    pot_thread = threading.Thread(target=pot_task)
    sound_thread.start()
    pot_thread.start()
    root = tk.Tk()
    my_gui = GUI(root)
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



