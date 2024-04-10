from pyrecipes.utils.text import clean_text, extract_leading_numbers, text_border


def test_clean_text():
    text = "01_this_is_a_test"
    assert clean_text(text) == "1) This is a test"


def test_extract_leading_number():
    text = "02_this_is_another_test"
    assert extract_leading_numbers(text) == 2


def test_assert_text_border():
    text = "testing"
    assert text_border(text) == "===========\n= testing =\n==========="
    assert (
        text_border(text, symbol="+", side_symbol="|", padding=3)
        == "+++++++++++++++\n|   testing   |\n+++++++++++++++"
    )
