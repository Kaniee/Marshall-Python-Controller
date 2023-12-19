from inputs import get_gamepad
import inputs
from udp2 import MarshallConnection

def remember_value(func):
    oldValue = 0
    def wrapper_remember(connection, value):
        nonlocal oldValue
        func(connection, value, oldValue)
        oldValue = value
    return wrapper_remember

def btn_start(connection, value):
    if value == 1:
        connection.power_on()

def btn_stop(connection, value):
    if value == 1:
        exit(0)

def sign(value):
    if value > 0:
        return 1 
    if value < 0:
        return -1
    return 0

def stick_curve(value):
    cut = 6000
    lim = 2**15
    cutted = value - sign(value) * min(cut, abs(value))
    return cutted / (lim - cut)

y_speed = 0
x_speed = 0

@remember_value
def stick_right_x(connection, value, oldValue):
    global x_speed
    global y_speed
    pan_speed = round(stick_curve(value) * 0x10)
    if pan_speed != round(stick_curve(oldValue) * 0x10):
        print(f'X {pan_speed} {value} {y_speed}')
        x_speed = pan_speed
        connection.move(pan_speed=x_speed, tilt_speed=y_speed)

@remember_value
def stick_right_y(connection, value, oldValue):
    global x_speed
    global y_speed
    tilt_speed = round(stick_curve(value) * 0x08)
    if tilt_speed != round(stick_curve(oldValue) * 0x08):
        print(f'Y {tilt_speed} {value} {x_speed}')
        y_speed = tilt_speed
        connection.move(pan_speed=x_speed, tilt_speed=y_speed)

@remember_value
def accel_right(connection, value, oldValue):
    zoom_speed = round(value / 2**8 * 8)
    if zoom_speed != round(oldValue / 2**8 * 8):
        print(f'Z {zoom_speed} {value}')
        connection.zoom(zoom_speed=zoom_speed)

@remember_value
def accel_left(connection, value, oldValue):
    zoom_speed = round(-value / 2**8 * 8)
    if zoom_speed != round(-oldValue / 2**8 * 8):
        print(f'Z {zoom_speed} {value}')
        connection.zoom(zoom_speed=zoom_speed)

def btn_A(connection, value):
    if value == 1:
        connection.stop()

event_dict = {
    'Key': {
        'BTN_SOUTH': btn_A,
        'BTN_WEST': None,
        'BTN_NORTH': None,
        'BTN_EAST': None,
        'BTN_START': btn_stop,
        'BTN_SELECT': btn_start,
        'BTN_TR': None,
        'BTN_TL': None,
        'BTN_THUMBL': None,
        'BTN_THUMBR': None
    },
    'Absolute': {
        'ABS_RX': None, # [-2^15, 2^15-1]
        'ABS_RY': None, # [-2^15, 2^15-1]
        'ABS_X': stick_right_x, # [-2^15, 2^15-1]
        'ABS_Y': stick_right_y, # [-2^15, 2^15-1]
        'ABS_HAT0Y': None, # [-2^0, 2^0] (Down = 1)
        'ABS_HAT0X': None, # [-2^0, 2^0] (Right = 1)
        'ABS_RZ': accel_right, # [0, 2^8-1]
        'ABS_Z': accel_left # [0, 2^8-1]
    }
}

conn = MarshallConnection()
controller2 = inputs.devices.gamepads[1]
while True:
    events = controller2.read()
    print(events)
    for event in events:
        if event.ev_type == 'Sync':
            continue
        f = event_dict[event.ev_type][event.code]
        if callable(f):
            f(conn, event.state)
