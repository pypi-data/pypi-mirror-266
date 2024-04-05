from typing import Dict, Any, List

from ..object.converter import CytomineAnnotationInfo, PolygonClassMatchingInfo


class FitUtil:
    @classmethod
    def parse_xml_to_cytomine_annotation_info(cls, xml_dict_data: Dict[str, Any]) -> CytomineAnnotationInfo:
        annotations_data = xml_dict_data["object-stream"]["Annotations"]
        image_name = annotations_data["@image"]
        annotation_infos = []
        if type(annotations_data["Annotation"]) == dict:
            annotation_info = annotations_data["Annotation"]
            class_name = annotation_info["@class"]
            polygon_points = [
                CytomineAnnotationInfo.AnnotationInfo.PolygonInfo(x=float(coord["@x"]), y=float(coord["@y"]))
                for coord in annotation_info["Coordinates"]["Coordinate"]
            ]
            annotation_infos.append(
                CytomineAnnotationInfo.AnnotationInfo(class_name=class_name, polygon_points=polygon_points)
            )
        else:
            for annotation_info in annotations_data["Annotation"]:
                class_name = annotation_info["@class"]
                polygon_points = [
                    CytomineAnnotationInfo.AnnotationInfo.PolygonInfo(
                        x=float(coord["@x"]), y=float(coord["@y"])
                    )
                    for coord in annotation_info["Coordinates"]["Coordinate"]
                ]
                annotation_infos.append(
                    CytomineAnnotationInfo.AnnotationInfo(
                        class_name=class_name, polygon_points=polygon_points
                    )
                )
        return CytomineAnnotationInfo(image_name=image_name, annotation_infos=annotation_infos)

    @classmethod
    def class_name_spliter(cls, class_name: str) -> List[str]:
        if "," in class_name:
            return [part.strip() for part in class_name.split(",")]
        else:
            return [class_name]

    @classmethod
    def make_polygon_info_to_cytomine_polygon_metric(
        cls,
        polygon_info: List[CytomineAnnotationInfo.AnnotationInfo.PolygonInfo],
        image_height: int,
    ) -> str:
        return "POLYGON((" + ", ".join(f"{point.x} {image_height - point.y}" for point in polygon_info) + "))"

    @classmethod
    def parse_cytomine_annotation_string_to_data_model(
        cls, polygon_info: List[PolygonClassMatchingInfo], image_name: str
    ) -> CytomineAnnotationInfo:
        cytomine_annotation_info: CytomineAnnotationInfo = CytomineAnnotationInfo(
            image_name=image_name,
            annotation_infos=[
                CytomineAnnotationInfo.AnnotationInfo(
                    class_name="ExampleClass",
                    polygon_points=[
                        CytomineAnnotationInfo.AnnotationInfo.PolygonInfo(
                            x=float(pair.split()[0]), y=float(pair.split()[1])
                        )
                        for pair in info.polygon.split("((")[1].split("))")[0].split(", ")
                    ],
                )
                for info in polygon_info
            ],
        )

        return cytomine_annotation_info
