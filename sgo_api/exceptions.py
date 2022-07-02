class SgoError(Exception):
    pass


class SchoolNotFoundError(SgoError):
    def __init__(self, url: str, school_id: str):
        self.url = url
        self.school_id = school_id

    def __str__(self):
        return f"В версии СГО {self.url} не обнаружено ОУ с id = {self.school_id}"
