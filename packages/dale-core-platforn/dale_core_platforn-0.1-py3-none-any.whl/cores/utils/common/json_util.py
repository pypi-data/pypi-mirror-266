import json


class ObjConverter:
    def __init__(self, data):
        self.__dict__.update(data)

    def to_json(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4))


class JsonConverterUtil:

    @staticmethod
    def convert_string_to_json(string: str):
        if string:
            return json.loads(string)
        else:
            return None

    @staticmethod
    def read_json_file(file: str):
        f = open(file)
        return json.load(f)
   
    @staticmethod
    def convert_json_to_object(data: dict) -> object:
        if data:
            return json.loads(json.dumps(data), object_hook=ObjConverter)
        else:
            return None
