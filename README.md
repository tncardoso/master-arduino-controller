Master Arduino Controller
==================================

Arduino controller for the Master System console. The provided
application communicates with the arduino via serial port and behaves
like a controller.

License: 3-Clause BSD

Dependencies
----------------------------------

In order to execute this project you need the following python libs:

* pygame

Usage
----------------------------------

1. Using as a controller

    `./master.py`

2. Recording game session

    `./master.py record [output_session_file]`

3. Playing recorded session

    `./master.py replay [input_session_file]`

Troubleshooting
----------------------------------

### 1. Error opening serial port ###

This error can happen if you are using a different port for your serial
communication. Changing '/dev/ttyACM0' in:

    `self._serial = serial.Serial('/dev/ttyACM0', 9600)`

for your port should fix this bug. Possible ports are: '/dev/ttyUSB0',
'/dev/ttySB0' and others. If you are adapting for your os and you
have the time, please submit patches with fallback code. 

### 2. libc.so.6 not found ###

This can happen if you are using a different libc version or if you are
using mac os. Changing 'libc.so.6' in:

    `libc = ctypes.CDLL('libc.so.6')`

for your correct lib name should fix this bug. If you are adapting for
your os and you have the time, please submit patches with fallback code.

