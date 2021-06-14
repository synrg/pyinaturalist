from datetime import date, datetime
from typing import List, Union

from attr import field

from pyinaturalist.models import (
    BaseModel,
    LazyProperty,
    Taxon,
    User,
    datetime_now_attr,
    define_model,
    kwarg,
)
from pyinaturalist.response_format import safe_split, try_int_or_float

# Mappings from observation field value datatypes to python datatypes
OFV_DATATYPES = {
    'dna': str,
    'date': date,
    'datetime': datetime,
    'numeric': try_int_or_float,
    'taxon': int,
    'text': str,
    'time': str,
}
OFVValue = Union[date, datetime, float, int, str]


@define_model
class ObservationField(BaseModel):
    """A dataclass containing information about an observation field **definition**, matching the schema of
    `GET /observation_fields <https://www.inaturalist.org/pages/api+reference#get-observation_fields>`_.
    """

    allowed_values: List[str] = field(converter=safe_split, factory=list)
    created_at: datetime = datetime_now_attr
    datatype: str = kwarg  # Enum
    description: str = kwarg
    id: int = kwarg
    name: str = kwarg
    updated_at: datetime = datetime_now_attr
    user_id: int = kwarg
    users_count: int = kwarg
    uuid: str = kwarg
    values_count: int = kwarg

    def __str__(self) -> str:
        description = ': {self.description}' if self.description else ''
        return f'[{self.id}] {self.name} ({self.datatype}){description}'


@define_model
class ObservationFieldValue(BaseModel):
    """A dataclass containing information about an observation field **value**, matching the schema of ``ofvs``
    from `GET /observations <https://api.inaturalist.org/v1/docs/#!/Observations/get_observations>`_.
    """

    datatype: str = kwarg  # Enum
    field_id: int = kwarg
    id: int = kwarg
    name: str = kwarg
    taxon_id: int = kwarg
    user_id: int = kwarg
    uuid: str = kwarg
    value: OFVValue = kwarg

    # Lazy-loaded nested model objects
    taxon: property = LazyProperty(Taxon.from_json)
    user: property = LazyProperty(User.from_json)

    # Unused attrbiutes
    # name_ci: str = kwarg
    # value_ci: int = kwarg

    # Convert value by datatype
    def __attrs_post_init__(self):
        if self.datatype in OFV_DATATYPES and self.value is not None:
            converter = OFV_DATATYPES[self.datatype]
            self.value = converter(self.value)

    def __str__(self) -> str:
        return f'{self.name}: {self.value}'
