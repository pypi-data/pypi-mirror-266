from typing import List
from pydantic import BaseModel
from abc import ABCMeta, abstractmethod


class CustomCytomineClientInterface(metaclass=ABCMeta):
    @abstractmethod
    def save_annotation_from_xml(self, xml_path: str, project_name: str) -> bool:
        pass

    @abstractmethod
    def create_term_from_xml_file(self, xml_file_path: str, ontology_name: str) -> bool:
        pass

    @abstractmethod
    def find_project_info_with_name(self, name: str) -> CytomineProjectInfo:
        pass

    @abstractmethod
    def find_terms_info_with_project_name(self, project_name: str) -> List[CytomineTermInfo]:
        pass


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
