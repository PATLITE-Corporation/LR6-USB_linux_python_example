import struct
import sys

import usb.core
from usb.core import Device


VENDOR_ID = 0x191A
"""vendor ID"""
DEVICE_ID = 0x8003
"""device ID"""
COMMAND_VERSION = 0x00
"""command version"""
COMMAND_ID = 0x00
"""command ID"""
ENDPOINT_ADDRESS = 1
"""endpoint address for transmission from host to USB control stacked signal light"""
SEND_TIMEOUT = 1000
"""timeout time for sending command"""

# LED unit color
LED_COLOR_RED = 0
"""red"""
LED_COLOR_YELLOW = 1
"""yellow"""
LED_COLOR_GREEN = 2
"""green"""
LED_COLOR_BLUE = 3
"""blue"""
LED_COLOR_WHITE = 4
"""white"""

# LED pattern
LED_OFF = 0x0
"""light off"""
LED_ON = 0x1
"""lighted"""
LED_PATTERN1 = 0x2
"""LED pattern 1"""
LED_PATTERN2 = 0x3
"""LED pattern 2"""
LED_PATTERN3 = 0x4
"""LED pattern 3"""
LED_PATTERN4 = 0x5
"""LED pattern 4"""
LED_KEEP = 0xF
"""keep current settings"""

# buzzer pattern
BUZZER_OFF = 0x0
"""stop"""
BUZZER_ON = 0x1
"""buzzing (continuous)"""
BUZZER_PATTERN1 = 0x2
"""buzzer pattern 1"""
BUZZER_PATTERN2 = 0x3
"""buzzer pattern 2"""
BUZZER_PATTERN3 = 0x4
"""buzzer pattern 3"""
BUZZER_PATTERN4 = 0x5
"""buzzer pattern 4"""
BUZZER_KEEP = 0xF
"""keep current settings"""

# buzzer pitch
BUZZER_PITCH_OFF = 0x0
"""stop"""
BUZZER_PITCH1 = 0x1
"""A6"""
BUZZER_PITCH2 = 0x2
"""B♭6"""
BUZZER_PITCH3 = 0x3
"""B6"""
BUZZER_PITCH4 = 0x4
"""C7"""
BUZZER_PITCH5 = 0x5
"""D♭7"""
BUZZER_PITCH6 = 0x6
"""D7"""
BUZZER_PITCH7 = 0x7
"""E♭7"""
BUZZER_PITCH8 = 0x8
"""E7"""
BUZZER_PITCH9 = 0x9
"""F7"""
BUZZER_PITCH10 = 0xA
"""G♭7"""
BUZZER_PITCH11 = 0xB
"""G7"""
BUZZER_PITCH12 = 0xC
"""A♭7"""
BUZZER_PITCH13 = 0xD
"""A7"""
BUZZER_PITCH_DFLT_A = 0xE
"""default value for note A: D7"""
BUZZER_PITCH_DFLT_B = 0xF
"""default value for sound B: (stop)"""


def main():
    args = sys.argv
    argc = len(sys.argv)

    # Connect to a USB controlled stacked signal light via USB communication
    dev = usb_open()

    # Get the command identifier specified by the command line argument
    commandId = 0;
    if argc > 1:
        commandId = args[1];

    if commandId == '1':
        # Turn on and pattern the USB controlled stacked signal lights by specifying the LED color and LED pattern
        if argc >= 4:
            set_light(dev, int(args[2]), int(args[3]))

    elif commandId == '2':
        # Pattern lighting of USB controlled stacked signal lights by specifying multiple LED colors and LED patterns
        if argc >= 7:
            set_tower(dev, int(args[2]), int(args[3]), int(args[4]), int(args[5]), int(args[6]))

    elif commandId == '3':
        # Specify buzzer pattern to buzz USB controlled stacked signal lights
        if argc >= 4:
            set_buz(dev, int(args[2]), int(args[3]))

    elif commandId == '4':
        # Specify buzzer scale and pattern to buzz USB controlled laminated signal lights
        if argc >= 6:
            set_buz_ex(dev, int(args[2]), int(args[3]), int(args[4]), int(args[5]))

    elif commandId == '5':
        # Turn off all LED units and stop the buzzer
        reset(dev)

    # Terminate USB communication with USB controlled stacked signal light
    usb_close()


def usb_open() -> Device:
    """
    Connect to a USB controlled stacked signal light via USB communication

    Returns
    -------
    dev : Device
        Device instance of USB controlled stacked signal light
    """

    # Search for devices
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=DEVICE_ID)
    if dev is None:
        raise ValueError('device not found')

    if sys.platform == 'linux':
        # Detach the kernel driver
        # ※Run only in Linux environment.
        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)

    # Setting up device configuration
    dev.set_configuration()

    return dev


def usb_close():
    """
    Terminate USB communication with USB controlled stacked signal light
    ※No implementation, as it will be automatically released.
    """
    pass


def send_command(dev: Device, data: bytes) -> bool:
    """
    Send command

    Parameters
    ----------
    dev: Device
        Device instance to be sent
    data: bytes
        Data to be sent

    Returns
    -------
    bool
        Result of sending (Success: True, Failure: False)
    """

    try:
        # Send
        write_length = dev.write(ENDPOINT_ADDRESS, data, SEND_TIMEOUT)
        if sys.platform == 'win32':
            # In the Windows environment, reduce the write size by 1 byte because it returns 1 byte more.
            write_length -= 1

        if write_length != len(data):
            print('falsed to send')
            return False

        return True

    finally:
        # Resetting the device
        dev.reset()


def set_light(dev: Device, color: int, state: int) -> bool:
    """
    Turn on and pattern the USB controlled stacked signal lights by specifying the LED color and LED pattern.

    The buzzer and LED units other than the specified LED color will maintain their current state.

    Parameters
    ----------
    dev: Device
        Device instance to be sent
    color: int
        LED color to control (Red: 0, Yellow: 1, Green: 2, Blue: 3, White: 4)
    state: int
        LED pattern (off: 0, on: 0x1, LED pattern 1: 0x2, LED pattern 2: 0x3, LED pattern 3: 0x4, LED pattern 4: 0x5, keep current setting: 0x6 to 0xF)

    Returns
    -------
    bool
        Result of sending (Success: True, Failure: False)
    """

    # Data conversion for LED control
    led_ry = (LED_KEEP << 4) | LED_KEEP
    led_gb = (LED_KEEP << 4) | LED_KEEP
    led_w_ = LED_KEEP << 4
    if color == LED_COLOR_RED:          # red
        led_ry = state << 4
        led_ry |= LED_KEEP

    elif color == LED_COLOR_YELLOW:     # yellow
        led_ry = LED_KEEP << 4
        led_ry |= state

    elif color == LED_COLOR_GREEN:      # green
        led_gb = state << 4
        led_gb |= LED_KEEP

    elif color == LED_COLOR_BLUE:       # blue
        led_gb = LED_KEEP << 4
        led_gb |= state

    elif color == LED_COLOR_WHITE:      # white
        led_w_ = state << 4

    else:
        print('out of range color')
        return False

    # Converted to communication data
    data = struct.pack(
        'BBBBBBBx',         # format
        COMMAND_VERSION,    # command version (0x00: fixed)
        COMMAND_ID,         # Command ID (0x00: fixed)
        BUZZER_KEEP,        # buzzer control (status quo)
        0,                  # buzzer scale
        led_ry,             # LED control (red, yellow)
        led_gb,             # LED control (green/blue)
        led_w_,             # LED Control (white, fixed)
    )

    # Send command
    ret = send_command(dev, data)
    if ret is False:
        print('failed to send data')
        return False

    return True


def set_tower(dev: Device, red: int, yellow: int, green: int, blue: int, white: int) -> bool:
    """
    Pattern lighting of USB controlled stacked signal lights by specifying multiple LED colors and LED patterns

    Parameters
    ----------
    dev: Device
        Device instance to be sent
    red: int
        Red LED pattern (off: 0, on: 0x1, LED pattern 1: 0x2, LED pattern 2: 0x3, LED pattern 3: 0x4, LED pattern 4: 0x5, keep current setting: 0x6 to 0xF)
    yellow: int
        Yellow LED pattern (off: 0, on: 0x1, LED pattern 1: 0x2, LED pattern 2: 0x3, LED pattern 3: 0x4, LED pattern 4: 0x5, keep current setting: 0x6 to 0xF)
    green: int
        Green LED pattern (off: 0, on: 0x1, LED pattern 1: 0x2, LED pattern 2: 0x3, LED pattern 3: 0x4, LED pattern 4: 0x5, keep current setting: 0x6 to 0xF)
    blue: int
        Blue LED pattern (off: 0, on: 0x1, LED pattern 1: 0x2, LED pattern 2: 0x3, LED pattern 3: 0x4, LED pattern 4: 0x5, keep current setting: 0x6 to 0xF)
    white: int
        White LED pattern (off: 0, on: 0x1, LED pattern 1: 0x2, LED pattern 2: 0x3, LED pattern 3: 0x4, LED pattern 4: 0x5, keep current setting: 0x6 to 0xF)

    Returns
    -------
    bool
        Result of sending (Success: True, Failure: False)
    """

    # Data conversion for LED control
    led_ry = red << 4
    led_ry |= yellow
    led_gb = green << 4
    led_gb |= blue
    led_w_ = white << 4

    # Converted to communication data
    data = struct.pack(
        'BBBBBBBx',         # format
        COMMAND_VERSION,    # command version (0x00: fixed)
        COMMAND_ID,         # Command ID (0x00: fixed)
        BUZZER_KEEP,        # buzzer control (status quo)
        0,                  # buzzer scale
        led_ry,             # LED control (red, yellow)
        led_gb,             # LED control (green/blue)
        led_w_,             # LED Control (white, fixed)
    )

    # Send command
    ret = send_command(dev, data)
    if ret is False:
        print('failed to send data')
        return False

    return True


def set_buz(dev: Device, buz_state: int, limit: int) -> bool:
    """
    Specify buzzer pattern to buzz USB controlled stacked signal lights.

    The LED unit will maintain its current state. /// LED unit maintains its current state; scale operates at default values.

    Parameters
    ----------
    dev: Device
        Device instance to be sent
    buz_state: int
        Buzzer pattern
    limit: int
        Continuous operation: 0, frequency operation: 1-15

    Returns
    -------
    bool
        Result of sending (Success: True, Failure: False)
    """

    # Buzzer control
    buzzer_control = limit << 4
    buzzer_control |= buz_state

    # buzzer scale
    buzzer_pitch = BUZZER_PITCH_DFLT_A << 4
    buzzer_pitch |= BUZZER_PITCH_DFLT_B

    # LED control (status quo)
    led_ry = LED_KEEP << 4
    led_ry |= LED_KEEP
    led_gb = LED_KEEP << 4
    led_gb |= LED_KEEP
    led_w_ = LED_KEEP << 4

    # Converted to communication data
    data = struct.pack(
        'BBBBBBBx',         # format
        COMMAND_VERSION,    # command version (0x00: fixed)
        COMMAND_ID,         # Command ID (0x00: fixed)
        buzzer_control,     # Buzzer control
        buzzer_pitch,       # buzzer scale
        led_ry,             # LED control (red, yellow)
        led_gb,             # LED control (green/blue)
        led_w_,             # LED Control (white, fixed)
    )

    # Send command
    ret = send_command(dev, data)
    if ret is False:
        print('failed to send data')
        return False

    return True


def set_buz_ex(dev: Device, buz_state: int, limit: int, pitch1: int, pitch2: int) -> bool:
    """
    Specify buzzer scale and pattern to buzz USB controlled laminated signal lights

    Parameters
    ----------
    dev: Device
        Device instance to be sent
    buz_state: int
        Buzzer pattern
    limit: int
        Continuous operation: 0, frequency operation: 1 to 15
    pitch1: int
        Buzzer scale for note A (Stop: 0x0, A6: 0x1, B♭6: 0x2, B6: 0x3, C7: 0x4, D♭7: 0x5, D7: 0x6, E♭7: 0x7, E7: 0x8, F7: 0x9, G♭7: 0xA, G7: 0xB, A♭7: 0xC, A7 : 0xD, default value for note A: D7: 0xE, default value for note B: (stop): 0xF)
    pitch2: int
        Buzzer scale for note B (Stop: 0x0, A6: 0x1, B♭6: 0x2, B6: 0x3, C7: 0x4, D♭7: 0x5, D7: 0x6, E♭7: 0x7, E7: 0x8, F7: 0x9, G♭7: 0xA, G7: 0xB, A♭7: 0xC, A7 : 0xD, default value for note A: D7: 0xE, default value for note B: (stop): 0xF)

    Returns
    -------
    bool
        Result of sending (Success: True, Failure: False)
    """

    # Buzzer control
    buzzer_control = limit << 4
    buzzer_control |= buz_state

    # buzzer scale
    buzzer_pitch = pitch1 << 4
    buzzer_pitch |= pitch2

    # LED control (status quo)
    led_ry = LED_KEEP << 4
    led_ry |= LED_KEEP
    led_gb = LED_KEEP << 4
    led_gb |= LED_KEEP
    led_w_ = LED_KEEP << 4

    # Converted to communication data
    data = struct.pack(
        'BBBBBBBx',         # format
        COMMAND_VERSION,    # command version (0x00: fixed)
        COMMAND_ID,         # Command ID (0x00: fixed)
        buzzer_control,     # Buzzer control
        buzzer_pitch,       # buzzer scale
        led_ry,             # LED control (red, yellow)
        led_gb,             # LED control (green/blue)
        led_w_,             # LED Control (white, fixed)
    )

    # Send command
    ret = send_command(dev, data)
    if ret is False:
        print('failed to send data')
        return False

    return True


def reset(dev: Device) -> bool:
    """
    Turn off all LED units and stop the buzzer

    Parameters
    ----------
    dev: Device
        Device instance to be sent

    Returns
    -------
    bool
        Result of sending (Success: True, Failure: False)
    """

    # Converted to communication data
    data = struct.pack(
        'BBBBBBBx',         # format
        COMMAND_VERSION,    # command version (0x00: fixed)
        COMMAND_ID,         # Command ID (0x00: fixed)
        BUZZER_OFF,         # Buzzer control
        BUZZER_PITCH_OFF,   # buzzer scale
        LED_OFF,            # LED control (red, yellow)
        LED_OFF,            # LED control (green/blue)
        LED_OFF,            # LED Control (white, fixed)
    )

    # Send command
    ret = send_command(dev, data)
    if ret is False:
        print('failed to send data')
        return False

    return True


if __name__ == '__main__':
    main()
