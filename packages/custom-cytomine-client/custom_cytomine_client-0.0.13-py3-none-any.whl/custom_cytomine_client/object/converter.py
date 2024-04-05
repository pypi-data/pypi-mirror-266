from typing import List
from pydantic import BaseModel


class CytomineAnnotationInfo(BaseModel):
    image_name: str

    class AnnotationInfo(BaseModel):
        class_name: str

        class PolygonInfo(BaseModel):
            x: float
            y: float

        polygon_points: List[PolygonInfo]

    annotation_infos: List[AnnotationInfo]


class CytomineTermInfo(BaseModel):
    term_name: str
    term_id: int


class CytomineImageInfo(BaseModel):
    image_name: str
    image_id: int
    height: int


class CytomineProjectInfo(BaseModel):
    project_id: int
    ontology_id: int


class PolygonClassMatchingInfo(BaseModel):
    class_name: str
    polygon: str
