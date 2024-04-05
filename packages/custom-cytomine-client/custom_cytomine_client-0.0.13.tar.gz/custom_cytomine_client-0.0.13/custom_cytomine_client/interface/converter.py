from abc import ABCMeta, abstractmethod
from typing import List

from ..object.converter import CytomineProjectInfo, CytomineTermInfo


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

    @abstractmethod
    def save_xml_files_from_project(self, save_path: str, project_name: str) -> None:
        pass
