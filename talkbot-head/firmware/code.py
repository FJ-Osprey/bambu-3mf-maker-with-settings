# Jaw servo for the talking head: Raspberry Pi Pico running CircuitPython.
# The computer sends one byte per frame, the servo angle, about 50 times a second over the USB data serial port.
# No byte for 0.5 s closes the mouth. Wiring: signal GP15, + VBUS, - GND. Copy this and boot.py to the CIRCUITPY drive,
# and adafruit_motor to CIRCUITPY/lib.
import time

import board
import pwmio
import usb_cdc
from adafruit_motor import servo  # bundle lib: copy adafruit_motor/ into CIRCUITPY/lib

CLOSED = 20          # match --servo-min on the computer. Below this the paddle pushes into the face: never commanded.
OPEN_MAX = 48        # match --servo-max. Any byte outside CLOSED..OPEN_MAX is clamped here, whoever sent it.
TIMEOUT_S = 0.5      # no byte for this long: close
RELEASE_S = 1.0      # angle unchanged for this long: stop the pulses

# A servo fed pulses pushes back at full strength for as long as it's powered, even with the computer's program off. Against
# any load at closed that is stall current, and the servo got very hot sitting idle. With no
# pulses the motor is off and the gears hold the paddle. The next new angle switches it back on at once.
pwm = pwmio.PWMOut(board.GP15, duty_cycle=2 ** 15, frequency=50)
jaw = servo.Servo(pwm, min_pulse=500, max_pulse=2400)   # MG90S range; trim if it buzzes at the ends
jaw.angle = CLOSED

link = usb_cdc.data        # enabled in boot.py
target = CLOSED
last_byte = last_move = time.monotonic()
while True:
    now = time.monotonic()
    n = link.in_waiting if link else 0
    want = target
    if n:
        want = max(CLOSED, min(OPEN_MAX, link.read(n)[-1]))   # keep only the newest angle
        last_byte = now
    elif now - last_byte > TIMEOUT_S:
        want = CLOSED
    if want != target:
        target = want
        jaw.angle = target
        last_move = now
        print("angle", target)
    elif jaw.angle is not None and now - last_move > RELEASE_S:
        jaw.angle = None
        print("released at", target)
    time.sleep(0.005)
