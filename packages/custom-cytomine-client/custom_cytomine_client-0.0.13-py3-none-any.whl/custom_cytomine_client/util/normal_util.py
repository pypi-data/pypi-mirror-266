import xmltodict
import random


class NormalUtil:
    @classmethod
    def xml_to_dict(cls, file_path: str) -> dict:
        with open(file_path, "r") as xml_file:
            xml_content = xml_file.read()
            dict_data = xmltodict.parse(xml_content)
            return dict_data

    @classmethod
    def gen_random_rgb_hex(cls) -> str:
        return "#{:02X}{:02X}{:02X}".format(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        )
