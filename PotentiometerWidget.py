import tkinter as tk
import math
import serial


def frequency_serial_data_map():
    range_range_max = range(1024)
    for element in range_range_max:
        frequency = int((element - 1) * (20000 - 20) / (1023 - 1) + 20)
        print(f"value={element} | frequency={frequency}")


class PotentiometerWidget(tk.Canvas):
    def __init__(self, master, radius, pot_func="linear", range_max=1024, **kwargs):
        super().__init__(master, **kwargs)
        self.angle_degrees_limit = 0
        self.pot_value = 0
        self.pot_func = pot_func
        self.radius = radius
        self.center_x = 0
        self.center_y = 0
        self.current_ray = None
        self.starting_angle_degrees = -135
        self.range_max = range_max
        self.range_min = 1 # always equals 1
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
        print(f"click (x, y): ({x}, {y})")
        angle = math.atan2(self.center_y - y, x - self.center_x)
        angle_degrees = angle * (180.0 / math.pi)

        if -135 <= angle_degrees <= -90:
            self.angle_degrees_limit = -135
        elif -90 <= angle_degrees <= -45:
            self.angle_degrees_limit = -45
        else:
            self.angle_degrees_limit = angle_degrees

        angle_radians = self.angle_degrees_limit * (math.pi / 180.0)
        x1 = self.center_x + self.radius * math.cos(angle_radians)
        y1 = self.center_y - self.radius * math.sin(angle_radians)

        self.current_ray = self.create_line(self.center_x, self.center_y, x1, y1, fill="black", width=8)
        self.map_pot_value(self.angle_degrees_limit)

    def map_pot_value(self, angle_degrees_limit):
        if -180 <= angle_degrees_limit <= -135:
            angle_map = abs(angle_degrees_limit + 135)
        elif -45 <= angle_degrees_limit <= 180:
            angle_map = 225 - angle_degrees_limit
        else:
            angle_map = "None"

        pot_value_range_max = int((angle_map / 270) * (self.range_max - 1)) + 1
        if self.pot_func == "exp":
            # y = a + e^(b * x)
            # find a, b -> conditions: pass through P1(0, 1) and P2(max, max) because we want to map range the linear
            #                          range [0, max] in exponential range [1, max]
            #
            # pass through P1(0, 1)       -> 1 = a + e^(b * 0)
            #                                a = 0
            # pass through P2(max, max) -> max = e^(b * max)
            #                                b = ln(max) / max
            # y = e^(ln(max) / max * x) is equal to max^(x/max), so:
            pot_value_range_max_log = self.range_max ** (pot_value_range_max / self.range_max)
            self.pot_value = pot_value_range_max_log
        elif self.pot_func == "linear":
            self.pot_value = pot_value_range_max

        print(f"degrees angle limited: {angle_degrees_limit}")
        print(f"angle map = {angle_map}")
        print(f"pot_value_range_max = {pot_value_range_max}")
        if self.pot_func == "exp":
            print(f"pot_value_range_max_log = {int(pot_value_range_max_log)}\n")

    def linear_value(self, x1, y1, x2, y2, x):
        m = (y2 - y1) / (x2 - x1)
        q = y1 - m * x1
        return m * x + q

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

    pot = PotentiometerWidget(root, range_max=2**10, pot_func="exp", radius=100)
    pot.pack(fill=tk.BOTH, expand=True)

    root.mainloop()
