from cytomine import Cytomine
from cytomine.models import (
    ImageInstanceCollection,
    Term,
    OntologyCollection,
    ProjectCollection,
    TermCollection,
    Annotation,
    AnnotationTerm,
    AnnotationCollection
)
from typing import List, Union, Optional
from overrides import override

from .interface.converter import CustomCytomineClientInterface
from .util.normal_util import NormalUtil
from .util.fit_util import FitUtil
from .util.custom_exception import XMLImageNameNotFoundError
from .object.converter import (
    CytomineAnnotationInfo,
    CytomineTermInfo,
    CytomineImageInfo,
    CytomineProjectInfo,
    PolygonClassMatchingInfo
)


class CustomCytomineClient(CustomCytomineClientInterface):
    def __init__(
        self,
        host: str,
        public_key: str,
        private_key: str,
        cytomine_logging: bool = True,
    ):
        self.host: str = host
        self.public_key: str = public_key
        self.private_key: str = private_key
        self.cytomine_logging: bool = cytomine_logging
        self.normal_util: NormalUtil = NormalUtil()
        self.fit_util: FitUtil = FitUtil()

    def _connect_cytomine(self) -> Cytomine:
        return Cytomine(
            host=self.host,
            public_key=self.public_key,
            private_key=self.private_key,
            configure_logging=self.cytomine_logging,
        )

    @override
    def create_term_from_xml_file(self, xml_file_path: str, ontology_name: str) -> bool:
        cytomine_metric: CytomineAnnotationInfo = self.fit_util.parse_xml_to_cytomine_annotation_info(
            xml_dict_data=self.normal_util.xml_to_dict(xml_file_path)
        )
        for term_name in cytomine_metric.annotation_infos:
            for class_name in self.fit_util.class_name_spliter(class_name=term_name.class_name):
                self._create_term_to_ontology(term_name=class_name, ontology_name=ontology_name)
        return True

    @override
    def find_terms_info_with_project_name(self, project_name: str) -> List[CytomineTermInfo]:
        with self._connect_cytomine():
            return [
                CytomineTermInfo(term_id=info.id, term_name=info.name)
                for info in TermCollection().fetch_with_filter(
                    "ontology",
                    self.find_project_info_with_name(name=project_name).ontology_id,
                )
            ]

    @override
    def save_annotation_from_xml(self, xml_path: str, project_name: str) -> bool:
        xml_data = self.normal_util.xml_to_dict(file_path=xml_path)
        file_name: str = xml_path.split("/")[-1]
        cytomine_metric: CytomineAnnotationInfo = self.fit_util.parse_xml_to_cytomine_annotation_info(
            xml_dict_data=xml_data
        )

        with self._connect_cytomine():
            try:
                image_info: CytomineImageInfo = self._find_image_info_by_name(
                    project_name, cytomine_metric.image_name
                )
            except XMLImageNameNotFoundError:
                image_info: CytomineImageInfo = self._find_image_info_by_name(project_name, file_name)

            for annotation_info in cytomine_metric.annotation_infos:
                self._save_annotation(image_info.image_id, annotation_info, project_name, image_info.height)
        return True

    @override
    def find_project_info_with_name(self, name: str) -> CytomineProjectInfo:
        with self._connect_cytomine():
            ontologies: list = OntologyCollection().fetch()
            projects: list = ProjectCollection().fetch()
            ontology_id: Optional[int] = next(
                (ontology.id for ontology in ontologies if ontology.name == name), None
            )
            project_id: Optional[int] = next(
                (project.id for project in projects if project.name == name), None
            )

            if ontology_id is None or project_id is None:
                raise Exception("해당 이름을 가진 프로젝트가 없습니다.")

            return CytomineProjectInfo(project_id=project_id, ontology_id=ontology_id)

    @override
    def save_xml_files_from_project(self, save_path: str, project_name: str) -> None:
        raise Exception("아직 미지원되는 기능입니다.")
        project_info: CytomineProjectInfo = self.find_project_info_with_name(name=project_name)
        with self._connect_cytomine():
            annotations = AnnotationCollection()
            annotations.project = project_info.project_id
            annotations.fetch()

        return None

    def _find_image_names_in_project(self, project_name: str) -> List[CytomineImageInfo]:
        with self._connect_cytomine():
            project_info: CytomineProjectInfo = self.find_project_info_with_name(name=project_name)
            images: list = ImageInstanceCollection().fetch_with_filter("project", project_info.project_id)
            return [
                CytomineImageInfo(
                    image_id=image.id,
                    image_name=image.instanceFilename,
                    height=image.height,
                )
                for image in images
            ]

    def _create_term_to_ontology(self, term_name: str, ontology_name: str) -> Union[Term, bool]:
        with self._connect_cytomine():
            term: Term = Term(
                name=term_name,
                id_ontology=self.find_project_info_with_name(name=ontology_name).ontology_id,
                color=self.normal_util.gen_random_rgb_hex(),
            ).save()
            return term

    def _attach_terms_to_annotation(self, annotation: Annotation, class_name: str, project_name: str) -> None:
        for class_name in self.fit_util.class_name_spliter(class_name=class_name):
            term_info = next(
                (
                    info
                    for info in self.find_terms_info_with_project_name(project_name=project_name)
                    if info.term_name == class_name
                ),
                None,
            )
            if term_info is not None:
                AnnotationTerm(annotation.id, term_info.term_id).save()
            else:
                term: Union[Term, bool] = self._create_term_to_ontology(
                    term_name=class_name, ontology_name=project_name
                )
                if type(term) is bool:
                    pass
                else:
                    AnnotationTerm(annotation.id, term.id).save()

    def _save_annotation(
        self,
        image_id: int,
        annotation_info: CytomineAnnotationInfo,
        project_name: str,
        image_height: int,
    ) -> Annotation:
        polygon_wkt: str = self.fit_util.make_polygon_info_to_cytomine_polygon_metric(
            polygon_info=annotation_info.polygon_points, image_height=image_height
        )
        annotation: Annotation = Annotation(location=polygon_wkt, id_image=image_id).save()
        self._attach_terms_to_annotation(annotation, annotation_info.class_name, project_name)
        return annotation

    def _find_image_info_by_name(self, project_name: str, image_name: str) -> CytomineImageInfo:
        image_infos: List[CytomineImageInfo] = self._find_image_names_in_project(project_name)
        image_info = next(
            (
                info
                for info in image_infos
                if info.image_name.rsplit(".", 1)[0] == image_name.rsplit(".", 1)[0]
            ),
            None,
        )
        if not image_info:
            raise XMLImageNameNotFoundError(msg=f"{image_name} / {image_infos}")
        return image_info
