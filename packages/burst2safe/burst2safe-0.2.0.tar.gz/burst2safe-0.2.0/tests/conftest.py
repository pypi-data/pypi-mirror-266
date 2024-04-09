from datetime import datetime
from pathlib import Path

import asf_search
import pytest

from burst2safe.utils import BurstInfo


TEST_DIR = Path(__file__).parent


def pytest_configure(config):
    config.addinivalue_line('filterwarnings', 'ignore::RuntimeWarning')


@pytest.fixture
def test_data_dir():
    return TEST_DIR / 'test_data'


@pytest.fixture
def test_data_xml(test_data_dir):
    return test_data_dir / 'S1A_IW_SLC__1SDV_20200604T022251_20200604T022318_032861_03CE65_7C85_VV.xml'


@pytest.fixture
def xsd_dir():
    xsd_dir = Path(__file__).parent.parent / 'src' / 'burst2safe' / 'data'
    return xsd_dir


@pytest.fixture
def search_result1():
    product = asf_search.ASFProduct()
    product.umm = {'InputGranules': ['S1A_IW_SLC__1SDV_20200604T022251_20200604T022318_032861_03CE65_7C85']}
    product.properties.update(
        {
            'fileID': 'S1_136231_IW2_20200604T022312_VV_7C85-BURST',
            'flightDirection': 'ascending',
            'polarization': 'vv',
            'orbit': 123,
            'url': 'https://example.com/foo.zip',
            'additionalUrls': ['https://example.com/foo.xml'],
            'burst': {
                'subswath': 'IW2',
                'relativeBurstID': 123456,
                'burstIndex': 7,
            },
        }
    )
    # If an ASFSearchResults object is needed, uncomment the following lines:
    # results = asf_search.ASFSearchResults([product])
    # results.searchComplete = True
    return product


@pytest.fixture
def burst_info1(test_data_xml):
    burst_info = BurstInfo(
        granule='S1_136231_IW2_20200604T022312_VV_7C85-BURST',
        slc_granule='S1A_IW_SLC__1SDV_20200604T022251_20200604T022318_032861_03CE65_7C85',
        swath='IW2',
        polarization='VV',
        burst_id=136231,
        burst_index=7,
        direction='DESCENDING',
        absolute_orbit=32861,
        date=datetime(2020, 6, 4, 2, 23, 12),
        data_url='https://sentinel1-burst.asf.alaska.edu/S1A_IW_SLC__1SDV_20200604T022251_20200604T022318_032861_03CE65_7C85/IW2/VV/7.tiff',
        data_path=Path(''),
        metadata_url='https://sentinel1-burst.asf.alaska.edu/S1A_IW_SLC__1SDV_20200604T022251_20200604T022318_032861_03CE65_7C85/IW2/VV/7.xml',
        metadata_path=test_data_xml,
        start_utc=datetime(2020, 6, 4, 2, 23, 12, 933265),
        stop_utc=datetime(2020, 6, 4, 2, 23, 16, 37825),
        length=1510,
    )
    return burst_info


@pytest.fixture
def burst_info2(test_data_xml):
    burst_info = BurstInfo(
        granule='S1_136232_IW2_20200604T022315_VV_7C85-BURST',
        slc_granule='S1A_IW_SLC__1SDV_20200604T022251_20200604T022318_032861_03CE65_7C85',
        swath='IW2',
        polarization='VV',
        burst_id=136232,
        burst_index=8,
        direction='DESCENDING',
        absolute_orbit=32861,
        date=datetime(2020, 6, 4, 2, 23, 15),
        data_url='https://sentinel1-burst.asf.alaska.edu/S1A_IW_SLC__1SDV_20200604T022251_20200604T022318_032861_03CE65_7C85/IW2/VV/8.tiff',
        data_path=Path(''),
        metadata_url='https://sentinel1-burst.asf.alaska.edu/S1A_IW_SLC__1SDV_20200604T022251_20200604T022318_032861_03CE65_7C85/IW2/VV/8.xml',
        metadata_path=test_data_xml,
        start_utc=datetime(2020, 6, 4, 2, 23, 15, 697989),
        stop_utc=datetime(2020, 6, 4, 2, 23, 18, 802549),
        length=1510,
    )
    return burst_info


@pytest.fixture
def burst_infos(burst_info1, burst_info2):
    return [burst_info1, burst_info2]
