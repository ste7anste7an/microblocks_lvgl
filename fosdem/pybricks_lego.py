from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop, Axis
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

from microremote import MicroRemote

hub = PrimeHub()
m1 = Motor(Port.C)
m2 = Motor(Port.E)
ur=MicroRemote(Port.A)

while 1:
    m1.reset_angle()
    angle = m1.angle()
    nr_led = angle//30
    ur.call("led",nr_led+1)
    #print(nr_led)
    a = ur.call("angle")[1][0]
    print(a)
    m2.run_target(500,a)
    #wait(10)
print(s.time())