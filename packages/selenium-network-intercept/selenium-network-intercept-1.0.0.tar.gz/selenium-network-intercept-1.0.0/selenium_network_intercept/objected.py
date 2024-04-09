from dataclasses import dataclass

class AttributeEmpty(Exception):...
class MethodError(Exception):...
class UrlNotFoundError(Exception):...

@dataclass
class ObjectIntercepted:
    """
    Classe para representar uma solicitação HTTP interceptada.

    Args:
        route (str): O caminho da solicitação interceptada.
        list_of_responses (list): A lista de URLs das respostas interceptadas.
        list_of_requests (list): A lista de URLs das solicitações interceptadas.

    Attributes:
        _body (list): O corpo da solicitação interceptada.
        _status_code (int): O código de status da solicitação interceptada.
        _url (str): A URL da solicitação interceptada.
        _method (str): O método HTTP da solicitação interceptada.
        _error (str): O erro da solicitação interceptada.
        route (str): O caminho da solicitação interceptada.
        list_of_responses (list): A lista de URLs das respostas interceptadas.
        list_of_requests (list): A lista de URLs das solicitações interceptadas.
    """
    
    def __init__(self,route):
        self.route = route
        self.list_of_responses = []
        self.list_of_requests = []
    
    
    def set_list_of_responses(self,url):
        if url is not None:
            self.list_of_responses.append(url)
        
    def get_list_of_responses(self):
        return self.list_of_responses.copy()
        
    def set_list_of_requests(self,url):
        if url is not None:
            self.list_of_requests.append(url)
        
    def get_list_of_requests(self):
        return self.list_of_requests.copy()
    
    
    
    _body : list = None 
    _status_code : int = None 
    _url : str = None 
    _method : str = None 
    _error : any = None
    _time : str = None 
    _query_params : dict = None 
    
    method_error = False
    is_filled = False
    has_error = False
    
    @property
    def body(self):
        if self._body is None:
            return None
        return self._body
    
    @body.setter
    def body(self,body):
        self._body = body

    @property
    def status_code(self):
        if self._status_code is None:
            return None
        return self._status_code
    
    @status_code.setter
    def status_code(self, status_code):
        self._status_code = status_code
        
    @property
    def url(self):
        if self._url is None:
            return None
        return self._url
    
    @url.setter
    def url(self, url):
        self._url = url
        
    @property
    def method(self):
        if self._method is None:
                        return None
        return self._method
    
    @method.setter
    def method(self, method):
        self._method = method

    @property
    def error(self):
        if self._error is None:
            return None
        return self._error
    
    @error.setter
    def error(self,error):
        self._error = error
    
    @property
    def time(self):
        if self._time is None:
            return None
        return self._time
    
    @time.setter
    def time(self,time):
        self._time = f"{time:.2f}"
        
    @property
    def query_params(self):
        if self._query_params is None:
            return None
        return self._query_params
    
    @query_params.setter
    def query_params(self,query_params):
        self._query_params = query_params