import pytest
from lstpressure.utils import normalize_coordinates


@pytest.mark.parametrize(
    "latitude, longitude, expected_latitude, expected_longitude",
    [
        ("-30:42:39.8", "21:26:38.0", -30.711055555555554, 21.44388888888889),
        (-30.711055555555554, 21.44388888888889, -30.711055555555554, 21.44388888888889),
    ],
)
def test_normalize_coordinates(latitude, longitude, expected_latitude, expected_longitude):
    lat, long = normalize_coordinates(latitude, longitude)
    assert lat == expected_latitude
    assert long == expected_longitude


def test_normalize_coordinates_mixed_format():
    lat = ["-30:42:39.8", -30.711055555555554]
    long = ["21:26:38.0", 21.44388888888889]

    # Should not be possible to use both DEC and DMS
    with pytest.raises(ValueError):
        normalize_coordinates(lat[0], long[1])
    with pytest.raises(ValueError):
        normalize_coordinates(lat[1], long[0])
