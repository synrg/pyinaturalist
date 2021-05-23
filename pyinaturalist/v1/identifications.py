from pyinaturalist import api_docs as docs
from pyinaturalist.constants import JsonResponse, MultiInt
from pyinaturalist.forge_utils import document_request_params
from pyinaturalist.pagination import add_paginate_all
from pyinaturalist.request_params import translate_rank_range
from pyinaturalist.response_format import convert_all_timestamps
from pyinaturalist.v1 import get_v1


def get_identifications_by_id(identification_id: MultiInt, user_agent: str = None) -> JsonResponse:
    """Get one or more identification records by ID.

    **API reference:** https://api.inaturalist.org/v1/docs/#!/Identifications/get_identifications_id

    Example:

        >>> get_identifications_by_id(155554373)

        .. admonition:: Example Response
            :class: toggle

            .. literalinclude:: ../sample_data/get_identifications.py

    Args:
        identification_id: Get taxa with this ID. Multiple values are allowed.

    Returns:
        Response dict containing identification records
    """
    r = get_v1('identifications', ids=identification_id, user_agent=user_agent)
    r.raise_for_status()

    identifications = r.json()
    identifications['results'] = convert_all_timestamps(identifications['results'])
    return identifications


@document_request_params([docs._identification_params, docs._pagination, docs._only_id])
@add_paginate_all(method='page')
def get_identifications(**params) -> JsonResponse:
    """Search identifications.

    **API reference:** https://api.inaturalist.org/v1/docs/#!/Identifications/get_identifications

    Example:

        Get all of your own species-level identifications:

        >>> response = get_identifications(user_login='my_username', rank='species')
        >>> print([f"{i['user']['login']}: {i['taxon_id']} ({i['category']})" for i in response['results']])
        [155043569] Species: 76465 (leading) added on 2021-02-15 10:46:27-06:00 by jkcook
        [153668189] Species: 76465 (supporting) added on 2021-02-06 17:43:37+00:00 by jkcook
        [147500725] Species: 1163860 (improving) added on 2020-12-24 23:52:30+00:00 by jkcook
        ...

        .. admonition:: Example Response
            :class: toggle

            .. literalinclude:: ../sample_data/get_identifications.py

    Returns:
        Response dict containing identification records
    """
    params = translate_rank_range(params)
    r = get_v1('identifications', params=params)
    r.raise_for_status()

    identifications = r.json()
    identifications['results'] = convert_all_timestamps(identifications['results'])
    return identifications