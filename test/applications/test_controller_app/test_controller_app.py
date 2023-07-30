import os
import sys
import pytest
import multiprocessing as mp
from unittest.mock import patch
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(os.path.join(parent_dir, 'applications/controller_app'))

from controller_app import *

class TestEntities:
    """ Test entities in controller app class """

    def test_should_has_correct_params(self):
        """ Params: no_resi, item, and date_ordered """
        data_item = DataItem('0023', 'sepatu', '2023-07-20 22:26:40')
        assert hasattr(data_item, 'no_resi')
        assert hasattr(data_item, 'item')
        assert hasattr(data_item, 'date_ordered')

    def test_data_item_entity_with_correct_args(self):
        """ Should contain no_resi, item and date_ordered """
        data_item = DataItem('0023', 'sandal', '2023-07-20 22:26:40')
        assert data_item.no_resi is '0023'
        assert data_item.item is 'sandal'
        assert data_item.date_ordered is '2023-07-20 22:26:40'

    def test_data_item_with_entity_with_uncorrect_args(self):
        """ Should raise Value Error """
        with pytest.raises(TypeError):
            data_item = DataItem(2323, {'item' : 'kaos kaki'} , 
                                 ['2023-07-20 22:26:40'])

    def test_no_resi_entity_with_correct_args(self):
        """ Test with 4 digits resi in string.
            should return correctly ( no resi inputted)
        """
        no_resi = NoResi('8889')
        assert no_resi.value_4_digits == '8889'

    def test_no_resi_with_non_string_args(self):
        """
            Expect:
                raise an type error.

        """
        with pytest.raises(TypeError):
            no_resi = NoResi(6636)