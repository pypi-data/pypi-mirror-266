import json
from io import BytesIO
from io import StringIO
from pathlib import Path
from uuid import uuid4

import asdf
import numpy as np
import pytest
from astropy.io import fits
from astropy.io.fits import CompImageHDU
from astropy.io.fits import HDUList
from astropy.io.fits import Header
from astropy.io.fits import PrimaryHDU

from dkist_processing_common.codecs.asdf import asdf_decoder
from dkist_processing_common.codecs.asdf import asdf_encoder
from dkist_processing_common.codecs.bytes import bytes_decoder
from dkist_processing_common.codecs.bytes import bytes_encoder
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdu_decoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.codecs.iobase import iobase_decoder
from dkist_processing_common.codecs.iobase import iobase_encoder
from dkist_processing_common.codecs.json import json_decoder
from dkist_processing_common.codecs.json import json_encoder
from dkist_processing_common.codecs.str import str_decoder
from dkist_processing_common.codecs.str import str_encoder
from dkist_processing_common.models.fits_access import FitsAccessBase


@pytest.fixture
def tmp_file(tmp_path):
    return tmp_path / uuid4().hex[:6]


@pytest.fixture
def bytes_object() -> bytes:
    return b"123"


@pytest.fixture
def path_to_bytes(bytes_object, tmp_file) -> Path:
    with open(tmp_file, "wb") as f:
        f.write(bytes_object)

    return tmp_file


@pytest.fixture
def bytesIO_object() -> BytesIO:
    return BytesIO(b"123")


@pytest.fixture(params=[0, 1])
def bytesIO_object_with_varied_pointer_position(request) -> BytesIO:
    seek_position = request.param
    result = BytesIO(b"123")
    result.seek(seek_position)
    return result


@pytest.fixture
def path_to_bytesIO(bytesIO_object, tmp_file) -> Path:
    with open(tmp_file, "wb") as f:
        f.write(bytesIO_object.read())

    return tmp_file


@pytest.fixture
def ndarray_object() -> np.ndarray:
    return np.array([1, 2, 3.0])


@pytest.fixture
def array_3d() -> np.ndarray:
    return np.random.random((1, 4, 5))


@pytest.fixture
def array_4d() -> np.ndarray:
    return np.random.random((1, 2, 3, 4))


@pytest.fixture
def fits_header() -> Header:
    return Header({"foo": "bar"})


@pytest.fixture
def primary_hdu_list(ndarray_object, fits_header) -> HDUList:
    return fits.HDUList([PrimaryHDU(data=ndarray_object, header=fits_header)])


@pytest.fixture
def path_to_primary_fits_file(primary_hdu_list, tmp_file) -> Path:
    primary_hdu_list.writeto(tmp_file)
    return tmp_file


@pytest.fixture
def path_to_3d_fits_file(array_3d, tmp_path) -> Path:
    tmp_file = tmp_path / "3D"
    hdul = fits.HDUList([PrimaryHDU(data=array_3d)])
    hdul.writeto(tmp_file)
    return tmp_file


@pytest.fixture
def path_to_4d_fits_file(array_4d, tmp_path) -> Path:
    tmp_file = tmp_path / "4D"
    hdul = fits.HDUList([PrimaryHDU(data=array_4d)])
    hdul.writeto(tmp_file)
    return tmp_file


@pytest.fixture
def compressed_hdu_list(ndarray_object, fits_header) -> HDUList:
    return fits.HDUList([PrimaryHDU(), CompImageHDU(data=ndarray_object, header=fits_header)])


@pytest.fixture
def path_to_compressed_fits_file(compressed_hdu_list, tmp_file) -> Path:
    compressed_hdu_list.writeto(tmp_file)
    return tmp_file


@pytest.fixture
def dictionary() -> dict:
    return {"foo": 123}


@pytest.fixture
def path_to_json(dictionary, tmp_file) -> Path:
    with open(tmp_file, "w") as f:
        json.dump(dictionary, f)

    return tmp_file


@pytest.fixture
def string() -> str:
    return "foo"


@pytest.fixture
def path_to_str(string, tmp_file) -> Path:
    with open(tmp_file, "w") as f:
        f.write(string)

    return tmp_file


@pytest.fixture
def asdf_tree() -> dict:
    return {"metadata_value": "something", "data": np.empty((100, 100))}


@pytest.fixture
def path_to_asdf_file(asdf_tree, tmp_file) -> Path:
    asdf_obj = asdf.AsdfFile(asdf_tree)
    asdf_obj.write_to(tmp_file)

    return tmp_file


class DummyFitsAccess(FitsAccessBase):
    def __init__(
        self,
        hdu: fits.ImageHDU | fits.PrimaryHDU | fits.CompImageHDU,
        name: str | None = None,
        auto_squeeze: bool = False,
    ):
        super().__init__(hdu=hdu, name=name, auto_squeeze=auto_squeeze)
        self.foo = self.header["foo"]


@pytest.mark.parametrize(
    "data_fixture_name, encoder_function",
    [
        pytest.param("bytes_object", bytes_encoder, id="bytes"),
        pytest.param("bytesIO_object", iobase_encoder, id="BytesIO"),
        pytest.param("ndarray_object", fits_array_encoder, id="fits ndarray"),
        pytest.param("primary_hdu_list", fits_hdulist_encoder, id="fits uncompressed HDUList"),
        pytest.param("compressed_hdu_list", fits_hdulist_encoder, id="fits compressed HDUList"),
        pytest.param("dictionary", json_encoder, id="json"),
        pytest.param("string", str_encoder, id="str"),
        pytest.param("asdf_tree", asdf_encoder, id="asdf"),
    ],
)
def test_encoder(data_fixture_name, encoder_function, request):
    """
    Given: Data of a type supported by the codecs
    When: Encoding data with the correct codec
    Then: A `bytes` object is returned
    """
    data = request.getfixturevalue(data_fixture_name)
    assert type(encoder_function(data)) is bytes


def test_iobase_encoder(bytesIO_object_with_varied_pointer_position):
    """
    Given: BytesIO object at any position in the buffer
    When: Encoding data with the iobase_encoder
    Then: A `bytes` object is returned with *all* of the buffered data
    """
    data = bytesIO_object_with_varied_pointer_position
    actual_encoded_data = iobase_encoder(data)
    data.seek(0)
    expected_encoded_data = data.read()
    assert actual_encoded_data == expected_encoded_data


def test_non_bytes_IOBase_encoder():
    """
    Given: String data in a StringIO object
    When: Trying to encode with the iobase_encoder
    Then: An error is raised
    """
    io_obj = StringIO()
    io_obj.write("foo")
    io_obj.seek(0)
    with pytest.raises(ValueError, match="produces str data"):
        iobase_encoder(io_obj)


@pytest.mark.parametrize(
    "header_func", [pytest.param(fits.Header, id="Header"), pytest.param(dict, id="dict")]
)
def test_fits_array_encoder_header_preserved(ndarray_object, header_func):
    """
    Given: A numpy array and a header as either a dict or `Header`
    When: Encoding the data and header with the `fits_array_encoder`
    Then: The data and header are preserved
    """
    raw_header = {"KEY1": "VALUE1"}
    header = header_func(raw_header)
    encoded_data = fits_array_encoder(data=ndarray_object, header=header)
    bytes_reader = BytesIO(encoded_data)
    hdul = fits.open(bytes_reader)

    assert len(hdul) == 1
    np.testing.assert_equal(hdul[0].data, ndarray_object)
    assert hdul[0].header["KEY1"] == "VALUE1"


@pytest.mark.parametrize(
    "data_fixture_name, path_fixture_name, decoder_function",
    [
        pytest.param("bytes_object", "path_to_bytes", bytes_decoder, id="bytes"),
        pytest.param("dictionary", "path_to_json", json_decoder, id="json"),
        pytest.param("string", "path_to_str", str_decoder, id="str"),
    ],
)
def test_simple_decoder(data_fixture_name, path_fixture_name, decoder_function, request):
    # This test is for values that can be compared with a simple `==`
    """
    Given: A path to a file containing data of a given type
    When: Decoding the path
    Then: The correct value and type is returned
    """
    expected = request.getfixturevalue(data_fixture_name)
    file_path = request.getfixturevalue(path_fixture_name)

    decoded_value = decoder_function(file_path)
    assert expected == decoded_value


def test_bytesio_decoder(bytesIO_object, path_to_bytesIO):
    """
    Given: Path to a file containing binary data
    When: Decoding the file with the iobase_decoder
    Then: The correct data and type are returned
    """
    decoded_object = iobase_decoder(path_to_bytesIO, io_class=BytesIO)

    bytesIO_object.seek(0)
    assert decoded_object.read() == bytesIO_object.read()


@pytest.mark.parametrize(
    "path_fixture_name",
    [
        pytest.param("path_to_primary_fits_file", id="uncompressed"),
        pytest.param("path_to_compressed_fits_file", id="compressed"),
    ],
)
def test_fits_hdu_decoder(path_fixture_name, ndarray_object, fits_header, request):
    """
    Given: Path to a FITS file
    When: Decoding the path with the fits_hdu_decoder
    Then: The correct data are returned
    """
    file_path = request.getfixturevalue(path_fixture_name)
    hdu = fits_hdu_decoder(file_path)

    assert np.array_equal(hdu.data, ndarray_object)
    assert hdu.header["foo"] == fits_header["foo"]


@pytest.mark.parametrize(
    "path_fixture_name",
    [
        pytest.param("path_to_primary_fits_file", id="uncompressed"),
        pytest.param("path_to_compressed_fits_file", id="compressed"),
    ],
)
def test_fits_access_decoder(path_fixture_name, ndarray_object, fits_header, request):
    """
    Given: Path to a FITS file
    When: Decoding the path with the fits_access_decoder
    Then: The correct data are returned
    """
    file_path = request.getfixturevalue(path_fixture_name)

    fits_obj = fits_access_decoder(file_path, fits_access_class=DummyFitsAccess)
    assert fits_obj.name == str(file_path)
    assert np.array_equal(fits_obj.data, ndarray_object)
    assert fits_obj.foo == fits_header["foo"]


def test_fits_array_decoder(path_to_primary_fits_file, ndarray_object):
    """
    Given: Path to a FITS file
    When: Decoding the path the fits_array_decoder
    Then: The correct data are returned
    """
    array = fits_array_decoder(path_to_primary_fits_file)
    assert np.array_equal(ndarray_object, array)


def test_fits_array_decoder_autosqueeze(
    path_to_3d_fits_file, path_to_4d_fits_file, array_3d, array_4d
):
    """
    Given: Path to a FITS file with a dummy 3rd axis
    When: Decoding the path with the fits_array_decoder
    Then: The auto_squeeze kwarg correctly squeezes dummy dimensions
    """
    non_squeezed_array = fits_array_decoder(path_to_3d_fits_file, auto_squeeze=False)
    assert np.array_equal(non_squeezed_array, array_3d)

    not_dummy_array = fits_array_decoder(path_to_4d_fits_file, auto_squeeze=True)
    assert np.array_equal(not_dummy_array, array_4d)

    squeezed_array = fits_array_decoder(path_to_3d_fits_file, auto_squeeze=True)
    assert np.array_equal(squeezed_array, array_3d[0])


def test_asdf_decoder(path_to_asdf_file, asdf_tree):
    """
    Given: Path to an ASDF file
    When: Decoding the path with the asdf_decoder
    Then: The correct data are returned
    """
    tree = asdf_decoder(path_to_asdf_file)
    for k, v in asdf_tree.items():
        np.testing.assert_equal(tree[k], v)  # Works for non-array objects, too
