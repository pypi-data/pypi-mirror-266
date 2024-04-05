class XMLImageNameNotFoundError(Exception):
    def __init__(self, msg: str):
        self.msg: str = msg

    def __str__(self):
        return f"해당 이미지 이름으로 등록된 정보가 없습니다. : {self.msg}"
