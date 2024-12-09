# Bluetooth Gamepad Reader

A Python script for reading and displaying input data from a Bluetooth gamepad (ShanWan BM-768, also known as GamePadPlus V3) in real-time. The script supports both direct HID connection and Bluetooth LE connection methods.

## Features

- Real-time display of:
  - Joystick positions (both sticks, with percentage and direction)
  - Button states (A, B, X, Y, LB, RB, Select, Start)
  - D-pad state (8 directions)
  - Analog triggers (LT, RT) with pressure values
- Automatic connection handling:
  - Tries HID connection first
  - Falls back to Bluetooth LE if HID connection fails
  - Reconnection capability
- Raw data display for debugging

## Hardware Support

Currently tested with:
- ShanWan BM-768 (GamePadPlus V3)
  - Vendor ID: 0x1949
  - Product ID: 0x0402

Other similar Bluetooth gamepads might work but haven't been tested.

## Requirements

- Python 3.7+
- macOS (tested on macOS Sonoma)
- The following Python packages:
  - `hidapi`
  - `bleak`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/vcb88/gamepad-reader.git
cd gamepad-reader
```

2. Create and activate a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Unix-like systems
# or
.\venv\Scripts\activate  # On Windows
```

3. Install system dependencies (macOS):
```bash
brew install hidapi
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Make sure your gamepad is charged and turned on.

2. If this is the first time using the gamepad:
   - Put the gamepad in pairing mode (usually by holding the HOME button)
   - Pair it with your computer through System Settings -> Bluetooth

3. Run the script:
```bash
python gamepad_reader.py
```

4. The script will:
   - Try to connect to the gamepad
   - Display real-time input data
   - Show connection status and any errors
   - Allow reconnection if the connection is lost

5. Press Ctrl+C to stop the script.

## Troubleshooting

1. If the gamepad is not detected:
   - Ensure it's powered on
   - Try re-pairing it in System Settings
   - Check if it appears in the system's Bluetooth device list

2. If you get permission errors:
   - Ensure hidapi is installed correctly
   - Try running the script with sudo (if necessary)

3. If the connection is unstable:
   - Check gamepad battery level
   - Reduce distance to the computer
   - Remove sources of interference

## Output Format

The script displays:
```
=== Gamepad State ===

Main buttons: A, B, X, Y, LB, RB
System buttons: Select, Start
D-pad: up-right

Triggers:
LT: 128 (50%)
RT: 255 (100%)

Left stick:
X:  -50% ←
Y:   25% ↓

Right stick:
X:    0% |
Y:   75% ↓

Raw data: 04 80 80 80 80 ff 00 00 00 00 00
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

## Acknowledgments

- Thanks to the `hidapi` and `bleak` projects for making this possible
- Thanks to the Python gaming community for testing and feedback
