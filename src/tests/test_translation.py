from ..translation import *
from ..translation import _translation_book
import pytest

class TestTranslation():
    """Tests for translation.py module"""

    def test_miau_to_pt_with_miau(self):
        for msg in InfoMessages:
            miau = _translation_book.inverse[msg]
            assert miau_to_pt(miau) == msg.value

        for i in range(2):
            miau = _translation_book.inverse[i]
            assert miau_to_pt(miau) == f'Preciso de mais {i} voto para pular.'
            
        for i in range(2,10):
            miau = _translation_book.inverse[i]
            assert miau_to_pt(miau) == f'Preciso de mais {i} votos para pular.'

    def test_miau_to_pt_without_miau(self):
        for msg in InfoMessages:
            with pytest.raises(TypeError):
                miau_to_pt(msg)

    def test_miau_to_pt_with_invalid_miau(self):
        not_a_miau = 'rawr'
        with pytest.raises(KeyError):
            miau_to_pt(not_a_miau)

        not_a_miau2 = 'woof'
        with pytest.raises(KeyError):
            miau_to_pt(not_a_miau2)

        not_a_miau3 = 'Oi!'
        with pytest.raises(KeyError):
            miau_to_pt(not_a_miau3)

    def test_pt_to_miau_with_pt(self):
        for msg in InfoMessages:
            miau = _translation_book.inverse[msg]
            assert pt_to_miau(msg) == miau

        for i in range(10):
            miau = _translation_book.inverse[i]
            assert pt_to_miau(i) == miau

    def test_pt_to_miau_without_pt(self):
        for msg in InfoMessages:
            miau = _translation_book.inverse[msg]
            with pytest.raises(TypeError):
                pt_to_miau(msg.value)
        
    def test_pt_to_miau_with_invalid_pt(self):
        with pytest.raises(KeyError):
            pt_to_miau(-1)

        with pytest.raises(KeyError):
            pt_to_miau(10)
