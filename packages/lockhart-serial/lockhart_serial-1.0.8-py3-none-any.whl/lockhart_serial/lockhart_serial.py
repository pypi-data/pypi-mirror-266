from serial import Serial
import time

class LockhartSerial():
    def __init__(self, port, baudrate=115200):
        self.serial = Serial(port, baudrate)
        self.directions = {
            'up': 1,
            'up_right' : 2,
            'right': 3,
            'down_right': 4,
            'down' : 5,
            'down_left': 6,
            'left': 7,
            'up_left': 8
        }

        self.analog = [
            'x',
            'y',
            'z',
            'rx',
            'ry',
            'rz'
        ]

    def press_button(self, number):
        if number < 1 or number > 32:
            raise ValueError(f"Invalid button number {number}")
        
        self.serial.write(f"BP {number}::".encode())
        return self
    
    def release_button(self, number):
        if number < 1 or number > 32:
            raise ValueError(f"Invalid button number {number}")
        
        self.serial.write(f"BR {number}::".encode())
        return self
    
    def press_direction(self, direction):
        if direction not in self.directions:
            raise ValueError(f"Invalid direction {direction}")
        
        self.serial.write(f"HP {self.directions[direction]}::".encode())
        return self
    
    def release_direction(self, direction):
        if direction not in self.directions:
            raise ValueError(f"Invalid direction {direction}")
        
        self.serial.write(f"HR {self.directions[direction]}::".encode())
        return self
    
    def move_analog(self, axis, value):
        if axis not in self.analog:
            raise ValueError(f"Invalid axis {axis}")
        
        if value < -128 or value > 127:
            raise ValueError(f"Invalid value {value}")
        
        self.serial.write(f"{axis.upper()}S {value}::".encode())
        return self
    
    def release_analog(self, axis):
        if axis not in self.analog:
            raise ValueError(f"Invalid axis {axis}")
        
        self.serial.write(f"{axis.upper()}R::".encode())
        return self
    
    def wait(self, milliseconds):
        time.sleep(milliseconds / 1000)
        return self
