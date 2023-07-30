import io
import os
import sys
import pytest
import multiprocessing as mp
from unittest.mock import patch
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(parent_dir, 'applications/controller_app'))

from controller_app import *

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
        """Test creation of NoResi entity with a string input shorter than 4 characters, should raise ValueError."""
        with pytest.raises(ValueError):
            no_resi = NoResi("521")

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