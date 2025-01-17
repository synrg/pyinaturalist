from pyinaturalist.client import iNatClient
from pyinaturalist.constants import API_V1_BASE_URL
from pyinaturalist.models import Place
from test.sample_data import SAMPLE_DATA, j_place_1, j_place_2


def test_from_id(requests_mock):
    requests_mock.get(
        f'{API_V1_BASE_URL}/places/89191,67591',
        json={'results': [j_place_1, j_place_2], 'total_results': 2},
        status_code=200,
    )
    client = iNatClient()
    results = client.places.from_id(89191, 67591).all()
    place = results[0]

    assert len(results) == 2 and isinstance(place, Place)
    assert place.id == 89191
    assert place.name == 'Conservation Area Riversdale'
    assert place.location == (-43.3254578926, 172.2325124165)


def test_autocomplete(requests_mock):
    requests_mock.get(
        f'{API_V1_BASE_URL}/places/autocomplete',
        json=SAMPLE_DATA['get_places_autocomplete'],
        status_code=200,
    )
    client = iNatClient()
    place = client.places.autocomplete('springbok').one()

    assert place.id == 93735
    assert place.name == 'Springbok'
    assert place.bbox_area == 0.000993854049
    assert place.location == (-29.665119, 17.88583)


def test_get_places_autocomplete__all_pages(requests_mock):
    page_1 = {'total_results': 25, 'results': [{'id': i} for i in range(20)]}
    page_2 = {'total_results': 25, 'results': [{'id': i} for i in range(15, 25)]}
    requests_mock.get(
        f'{API_V1_BASE_URL}/places/autocomplete',
        [
            {'json': page_1, 'status_code': 200},
            {'json': page_2, 'status_code': 200},
        ],
    )
    client = iNatClient()
    results = client.places.autocomplete('springbok').all()

    # Expect 2 requests, and for results to be deduplicated
    assert len(results) == 25


def test_nearby(requests_mock):
    requests_mock.get(
        f'{API_V1_BASE_URL}/places/nearby',
        json=SAMPLE_DATA['get_places_nearby'],
        status_code=200,
    )
    client = iNatClient()

    results = client.places.nearby(150.0, -50.0, -149.999, -49.999).all()
    place = results[0]

    assert isinstance(place, Place)
    assert place.id == 97394
    assert place.admin_level == -1
    assert place.name == 'North America'
    assert place.category == 'standard'
    assert place.bbox_area == 28171.40875125
    assert place.location == (56.7732555574, -179.68825)
    assert place.ancestor_place_ids == []
