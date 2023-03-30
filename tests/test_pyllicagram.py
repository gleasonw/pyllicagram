import pytest
from src.pyllicagram import pyllicagram

# a few basic tests
# run `python -m pytest` in the root directory of the project


def assert_float(x):
    if x != x:
        raise (ValueError("nan value in ratio"))
    assert type(x) == float
    return x


def test_pyllica_special_chars():
    with pytest.raises(ValueError):
        pyllicagram(1)
    res = pyllicagram("création")
    res["ratio"].apply(lambda x: assert_float(x))


def test_pyllica_multiple_words():
    res = pyllicagram(["création", "développement"])
    res["ratio"].apply(lambda x: assert_float(x))


def test_pyllica_sum():
    res = pyllicagram("création développement", somme=True)
    res["ratio"].apply(lambda x: assert_float(x))
    assert res["gram"][0] == "création développement"


def test_pyllica_spaces():
    """Test that spaces are correctly handled."""
    res = pyllicagram("création développement")
    res["ratio"].apply(lambda x: assert_float(x))


def test_pyllica_wide_range():
    """Test that a wide range of years works."""
    res = pyllicagram("création développement", debut=1000, fin=2000)
    res["ratio"].apply(lambda x: assert_float(x))
