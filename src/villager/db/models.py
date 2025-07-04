from peewee import Model, CharField, IntegerField, AutoField, Select, FloatField
from .database import db
from abc import abstractmethod
from ..types import Country, Subdivision, Locality
from typing import TypeVar, Generic

T = TypeVar("T")


class DTOModel(Generic[T]):
    def to_dto(self) -> T:
        raise NotImplementedError

    @classmethod
    def select(cls, *fields) -> Select:
        return super().select(*fields)

    @classmethod
    def to_dtos(cls) -> list[T]:
        return [row.to_dto() for row in cls.select().iterator()]


class BaseModel(Model):
    class Meta:
        database = db


class CountryModel(BaseModel, DTOModel[Country]):
    id = AutoField()
    name = CharField(index=True)
    alpha2 = CharField(unique=True, max_length=2)
    alpha3 = CharField(unique=True, max_length=3)
    numeric = IntegerField(unique=True)
    long_name = CharField()

    def to_dto(self):
        return Country(
            self.name,
            self.alpha2,
            self.alpha3,
            self.numeric,
            self.long_name,
        )

    class Meta:
        table_name = "countries"


class SubdivisionModel(BaseModel, DTOModel[Subdivision]):
    id = AutoField()
    name = CharField(index=True)
    alt_name = CharField(index=True)
    iso_code = CharField(unique=True)
    code = CharField(index=True)
    type = CharField()
    country = CharField(index=True)
    country_code = CharField(index=True)
    country_alpha3 = CharField(index=True)

    def to_dto(self):
        return Subdivision(
            self.name,
            self.alt_name,
            self.iso_code,
            self.code,
            self.type,
            self.country,
            self.country_code,
            self.country_alpha3,
        )

    class Meta:
        table_name = "subdivisions"


class LocalityModel(BaseModel, DTOModel[Locality]):
    id = AutoField()
    name = CharField(index=True)
    display_name = CharField(index=True)
    admin1 = CharField(index=True)
    admin1_iso_code = CharField(index=True)
    admin1_code = CharField(index=True, null=True)
    country = CharField(index=True)
    country_alpha2 = CharField(index=True)
    country_alpha3 = CharField(index=True)
    lat = FloatField()
    lng = FloatField()
    classification = CharField()
    osm_type = CharField()
    osm_id = IntegerField()
    population = IntegerField(null=True)

    def to_dto(self):
        return Locality(
            self.name,
            self.display_name,
            self.admin1,
            self.admin1_iso_code,
            self.admin1_code,
            self.country,
            self.country_alpha2,
            self.country_alpha3,
            self.lat,
            self.lng,
            self.classification,
            self.osm_type,
            self.osm_id,
            self.population,
        )

    class Meta:
        table_name = "localities"
