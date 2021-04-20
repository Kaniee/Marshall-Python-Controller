import socket

class MarshallConnection():
    _msg_counter = 0
    _msg_prefix = b'\x01\x00\x00\x09'

    def __init__(self, udp_ip, udp_port=52381):
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.sock = socket.socket(socket.AF_INET, # Internet
                                  socket.SOCK_DGRAM) # UDP

    def _get_msg_number(self) -> int:
        self._msg_counter += 1
        return self._msg_counter
    
    def _msg_number_bytes(self) -> bytes:
        return self._get_msg_number().to_bytes(4, 'big')
   
    @staticmethod
    def _speed_bytes(speed) -> bytes:
        return speed.to_bytes(1, 'big')

    @staticmethod
    def _dir_bytes(speed) -> bytes:
        if speed == 0:
            return b'\x03'
        if speed > 0:
            return b'\x01'
        if speed < 0:
            return b'\x02'

    @staticmethod
    def _zoom_focus_speed_bytes(speed) -> bytes:
        if speed == 0:
            return b'\x00'
        if speed > 0:
            return bytes.fromhex('2' + str(speed - 1))
        if speed < 0:
            return bytes.fromhex('3' + str(-speed - 1))

    @staticmethod
    def _shutter_iris_direction_bytes(direction) -> bytes:
        if direction == 0:
            return b'\x00'
        if direction == 1:
            return b'\x02'
        if direction == -1:
            return b'\x03'

    @staticmethod
    def _preset_bytes(action, preset_number):
        preset_block = int(preset_number // 128)
        action_byte = bytes.fromhex(str(preset_block) + str(action))
        return action_byte + (preset_number % 128).to_bytes(1, 'big')

    def _built_msg(self, cmd) -> bytes:
        msg = self._msg_prefix + self._msg_number_bytes() + cmd
        return msg
    
    def move(self, pan_speed=0, tilt_speed=0):
        for speed, axis in zip((pan_speed, tilt_speed), ('pan', 'tilt')):
            if not isinstance(speed, int):
                raise TypeError(f'{axis.capitalize()} speed must be a interger value')
            if abs(speed) > 0x18:
                raise ValueError(f'Absolute {axis} speed can not exceed {0x18}')
        
        cmd = b'\x81\x01\x06\x01' + self._speed_bytes(abs(pan_speed)) + self._speed_bytes(abs(tilt_speed)) + self._dir_bytes(-pan_speed) + self._dir_bytes(tilt_speed) +  b'\xFF'
        self.send_cmd(cmd)    

    def zoom(self, zoom_speed):
        if not isinstance(zoom_speed, int):
            raise TypeError('Zoom speed must be a interger value')
        if abs(zoom_speed) > 8:
            raise ValueError('Absolute zoom speed can not exceed 8')
        
        cmd = b'\x81\x01\x04\x07' + self._zoom_focus_speed_bytes(zoom_speed) + b'\xFF'
        self.send_cmd(cmd)


    def focus(self, focus_speed):
        if not isinstance(focus_speed, int):
            raise TypeError('Focus speed must be a interger value')
        if abs(focus_speed) > 8:
            raise ValueError('Absolute focus speed can not exceed 8')
        
        cmd = b'\x81\x01\x04\x08' + self._zoom_focus_speed_bytes(focus_speed) + b'\xFF'
        self.send_cmd(cmd)

    def shutter(self, direction):
        if not isinstance(direction, int):
            raise TypeError('Shutter direction must be a interger value')
        if abs(direction) > 1:
            raise ValueError('Shutter direction must be one of {-1, 0, 1}')
        
        cmd = b'\x81\x01\x04\x0A' + self._shutter_iris_direction_bytes(direction) + b'\xFF'
        self.send_cmd(cmd)

    def iris(self, direction):
        if not isinstance(direction, int):
            raise TypeError('Iris direction must be a interger value')
        if abs(direction) > 1:
            raise ValueError('Iris direction must be one of {-1, 0, 1}')
        
        cmd = b'\x81\x01\x04\x0B' + self._shutter_iris_direction_bytes(direction) + b'\xFF'
        self.send_cmd(cmd)

    def gain(self, direction):
        if not isinstance(direction, int):
            raise TypeError('Gain direction must be a interger value')
        if abs(direction) > 1:
            raise ValueError('Gain direction must be one of {-1, 0, 1}')
        
        cmd = b'\x81\x01\x04\x0C' + self._shutter_iris_direction_bytes(direction) + b'\xFF'
        self.send_cmd(cmd)
    
    def automatic_exposure_mode(self, shutter_auto=True, iris_auto=True):
        if shutter_auto and iris_auto:
            mode_bytes = b'\x00'
        else:
            if shutter_auto:
                mode_bytes = b'\x0B'
            elif iris_auto:
                mode_bytes = b'\x0A'
            else:
                mode_bytes = b'\x03'
        cmd = b'\x81\x01\x04\x39' + mode_bytes + b'\xFF'
        self.send_cmd(cmd)

    def auto_focus_toggle(self):
        cmd = b'\x81\x01\x04\x38\x10\xFF'
        self.send_cmd(cmd)

    def auto_focus_on(self):
        cmd = b'\x81\x01\x04\x38\x02\xFF'
        self.send_cmd(cmd)

    def auto_focus_off(self):
        cmd = b'\x81\x01\x04\x38\x03\xFF'
        self.send_cmd(cmd)


    def stop(self):
        self.stop_move()
        self.stop_zoom()
        self.stop_focus()

    def stop_move(self):
        self.move(pan_speed=0, tilt_speed=0)

    def stop_zoom(self):
        self.zoom(zoom_speed=0)

    def stop_focus(self):
        self.focus(focus_speed=0)

    def reset_preset(self, preset_number):
        self._use_preset(0, preset_number)

    def set_preset(self, preset_number):
        self._use_preset(1, preset_number)
        
    def recall_preset(self, preset_number):
        self._use_preset(2, preset_number)

    def _use_preset(self, action, preset_number):
        if not isinstance(preset_number, int):
            raise TypeError('preset number must be a interger value')
        if preset_number < 0 or preset_number > 255:
            raise ValueError('preset number must be between 0 and 255')

        cmd = b'\x81\x01\x04\x3F' + self._preset_bytes(action=action, preset_number=preset_number) + b'\xFF'
        self.send_cmd(cmd)

    def power_on(self):
        cmd = b'\x81\x01\x04\x00\x02\xFF'
        self.send_cmd(cmd)

    def power_off(self):
        cmd = b'\x81\x01\x04\x00\x03\xFF'
        self.send_cmd(cmd)

    def send_cmd(self, cmd):
        msg = self._built_msg(cmd)
        # print('Message: ' + msg.hex())
        self.sock.sendto(msg, (self.udp_ip, self.udp_port))
