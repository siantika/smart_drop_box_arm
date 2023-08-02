import io
import os
import sys
import pytest
import serial
import multiprocessing as mp
from unittest.mock import patch
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(parent_dir, 'applications/controller_app'))
sys.path.append(os.path.join(parent_dir, 'applications/display_app'))

from controller_app import *
from display_app import * 

class TestEntities:
    """Test entities in the controller app class."""

    def test_should_has_correct_params(self):
        """Test if DataItem has correct parameters: no_resi, item, and date_ordered."""
        data_item = DataItem('0023', 'sepatu', '2023-07-20 22:26:40')
        assert hasattr(data_item, 'no_resi')
        assert hasattr(data_item, 'item')
        assert hasattr(data_item, 'date_ordered')

    def test_data_item_entity_with_correct_args(self):
        """Test DataItem entity creation with correct arguments."""
        data_item = DataItem('0023', 'sandal', '2023-07-20 22:26:40')
        assert data_item.no_resi == '0023'
        assert data_item.item == 'sandal'
        assert data_item.date_ordered == '2023-07-20 22:26:40'

    def test_data_item_with_entity_with_uncorrect_args(self):
        """Test DataItem entity creation with incorrect arguments, should raise ValueError."""
        with pytest.raises(TypeError):
            data_item = DataItem(2323, {'item': 'kaos kaki'}, ['2023-07-20 22:26:40'])

    def test_no_resi_entity_with_correct_args(self):
        """Test creation of NoResi entity with a 4-digit string input."""
        no_resi = NoResi('8889')
        assert no_resi.value_4_digits == '8889'

    def test_no_resi_with_non_string_args(self):
        """Test creation of NoResi entity with a non-string input, should raise TypeError."""
        with pytest.raises(TypeError):
            no_resi = NoResi(6636)

    def test_no_resi_with_more_than_4_chars(self):
        """Test creation of NoResi entity with a string input longer than 4 characters, should raise ValueError."""
        with pytest.raises(ValueError):
            no_resi = NoResi("55522223336210002312")

    def test_no_resi_with_less_than_4_chars(self):
        """Test creation of NoResi entity with a string input shorter than 4 characters, should return the same value."""
        no_resi = NoResi("521")
        assert no_resi.value_4_digits == "521"

    def test_file_photo_entity_with_correct_args(self):
        """Test creation of FilePhoto entity with correct binary data input."""
        # Example binary data (Hello World)
        binary_data = b'\x48\x65\x6c\x6c\x6f\x20\x57\x6f\x72\x6c\x64'

        # Create a binary data
        # Write binary data to the in-memory stream using BytesIO
        binary_data_read = None
        with io.BytesIO() as stream:
            stream.write(binary_data)
            stream.seek(0)  # Move the stream cursor to the beginning
            binary_data_read = stream.read()

        file_photo = FilePhoto(binary_data_read)
        assert file_photo.bin_data == binary_data

    def test_item_weight_entity_with_correct_args(self):
        """Test creation of ItemWeight entity with a correct float value input."""
        item = ItemsWeight(8.0362)
        assert item.unit_weight == 8.0362


class TestGetDataItem:
    """ Test creation for getting data item from data source"""

    def test_with_correct_queue_data(self):
        """ Should return no_resi, item, and date_odered """
        queue_data = mp.Queue(2)
        queue_data.put(
            {
                'no_resi' : '3333',
                'item' : 'Vape',
                'date_ordered' : '2023-07-20 22:26:40',
            }
        )
        #add delay for putting data in queue
        time.sleep(0.1)
        data_item = DataItemRoutines()
        data = data_item.get(queue_data)
        assert data != None
        assert data.no_resi== '3333'
        assert data.item == 'Vape'
        assert data.date_ordered == '2023-07-20 22:26:40'

    def test_with_uncorrect_queue_data(self):
        with pytest.raises(KeyError):
            """ Should raise a KeyError"""
            queue_data = mp.Queue(2)
            queue_data.put(
                {
                    'no_reddsadsi' : '3333',
                    'itedm' : 'Vape',
                    'datcce_ordered' : '2023-07-20 22:26:40',
                }
            )
            #add delay for putting data in queue
            time.sleep(0.1)
            data_item = DataItemRoutines()
            data = data_item.get(queue_data)


class TestUserNoResi:
    """ Test mechanism to get no resi """
    def help_mock(self):
        self._mock_serial = patch('serial.Serial', spec=serial.Serial).start()

    def test_determinator_with_correct_delete_no_resi_scenario(self):
        """ Test with 'D' char that inputted by user.
            It should delete the latest char.           
        """
        test_queue_data = mp.Queue(4)
        test_keypad_buffer = ['5', '6']
        _determinator = UserInputNoResi()
        _determinator._determinator(
            test_keypad_buffer,
            'D',
             test_queue_data 
        )
        # Give time for putting data in the queue
        time.sleep(0.1)
        data = test_queue_data.get_nowait()
        assert data == {
            'cmd' : DisplayMode.NORMAL,
            'payload' : ['Masukan resi:',
                         '5']
        }

    def test_determinator_with_correct_input_resi_scenario(self):
        """ Test with valid no resi inputted by user             
        """
        test_queue_data = mp.Queue(4)
        test_keypad_buffer = []
        _determinator = UserInputNoResi()
        _determinator._determinator(
            test_keypad_buffer,
            '6',
             test_queue_data 
        )
        # Give time for putting data in the queue
        time.sleep(0.1)
        data = test_queue_data.get_nowait()
        assert data == {
            'cmd' : DisplayMode.NORMAL,
            'payload' : ['Masukan resi:',
                         '6']
        }
 
    def test_get_method_with_correct_input_4_chars(self):
        """ Should return a correct number resi """
        self.help_mock()
        periph = PeripheralOperations.get_instance()
        keypad = periph.keypad
        with patch.object(keypad, 'reading_input_char', return_value='1'):
            test_display_queue = mp.Queue(4)
            data = UserInputNoResi()
            no_resi = data.get(periph, test_display_queue)
            assert no_resi.value_4_digits == '1111'
        # clean the serial pacther 
        patch.stopall()

    def test_get_method_with_empty_input_chars(self):
        """ Should return empty string """
        self.help_mock()
        periph = PeripheralOperations.get_instance()
        keypad = periph.keypad
        with patch.object(keypad, 'reading_input_char', return_value=None):
            test_display_queue = mp.Queue(4)
            data = UserInputNoResi()
            no_resi = data.get(periph, test_display_queue)
            assert no_resi.value_4_digits == ''
            # Clean the serial patcher
        patch.stopall()

    def test_get_method_with_less_than_4_input_chars(self):
        """ Should return empty string 
            Queue size affects the mock keypad sending the returns
            values. Here it specified with 3 means it send ''3 times
        """
        self.help_mock()
        periph = PeripheralOperations.get_instance()
        keypad = periph.keypad
        with patch.object(keypad, 'reading_input_char', return_value=None):
            test_display_queue = mp.Queue(3)
            data = UserInputNoResi()
            no_resi = data.get(periph, test_display_queue)
            assert no_resi.value_4_digits == ''
            # Clean the serial patcher
        patch.stopall()


class TestValidation:
    """ Test vallidation of no resi and door password """
    def test_validation_no_resi_with_exist_data(self):
        """ Returns exist data from available data stored in dict """
        test_available_data = {
            '2321' : {
                        'no_resi' : '2321',
                        'item' : 'bola',
                        'date_ordered' : '2023-07-20 22:26:40'
                     },
        }
        user_no_resi = NoResi('2321')
        validator = Validation(('door', 'password'))
        valid_no_resi = validator.validate_input(user_no_resi,
                                                    test_available_data)

        assert valid_no_resi.no_resi == '2321'
        assert valid_no_resi.item == 'bola'
        assert valid_no_resi.date_ordered == '2023-07-20 22:26:40'

    def test_validation_no_resi_with_non_exist_data(self):
        """ Returns None """
        test_available_data = {
            '2321' : {
                        'no_resi' : '2321',
                        'item' : 'bola',
                        'date_ordered' : '2023-07-20 22:26:40'
                     },
        }
        user_no_resi = NoResi('0023')
        validator = Validation(('door', 'password'))
        valid_no_resi = validator.validate_input(user_no_resi,
                                                    test_available_data)

        assert valid_no_resi == None

    def test_password_validation_with_correct_password(self):
        """ Returns 'door' """
        user_input = NoResi('BCA*')
        validator = Validation(('door', 'password'))
        assert validator.validate_input(user_input, {}) == 'door'
    
    def test_password_validation_with_uncorrect_password(self):
        """ Returns None """
        user_input = NoResi('5569')
        validator = Validation(('door', 'password'))
        assert validator.validate_input(user_input, {}) == None


class TestTakingItem:
    """ Test taking item operations """
    def help_mock(self):
        self._mock_serial = patch('serial.Serial', spec=serial.Serial).start()

    def test_with_close_the_door(self):
        """ Closed door, break immediatelly the loop,
        read the weight of items and log the success of process execution"""
        self.help_mock()
        periph = PeripheralOperations.get_instance()
        door = periph.door
        weight = periph.weight
        with patch.object(door, 'sense_door_state', return_value = False),\
            patch.object(weight, 'get_weight', return_value = 12.2),\
                patch('log.logger.info') as mock_log_info:
            weight = TakingItem.process(periph)
            mock_log_info.assert_called_once()
            assert weight.unit_weight == 12.2
        patch.stopall()

 # NOTE : performs this test manual !
    # def test_with_door_always_open(self):
    #     """ Plays the warning sound """
    #     self.help_mock()
    #     periph = PeripheralOperations.get_instance()
    #     door = periph.door
    #     with patch.object(door, 'sense_door_state', return_value = True):
    #         TakingItem.process(periph)
    #     patch.stopall()


class TestTakingPhoto:
    """ Test taking photo operation """
    def help_mock(self):
        self._mock_serial = patch('serial.Serial', spec=serial.Serial).start()

    def test_with_correct_photo(self):
        """ Capturing directly from development 
            camera """
        self.help_mock()
        taking_photo = TakingPhoto()
        periph = PeripheralOperations.get_instance()
        # clean old photos
        all_photos = periph.camera.get_all_photos_file_name()
        if len(all_photos) > 0:
            periph.camera.delete_all_photos()
            
        photo = taking_photo.process(periph)
        #open the same photo and read it as binary data
        expected_bin_data = None
        file_name = periph.camera.get_all_photos_file_name()[0]
        full_path = os.path.join(parent_dir, './assets/photos/', file_name)
        with open(full_path, 'rb') as f:
            expected_bin_data = f.read()
        assert photo.bin_data == expected_bin_data
        # Clean all resources 
        patch.stopall()
        periph.camera.delete_all_photos()


class TestReceivingItem:
    """ Test receiving-item operations. There are
    3 conditions should be tested.
        1. If door is closed and no change in item weight, it will play 
            "No item stored" sound.
        2. If door position is open exceeding door timeout, It will play
            alert sound until door is closed.
        3. If door position close and there is change in item weight, it will
            play " Item successfully stored " and return success operation 
    """
    def _mock_resources(self):
        self.mock_serial = patch('serial.Serial', spec=serial.Serial).start()
        self.periph = PeripheralOperations.get_instance()
        door = self.periph.door
        weight = self.periph.weight
        
        self.mock_door_sense = patch.object(door, 'sense_door_state').start()
        self.mock_get_weight = patch.object(weight, 'get_weight').start()
        self.mock_door_unlock = patch.object(door, 'unlock').start()
        self.mock_door_lock = patch.object(door, 'lock').start()

    def test_with_condition_1(self):
        """ Should performs 'no received item' process """
        self._mock_resources()
        self.mock_door_sense.return_value = False
        self.mock_get_weight.return_value = 12.0
        test_item = ItemsWeight(12.0)
        test_queue_to_disp = mp.Queue(2)
        rec_item = ReceivingItem()
        new_item = rec_item.process(self.periph, test_item, test_queue_to_disp
                         )
        self.mock_door_unlock.assert_called()
        data_sent_to_disp = test_queue_to_disp.get_nowait()
        assert data_sent_to_disp == LcdData.NO_ITEM_RECEIVED
        assert new_item.unit_weight == 12.0 
        #clear resoureces 
        patch.stopall()

    # NOTE: Performs the test manually 
    # def test_with_condition_2(self):
    #     """ Should performs 'alert' process """
    #     self._mock_resources()
    #     self.mock_door_sense.return_value = True
    #     self.mock_get_weight.return_value = 12.0
    #     test_item = ItemsWeight(12.0)
    #     test_queue_to_disp = mp.Queue(2)
    #     rec_item = ReceivingItem()
    #     rec_item.process(self.periph, test_item, test_queue_to_disp
    #                      )
    #     #clear resourcess 
    #     patch.stopall()

    def test_with_condition_3(self):
        """ Should performs 'item stored ' process """
        self._mock_resources()
        self.mock_door_sense.return_value = False
        self.mock_get_weight.return_value = 22.0
        test_item = ItemsWeight(12.0)
        test_queue_to_disp = mp.Queue(2)
        rec_item = ReceivingItem()
        new_item = rec_item.process(self.periph, test_item, test_queue_to_disp
                         )
        self.mock_door_unlock.assert_called()
        data_sent_to_disp = test_queue_to_disp.get_nowait()
        assert data_sent_to_disp == LcdData.ITEM_RECEIVED
        assert new_item.unit_weight == 22.0
        #clear resoureces 
        patch.stopall()
        

class TestProcessingData:
    """ Test processing data operations """
    def test_with_correct_queue_data(self):
        """ queue data to data-access should be match,
            queue data size is not full  """
        queue_data_to_data_access = mp.Queue(5)
        test_target_data_item = DataItem('5569', 'sepatu', 
                                         '2023-07-20 22:26:40')
        # Create mock for binary data
        binary_data = b'\x48\x65\x6c\x6c\x6f\x20\x57\x6f\x72\x6c\x64'
        # Create a binary data
        # Write binary data to the in-memory stream using BytesIO
        binary_data_read = None
        with io.BytesIO() as stream:
            stream.write(binary_data)
            stream.seek(0)  # Move the stream cursor to the beginning
            binary_data_read = stream.read()

        processing_data = ProcessingData()
        processing_data.process(queue_data_to_data_access, 
                                test_target_data_item,
                                binary_data_read)
        
        # assert the delete.php endpoint
        assert queue_data_to_data_access.get_nowait() == {
            'endpoint' : 'delete.php',
            'data' : {'no_resi': '5569'},
            'http_header' : {'content-type' : 'application/json'},
            }

        # assert the success_item.php endpoint
        assert queue_data_to_data_access.get_nowait() == {
            'endpoint' : 'success_item.php',
            'data' : {'no_resi': '5569', 
                      'item' : 'sepatu', 
                      'date_ordered' : '2023-07-20 22:26:40'
                      },
            'http_header' : {'content-type' : 'application/json'},
            'file' : binary_data_read
            }


class TestNotify:
    """ Test notify operations. It implements Telegram app """
    def test_telegram_notif_with_correct_data(self):
        """ 'Telegram send notification' method invoked
              once with corrects params """
                # Create mock for binary data
        binary_data = b'\x48\x65\x6c\x6c\x6f\x20\x57\x6f\x72\x6c\x64'
        # Create a binary data
        # Write binary data to the in-memory stream using BytesIO
        binary_data_read = None
        with io.BytesIO() as stream:
            stream.write(binary_data)
            stream.seek(0)  # Move the stream cursor to the beginning
            binary_data_read = stream.read()
        
        test_photo = FilePhoto(binary_data_read)
        test_target_data_item = DataItem('0030', 'rokok', '2023-07-20 22:26:40')
        with patch.object(TelegramApp, 'send_notification', return_value = 1) as mock_notify:
            Notify.send_telegram_notification(test_target_data_item,
                                              test_photo)
            mock_notify.assert_called_once_with(
                {'no_resi':'0030', 'item' : 'rokok'},
                test_photo.bin_data
            )


class TestRegister:
    """ Test the registration of device to server 
        test the success and the fail processes.
       """

    def test_with_valid_serial_number(self):
        with patch.object(HttpDataAccess,'post') as mock_post:
            test_response =(200, {
                'api_key' : 'asdasdsad55325asd44d',
                'owner' : 'Sian ajus',
                'date_registered' : '20:00:00 1/08/2023'
            })
            mock_post.return_value = test_response
            register = Registration()
            result = register.register_device()
            mock_post.assert_called_once()
            assert os.environ['API_KEY'] == test_response[1]['api_key']
            assert os.environ['OWNER'] == test_response[1]['owner']
            assert result == True
            # Clear environments vars
            del os.environ['API_KEY']
            del os.environ['OWNER']

    def test_with_invalid_invalid_serial_number(self):
        with patch.object(HttpDataAccess,'post') as mock_post:
            test_response =(403, {'message' : 'Access forbiden '})
            mock_post.return_value = test_response
            register = Registration()
            result = register.register_device()
            mock_post.assert_called_once()
            assert 'API_KEY' not in os.environ.keys()
            assert 'OWNER' not in os.environ.keys()
            assert result == False


class TestSecurity:
    """ Test security methods """
    def help_mock(self):
        self._mock_serial = patch('serial.Serial', spec=serial.Serial).start()

    def test_with_door_state_is_open(self):
        self.help_mock()
        periph = PeripheralOperations.get_instance()
        door = periph.door
        with patch.object(door, 'sense_door_state') as mock_door:
            mock_door.return_value = 1
            sec = Security()
            sec.run()
            # give time for the sound to play
            time.sleep(0.5)
            assert sec._has_alert == True
            # Clear the resources
            sec._periph.sound.stop(sec._sound_alert)
            patch.stopall()

    def test_with_door_state_is_close(self):
        self.help_mock()
        periph = PeripheralOperations.get_instance()
        door = periph.door
        with patch.object(door, 'sense_door_state') as mock_door:
            mock_door.return_value = 0
            sec = Security()
            sec.run()
            # give time for the sound to play
            time.sleep(0.5)
            assert sec._has_alert == False
            assert sec._security_flag == 0
            assert sec._sound_alert == None
            patch.stopall()

    def test_with_door_open_then_close_the_door(self):
        self.help_mock()
        periph = PeripheralOperations.get_instance()
        door = periph.door
        with patch.object(door, 'sense_door_state') as mock_door:
            mock_door.return_value = 1
            sec = Security()
            sec.run()
            # give time for the sound to play
            time.sleep(1.0)
            sec.run()
            mock_door.return_value = 0
            # give time for prcocessing the door state
            time.sleep(1.0)
            assert not sec._sound_alert.is_alive()
            patch.stopall()