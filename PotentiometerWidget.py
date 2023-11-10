import tkinter as tk
import math
import serial


def frequency_serial_data_map():
    range_range_max = range(1024)
    for element in range_range_max:
        frequency = int((element - 1) * (20000 - 20) / (1023 - 1) + 20)
        print(f"value={element} | frequency={frequency}")


class PotentiometerWidget(tk.Canvas):
    def __init__(self, master, radius, ser, pot_func="linear", **kwargs):
        super().__init__(master, **kwargs)
        self.pot_func = pot_func
        self.radius = radius
        self.center_x = 0
        self.center_y = 0
        self.current_ray = None
        self.starting_angle_degrees = -135
        self.ser = serial.Serial(ser, baudrate=9600)
        self.range_max = 1024
        self.range_min = 1
        self.log_speed_factor = 2  # velocità crescita
        self.bind("<Configure>", self.setup)
        self.bind("<Button-1>", self.draw_ray)
        self.bind("<B1-Motion>", self.draw_ray)

    def setup(self, event):
        self.delete("all")
        w = event.width
        h = event.height
        self.center_x = w / 2
        self.center_y = h / 2
        x = self.center_x
        y = self.center_y
        self.create_oval(x - self.radius, y - self.radius, x + self.radius, y + self.radius, outline="black",
                         fill="grey", width=4, tags="circle")
        self.after(10, self.draw_initial_ray)

    def draw_ray(self, event):
        if self.current_ray:
            self.delete(self.current_ray)

        x, y = event.x, event.y
        angle = math.atan2(self.center_y - y, x - self.center_x)
        angle_degrees = angle * (180.0 / math.pi)

        if -135 <= angle_degrees <= -90:
            angle_degrees_limit = -135
        elif -90 <= angle_degrees <= -45:
            angle_degrees_limit = -45
        else:
            angle_degrees_limit = angle_degrees

        angle_radians = angle_degrees_limit * (math.pi / 180.0)
        x1 = self.center_x + self.radius * math.cos(angle_radians)
        y1 = self.center_y - self.radius * math.sin(angle_radians)

        self.current_ray = self.create_line(self.center_x, self.center_y, x1, y1, fill="black", width=8)

        if -180 <= angle_degrees_limit <= -135:
            angle_map = abs(angle_degrees_limit + 135)
        elif -45 <= angle_degrees_limit <= 180:
            angle_map = 225 - angle_degrees_limit
        else:
            angle_map = "None"

        pot_value_range_max = int((angle_map / 270) * (self.range_max - 1)) + 1
        if self.pot_func == "log":
            pot_value_1000 = pot_value_range_max / (self.range_max / 100)
            pot_value_range_max_log = self.range_min * (self.range_max / self.range_min) ** (pot_value_1000 / 100)
            self.ser.write((str(int(pot_value_range_max_log))).encode() + "\n".encode())

        print(f"click (x, y): ({x}, {y})")
        print(f"degrees angle limited: {angle_degrees_limit}")
        print(f"angle map = {angle_map}")
        print(f"pot_value_range_max = {pot_value_range_max}")
        if self.pot_func == "log":
            print(f"pot_value_1000 = {pot_value_1000}")
            print(f"pot_value = {pot_value_range_max_log}\n")

    def draw_initial_ray(self):
        initial_angle_degrees = self.starting_angle_degrees
        initial_angle_radians = initial_angle_degrees * (math.pi / 180.0)
        x1 = self.center_x + self.radius * math.cos(initial_angle_radians)
        y1 = self.center_y - self.radius * math.sin(initial_angle_radians)

        self.current_ray = self.create_line(self.center_x, self.center_y, x1, y1, fill="black", width=8)

    def serial_send(self, value):
        self.ser.write(str(value).encode())


if __name__ == "__main__":
    serial_port = "COM8"

    root = tk.Tk()
    root.title("Widget Cerchio con Raggi")

    pot = PotentiometerWidget(root,ser=serial_port, pot_func="log", radius=100)
    pot.pack(fill=tk.BOTH, expand=True)

    root.mainloop()
