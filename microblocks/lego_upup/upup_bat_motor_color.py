from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop, Axis
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))

def saturate(value):
    return clamp(value, 0.0, 1.0)

def hue_to_rgb(h):
    r = abs(h * 6.0 - 3.0) - 1.0
    g = 2.0 - abs(h * 6.0 - 2.0)
    b = 2.0 - abs(h * 6.0 - 4.0)
    return saturate(r), saturate(g), saturate(b)

def hsl_to_rgb(h, s, l):
    # Takes hue in range 0-359, 
    # Saturation and lightness in range 0-99
    h /= 359
    s /= 100
    l /= 100
    r, g, b = hue_to_rgb(h)
    c = (1.0 - abs(2.0 * l - 1.0)) * s
    r = (r - 0.5) * c + l
    g = (g - 0.5) * c + l
    b = (b - 0.5) * c + l
    rgb = tuple([round(x*255) for x in (r,g,b)])
    return rgb


from micropup import MicroPUP

hub = PrimeHub()
motor = Motor(Port.F)
colorsensor = ColorSensor(Port.E)

p=MicroPUP(Port.A)
p.add_command('bat', 0, 2)
p.add_command('motor', 1, 0)
p.add_command('color', 1, 3)


surface=True

while True:
    voltage = hub.battery.voltage()
    current = hub.battery.current()
    p.call('bat', voltage, current)
    angle = p.call("motor")
    motor.run_target(400,angle)
    color = colorsensor.hsv(surface=surface)
    surface = p.call('color',*hsl_to_rgb(color.h,color.s,color.v))
    wait(50)
