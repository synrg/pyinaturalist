from datetime import datetime
from typing import Dict, List, Optional

import attr

from pyinaturalist.constants import Coordinates
from pyinaturalist.models import (
    ID,
    BaseModel,
    Photo,
    Taxon,
    User,
    cached_property,
    coordinate_pair,
    dataclass,
    datetime_attr,
    datetime_now_attr,
    kwarg,
)
from pyinaturalist.node_api import get_observation
from pyinaturalist.response_format import convert_observation_timestamp


@dataclass
class Observation(BaseModel):
    """A dataclass containing information about an observation, matching the schema of
    `GET /observations <https://api.inaturalist.org/v1/docs/#!/Observations/get_observations>`_.

    Can be constructed from either a full JSON record, a partial JSON record, or just an ID.
    """

    created_at: datetime = datetime_now_attr
    cached_votes_total: int = kwarg
    captive: bool = kwarg
    comments_count: int = kwarg
    community_taxon_id: int = kwarg
    description: str = kwarg
    faves_count: int = kwarg
    geoprivacy: str = kwarg  # Enum
    id: int = kwarg
    id_please: bool = kwarg
    identifications_count: int = kwarg
    identifications_most_agree: bool = kwarg
    identifications_most_disagree: bool = kwarg
    identifications_some_agree: bool = kwarg
    license_code: str = kwarg  # Enum
    location: Optional[Coordinates] = coordinate_pair
    map_scale: int = kwarg
    mappable: bool = kwarg
    num_identification_agreements: int = kwarg
    num_identification_disagreements: int = kwarg
    oauth_application_id: str = kwarg
    obscured: bool = kwarg
    out_of_range: bool = kwarg
    owners_identification_from_vision: bool = kwarg
    place_guess: str = kwarg
    positional_accuracy: int = kwarg
    public_positional_accuracy: int = kwarg
    quality_grade: str = kwarg  # Enum
    site_id: int = kwarg
    spam: bool = kwarg
    species_guess: str = kwarg
    observed_on: Optional[datetime] = datetime_attr
    updated_at: Optional[datetime] = datetime_attr
    uri: str = kwarg
    uuid: str = kwarg

    # Lazy-loaded nested model objects
    _identifications: List[Dict] = attr.ib(factory=list, repr=False)
    _photos: List[Dict] = attr.ib(factory=list, repr=False)
    _taxon: Dict = attr.ib(factory=dict, repr=False)
    _user: Dict = attr.ib(factory=dict, repr=False)
    _identifications_obj: List[ID] = None  # type: ignore
    _photos_obj: List[Photo] = None  # type: ignore
    _taxon_obj: Taxon = None  # type: ignore
    _user_obj: User = None  # type: ignore

    # Nested collections
    annotations: List = attr.ib(factory=list)
    comments: List = attr.ib(factory=list)
    faves: List = attr.ib(factory=list)
    flags: List = attr.ib(factory=list)
    ofvs: List = attr.ib(factory=list)
    outlinks: List = attr.ib(factory=list)
    place_ids: List = attr.ib(factory=list)
    preferences: Dict = attr.ib(factory=dict)
    project_ids: List = attr.ib(factory=list)
    project_ids_with_curator_id: List = attr.ib(factory=list)
    project_ids_without_curator_id: List = attr.ib(factory=list)
    project_observations: List = attr.ib(factory=list)
    quality_metrics: List = attr.ib(factory=list)
    reviewed_by: List = attr.ib(factory=list)
    sounds: List = attr.ib(factory=list)
    tags: List = attr.ib(factory=list)
    votes: List = attr.ib(factory=list)

    # Additional attributes from API response that are redundant here; just left here for reference
    # created_at_details: Dict = attr.ib(factory=dict)
    # created_time_zone: str = kwarg
    # geojson: Dict = attr.ib(factory=dict)
    # non_owner_ids: List = attr.ib(factory=list)
    # observation_photos: List[Photo] = attr.ib(converter=Photo.from_dict_list, factory=list)
    # time_observed_at: Optional[datetime] = datetime_attr
    # observed_on_details: Dict = attr.ib(factory=dict)
    # observed_on_string: str = kwarg
    # observed_time_zone: str = kwarg
    # time_zone_offset: str = kwarg

    # Attributes that will only be used during init and then omitted
    temp_attrs = [
        'created_at_details',
        'observed_on_string',
        'observed_time_zone',
        'time_zone_offset',
    ]

    # Convert observation timestamps prior to attrs init
    # TODO: better function signature for docs; use forge?
    def __init__(
        self,
        created_at_details: Dict = None,
        observed_on_string: str = None,
        observed_time_zone: str = None,
        time_zone_offset: str = None,
        **kwargs,
    ):
        tz_offset = time_zone_offset
        tz_name = observed_time_zone
        created_date = (created_at_details or {}).get('date')

        if not isinstance(kwargs.get('created_at'), datetime) and created_date:
            kwargs['created_at'] = convert_observation_timestamp(created_date, tz_offset, tz_name)
        if not isinstance(kwargs.get('observed_on'), datetime) and observed_on_string:
            kwargs['observed_on'] = convert_observation_timestamp(
                observed_on_string, tz_offset, tz_name, ignoretz=True
            )

        self.__attrs_init__(**kwargs)  # type: ignore

    @cached_property
    def identifications(self):
        return ID.from_json_list(self._identifications)

    @cached_property
    def photos(self):
        return Photo.from_json_list(self._photos)

    @cached_property
    def taxon(self):
        return Taxon.from_json(self._taxon)

    @cached_property
    def user(self):
        return User.from_json(self._user)

    @classmethod
    def from_id(cls, id: int):
        """Lookup and create a new Observation object from an ID"""
        json = get_observation(id)
        return cls.from_json(json)

    @property
    def thumbnail_url(self) -> Optional[str]:
        if not self.photos:
            return None
        return self.photos[0].thumbnail_url

    # TODO: Return simplified dict
    # def simplify(self) -> Dict:
    #     pass

    # TODO
    # def __str__(self) -> str:
    #     pass
