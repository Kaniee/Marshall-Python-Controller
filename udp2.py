import socket

class MarshallConnection():
    _msg_counter = 0
    _msg_prefix = b'\x01\x00'

    def __init__(self, udp_ip='192.168.102.34', udp_port=52381):
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
    def _cmd_size_bytes(msg) -> bytes:
        return len(msg).to_bytes(2, 'big')

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
    def _zoom_speed_bytes(zoom_speed) -> bytes:
        if zoom_speed == 0:
            return b'\x00'
        if zoom_speed > 0:
            return bytes.fromhex('2' + str(zoom_speed - 1))
        if zoom_speed < 0:
            return bytes.fromhex('3' + str(-zoom_speed - 1))

    @staticmethod
    def _preset_bytes(action, preset_number):
        preset_block = int(preset_number // 128)
        action_byte = bytes.fromhex(str(preset_block) + str(action))
        return action_byte + (preset_number % 128).to_bytes(1, 'big')

    def _built_msg(self, cmd) -> bytes:
        msg = self._msg_prefix + self._cmd_size_bytes(cmd) + self._msg_number_bytes() + cmd
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
        
        cmd = b'\x81\x01\x04\x07' + self._zoom_speed_bytes(zoom_speed) + b'\xFF'
        # print(cmd)
        self.send_cmd(cmd)

    def stop(self):
        self.stop_move()
        self.stop_zoom()

    def stop_move(self):
        self.move(pan_speed=0, tilt_speed=0)

    def stop_zoom(self):
        self.zoom(zoom_speed=0)
        
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
