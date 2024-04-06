from cores.model.request import RequestObjModel
from cores.const.api import RequestConst


class Request(object):
    def __init__(self, token: str, content_type: str, method: str, body: dict | str = None, files: list = None):
        """
        Initialize the Request object.s

        Args:
            token (str): The authentication token.
            content_type (str): The content type of the request.
            method (str): The HTTP method of the request (e.g., GET, POST).
            body (dict, optional): The body of the request.
            files (list, optional): List of files to attach.
        """
        self._token = token or str()
        self._content_type = content_type
        self._header = {'Content-Type': self._content_type,
                        'Authorization': f'Bearer {self._token}'}
        self._method = method
        self._body = body
        self._files = files
        self._request_object = RequestObjModel(
            header=self._header, method=self._method, body=self._body, files=self._files)

    def request_generate(self) -> RequestObjModel:
        """
            Generate the request object.

            Returns:
                RequestObjModel: The generated request object.
        """
        return self._request_object


class GetRequest(Request):
    """Class for generating GET request objects."""

    def __init__(self, token: str, content_type: str):
        """
        Initialize the GetRequest object.

        Args:
            token (str): The authentication token.
            content_type (str): The content type of the request.
        """
        super().__init__(token, content_type, method=RequestConst.Method.GET)
        self.request_generate = RequestObjModel(
            **dict(header=self._header, method=self._method))


class PostRequest(Request):
    """Class for generating POST request objects."""

    def __init__(self, token: str, content_type: str, body: dict):
        """
        Initialize the PostRequest object.

        Args:
            token (str): The authentication token.
            content_type (str): The content type of the request.
            body (dict): The body of the request.
        """
        super().__init__(token, content_type, method=RequestConst.Method.POST, body=body)
        self.request_generate = RequestObjModel(**dict(header=self._header,
                                                body=self._body,
                                                method=self._method))


class PutRequest(Request):
    """Class for generating PUT request objects."""

    def __init__(self, token: str, content_type: str, body: dict):
        """
        Initialize the PutRequest object.

        Args:
            token (str): The authentication token.
            content_type (str): The content type of the request.
            body (dict): The body of the request.
        """
        super().__init__(token, content_type, method=RequestConst.Method.PUT, body=body)
        self.request_generate = RequestObjModel(**dict(header=self._header,
                                                body=self._body,
                                                method=self._method))


class PatchRequest(Request):
    """Class for generating PATCH request objects."""

    def __init__(self, token: str, content_type: str, body: dict):
        """
        Initialize the PatchRequest object.

        Args:
            token (str): The authentication token.
            content_type (str): The content type of the request.
            body (dict): The body of the request.
        """
        super().__init__(token, content_type, method=RequestConst.Method.PATCH, body=body)
        self.request_generate = RequestObjModel(**dict(header=self._header,
                                                body=self._body,
                                                method=self._method))


class AttachRequest(Request):
    """Class for generating ATTACH request objects."""

    def __init__(self, token: str, content_type: str, body: dict, file_name: str = '', file_location: str = ''):
        """
        Initialize the AttachRequest object.

        Args:
            token (str): The authentication token.
            content_type (str): The content type of the request.
            body (dict): The body of the request.
            file_name (str, optional): The name of the file to attach.
            file_location (str, optional): The location of the file to attach.
        """
        super().__init__(token, content_type, method=RequestConst.Method.ATTACH, body=body)
        self._request_object.files = [
            ('my_file', (file_name, open(file_location, 'rb')))]
        self.request_generate = RequestObjModel(**dict(header=self._header,
                                                       body=self._body,
                                                       files=self._request_object,
                                                       method=self._method))
