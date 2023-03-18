import sys
from unittest.mock import patch
sys.path.append('drivers/keypad')
sys.path.append('drivers/hx711')
sys.path.append('drivers/door')
sys.path.append('drivers/usb_camera')
sys.path.append('applications/peripheral_operations')
sys.path.append('drivers/sound')

from keypad import Keypad
from door import Door
from hx711 import Hx711
from usb_camera import UsbCamera
from peripheral_operations import PeripheralOperations
from sound import Sound


class TestPeriphInit:
    def test_keypad_should_be_init_correctly(self):
        periph = PeripheralOperations()

        assert periph.pin_row_keypad == ''
        assert periph.pin_col_keypad == ''
        assert periph.pin_dout_weight == ''
        assert periph.pin_sck_weight == ''
        assert periph.pin_door_lock == ''
        assert periph.pin_door_sense == ''
        assert periph.dir_saved_photo == ''
        assert periph.hw_addr_usb_camera == ''
        
        assert periph.keypad == None
        assert periph.weight == None
        assert periph.door   == None
        assert periph.camera == None


    def test_set_dir_camera_should_be_correct(self):
        periph = PeripheralOperations()
        periph._set_dir_saved_photo()
        
        assert periph.dir_saved_photo == './assets/photos/'


    def test_set_hw_usb_camera_should_be_correct(self):
        periph = PeripheralOperations()
        periph._set_hw_usb_camera()

        assert periph.hw_addr_usb_camera == '/dev/video0'


    def test_set_pin_keypad_should_be_correct(self):
        PIN_ROW_KEYPAD = [2,3,4,6]
        PIN_COL_KEYPAD = [8,11,12,14]
        periph = PeripheralOperations()

        periph._set_keypad_pins(PIN_ROW_KEYPAD, PIN_COL_KEYPAD)

        assert periph.pin_row_keypad == PIN_ROW_KEYPAD
        assert periph.pin_col_keypad == PIN_COL_KEYPAD


    def test_set_pin_weight_should_be_correct(self):
        PIN_PD_OUT = 9
        PIN_SCK = 10
        periph = PeripheralOperations()

        periph._set_weight_pins(PIN_PD_OUT, PIN_SCK)

        assert periph.pin_dout_weight== PIN_PD_OUT
        assert periph.pin_sck_weight == PIN_SCK


    def test_set_pin_door_should_be_correct(self):
        PIN_DOOR_LOCK = 4
        PIN_DOOR_SENSE = 5

        periph = PeripheralOperations()

        periph._set_door_pins(PIN_DOOR_LOCK, PIN_DOOR_SENSE)

        assert periph.pin_door_lock == PIN_DOOR_LOCK
        assert periph.pin_door_sense == PIN_DOOR_SENSE

    
    # integration tests
    def test_set_pins_all_periphs_should_be_correct(self):
         
        periph = PeripheralOperations()

        periph.set_all_pins_periphs()

        assert periph.pin_row_keypad == [2,3,4,6]
        assert periph.pin_col_keypad == [8,11,12,14]
        assert periph.pin_dout_weight == 9
        assert periph.pin_sck_weight == 10
        assert periph.pin_door_lock == 7
        assert periph.pin_door_sense == 5
        

    def test_init_periph_should_be_initiates_all_periphs(self):
        periph = PeripheralOperations()
        periph.init_all()

        assert isinstance(periph.keypad, Keypad)
        assert isinstance(periph.weight, Hx711)
        assert isinstance(periph.door, Door)
        assert isinstance(periph.camera, UsbCamera)

        assert periph.dir_saved_photo == './assets/photos/'

    

class TestKeypadoperations:
    def _help_init_periph(self):

        self.periph = PeripheralOperations()
        self.periph.set_all_pins_periphs()
        self.periph.init_all()


    def test_read_input_keypad_should_invoked_correctly(self):
        with patch.object(Keypad, 'reading_input_char') as \
            mock_keypad_reading:

            self._help_init_periph()
            self.periph.read_input_keypad()

            mock_keypad_reading.assert_called_once()


    def test_read_input_keypad_should_return_correctly(self):
        with patch.object(Keypad, 'reading_input_char') as \
            mock_keypad_reading:
            mock_keypad_reading.return_value = '5'
            self._help_init_periph()
            ret_char = self.periph.read_input_keypad()

            assert ret_char == '5'


class TestCameraOperations:
    def _help_init_periph(self):
        self.periph = PeripheralOperations()
        self.periph.set_all_pins_periphs()
        self.periph.init_all()


    def test_capture_photo_should_invoked_correctly(self):
        self._help_init_periph()
        with patch.object(UsbCamera, 'capture_photo') as mock_capture:
            self.periph.capture_photo()

            mock_capture.assert_called_once()


    def test_delete_capture_photo_should_invoked_correctly(self):
        self._help_init_periph()
        with patch.object(UsbCamera, 'delete_all_photos_in_folder') as mock_delete:
            self.periph.delete_photo()

            mock_delete.assert_called_once()



class TestDoorOpeartions:
    def _help_init_periph(self):
        self.periph = PeripheralOperations()

        self.periph.set_all_pins_periphs()

        self.periph.init_all()


    def test_lock_door_should_invoked_correctly(self):
        self._help_init_periph()
        with patch.object(Door, 'lock_door') as \
            mock_door_lock:

            self._help_init_periph()
            self.periph.lock_door()

            mock_door_lock.assert_called()
            ## we called lock_door() in init so,
            # it counts twice with this invoking


    def test_unlock_door_should_invoked_correctly(self):
        self._help_init_periph()
        with patch.object(Door, 'unlock_door') as \
            mock_unlock_door:

            self._help_init_periph()
            self.periph.unlock_door()

            mock_unlock_door.assert_called()
            ## we called lock_door() in init so,
            # it counts twice with this invoking


    def test_sense_door_should_return_correctly(self):
        self._help_init_periph()
        with patch.object(Door, 'sense_door_state') as \
            mock_sense_door:

            mock_sense_door.return_value = 1

            self._help_init_periph()
            ret_sense = self.periph.sense_door()

            mock_sense_door.assert_called()  
            assert ret_sense == 1


class TestWeightSensorOperations:
    def _help_init_periph(self):
            self.periph = PeripheralOperations()
            self.periph.set_all_pins_periphs()
            self.periph.init_all()


    def test_weight_should_invoke_init_correctly(self):
        self._help_init_periph()

        TEST_REF = 92

        with patch.object(Hx711, 'set_reading_format') as mock_set_form,\
          patch.object(Hx711, 'set_reference_unit') as mock_set_ref, \
            patch.object(Hx711, 'reset') as mock_reset, \
              patch.object(Hx711, 'tare') as mock_tare :
            
            self.periph.init_weight()

            mock_set_form.assert_called_once_with("MSB", "MSB")
            mock_set_ref.assert_called_once_with(TEST_REF)
            mock_reset.assert_called_once()
            mock_tare.assert_called_once()

    
    def test_weight_should_return_weight_value_correctly(self):
        self._help_init_periph()

        with patch.object(Hx711, 'get_weight') as mock_get_weight:
            mock_get_weight.return_value = 20
            ret_weight = self.periph.get_weight()

        mock_get_weight.assert_called_once()
        assert ret_weight == 20


    def test_weight_should_be_able_to_power_down_mode(self):
        self._help_init_periph()
        with patch.object(Hx711, 'power_down') as mock_power_down:
            self.periph.set_power_down_weight()

        mock_power_down.assert_called_once()
       

    def test_weight_should_be_able_to_power_up_mode(self):
        self._help_init_periph()
        with patch.object(Hx711, 'power_up') as mock_power_up:
            self.periph.set_power_up_weight()

        mock_power_up.assert_called_once()


class TestSoundOperations:

    def _help_init_periph(self):
        self.periph = PeripheralOperations()
        self.periph.set_all_pins_periphs()
        self.periph.init_all()


    def test_sound_should_initial_correctly(self):
        self._help_init_periph()
        
        assert isinstance(self.periph.sound, Sound)
        assert self.periph.sound_files_dir == './assets/sounds'
        

