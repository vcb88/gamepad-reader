import asyncio
from bleak import BleakScanner, BleakClient
import hid
import time
import sys
import platform

class GamePadReader:
    def __init__(self):
        self.target_name = "GamePadPlus V3"
        self.device = None
        self.client = None
        self.vendor_id = 0x1949
        self.product_id = 0x0402

    async def try_ble_connect(self):
        """Attempt to connect via Bluetooth LE"""
        print(f"Scanning for {self.target_name} via Bluetooth...")
        
        try:
            devices = await BleakScanner.discover(timeout=5.0)
            for device in devices:
                if device.name and self.target_name.lower() in device.name.lower():
                    print(f"\nFound {self.target_name} ({device.address})")
                    async with BleakClient(device) as client:
                        print("Connected via Bluetooth!")
                        await asyncio.sleep(2)  # Give time for connection to establish
                        return True
            return False
                
        except Exception as e:
            print(f"Bluetooth connection error: {str(e)}")
            return False

    def read_hid(self):
        """Read data via HID interface"""
        try:
            print("Looking for HID devices...")
            found = False
            # List all HID devices for debugging
            for device in hid.enumerate():
                print(f"\nFound device:")
                print(f"Vendor ID:  0x{device['vendor_id']:04x}")
                print(f"Product ID: 0x{device['product_id']:04x}")
                print(f"Path: {device['path']}")
                print(f"Manufacturer: {device['manufacturer_string']}")
                print(f"Product: {device['product_string']}")
                if device['vendor_id'] == self.vendor_id and device['product_id'] == self.product_id:
                    found = True

            if not found:
                raise hid.HIDException("Device not found in HID list")

            gamepad = hid.Device(self.vendor_id, self.product_id)
            print(f"\nSuccessfully opened HID device:")
            print(f"Manufacturer: {gamepad.manufacturer}")
            print(f"Product: {gamepad.product}")
            
            print("\nReading data... Press Ctrl+C to stop.\n")
            
            while True:
                try:
                    data = gamepad.read(64, timeout=100)
                    if data:
                        self.process_data(data)
                except TimeoutError:
                    continue
                except Exception as e:
                    print(f"Error reading data: {e}")
                    break
                    
        except IOError as e:
            print(f"\nCann't open HID device: {e}")
            return False
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            if 'gamepad' in locals():
                gamepad.close()

    def process_data(self, data):
        """Process data received from the gamepad"""
        try:
            # Joysticks
            left_x = data[1]
            left_y = data[2]
            right_x = data[3]
            right_y = data[4]
            
            # D-pad (bytes 5)
            dpad = data[5]
            dpad_mapping = {
                0x00: "up",
                0x01: "up-right",
                0x02: "right",
                0x03: "down-right",
                0x04: "down",
                0x05: "down-left",
                0x06: "left",
                0x07: "up-left",
                0xff: "center"
            }
            dpad_state = dpad_mapping.get(dpad, f"unknown (0x{dpad:02x})")
            
            # Main buttons - byte 6
            buttons = data[6]
            main_buttons = []
            if buttons & 0x01:
                main_buttons.append("A")
            if buttons & 0x02:
                main_buttons.append("B")
            if buttons & 0x08:
                main_buttons.append("X")
            if buttons & 0x10:
                main_buttons.append("Y")
            if buttons & 0x40:
                main_buttons.append("LB")
            if buttons & 0x80:
                main_buttons.append("RB")
            
            # Select/Start and triggers - byte 7
            system_buttons = data[7]
            sys_buttons = []
            triggers_active = []
            if system_buttons & 0x04:
                sys_buttons.append("Select")
            if system_buttons & 0x08:
                sys_buttons.append("Start")
            if system_buttons & 0x01:
                triggers_active.append("LT")
            if system_buttons & 0x02:
                triggers_active.append("RT")
            
            # Analog triggers values
            rt_value = data[8]  # RT
            lt_value = data[9]  # LT
            
            # Convert stick values to percentages
            def stick_to_percent(value, base=0x80):
                return round(((value - base) / 127.0) * 100)
            
            # Clear screen and display information
            print("\033[2J\033[H")  # Clear screen and move cursor to top
            print("=== Gamepad State ===")
            
            print("\nMain buttons:", ", ".join(main_buttons) if main_buttons else "none")
            print("System buttons:", ", ".join(sys_buttons) if sys_buttons else "none")
            print(f"D-pad: {dpad_state}")
            
            print("\nTriggers:")
            if "LT" in triggers_active:
                print(f"LT: {lt_value} ({lt_value / 255 * 100:.0f}%)")
            if "RT" in triggers_active:
                print(f"RT: {rt_value} ({rt_value / 255 * 100:.0f}%)")
            
            print("\nLeft stick:")
            print(f"X: {stick_to_percent(left_x):4d}% ({'←' if left_x < 0x80 else '→' if left_x > 0x80 else '|'})")
            print(f"Y: {stick_to_percent(left_y):4d}% ({'↑' if left_y < 0x80 else '↓' if left_y > 0x80 else '|'})")
            
            print("\nRight stick:")
            print(f"X: {stick_to_percent(right_x):4d}% ({'←' if right_x < 0x80 else '→' if right_x > 0x80 else '|'})")
            print(f"Y: {stick_to_percent(right_y):4d}% ({'↑' if right_y < 0x80 else '↓' if right_y > 0x80 else '|'})")
            
            print("\nRaw data:", ' '.join(f"{x:02x}" for x in data))
            
        except Exception as e:
            print(f"Error processing data: {str(e)}")

async def main():
    reader = GamePadReader()
    
    while True:
        try:
            # Try to open as HID first
            print("\nTrying to open as HID device...")
            try:
                reader.read_hid()
            except (IOError, hid.HIDException) as e:
                print(f"HID connection failed ({str(e)}), trying Bluetooth...")
                
                # If failed, try Bluetooth connection
                if await reader.try_ble_connect():
                    print("Bluetooth connection successful, trying HID again...")
                    try:
                        # Give system time to register HID device
                        await asyncio.sleep(2)
                        # Try HID again after successful Bluetooth connection
                        reader.read_hid()
                    except (IOError, hid.HIDException) as e:
                        print(f"Failed to open HID after Bluetooth connection: {str(e)}")
                else:
                    print("Bluetooth connection failed.")
            
            print("\nRetry? (y/n)")
            response = input().lower().strip()
            if response != 'y':
                break
                
        except KeyboardInterrupt:
            print("\nStopping...")
            try:
                response = input("\nRetry? (y/n) ").lower().strip()
                if response != 'y':
                    break
            except KeyboardInterrupt:
                break
        
        except asyncio.CancelledError:
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        print("\nCleanup complete.")
