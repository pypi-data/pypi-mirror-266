import time
import json
from selenium_network_intercept.response import network_response
from selenium_network_intercept.request import network_request
from time import sleep
from selenium_network_intercept.objected import ObjectIntercepted


def  _get_url(params,req_or_res): #falta teste unitario
    try:
        if req_or_res == 'response':
            url = _fix_url(params.get('response').get('url'))
        else:
            url = _fix_url(params.get('request').get('url'))
        return url
    except:...
    
    
def _fix_url(url):
    """_summary_

    Args:
        url (string): URL Completa da requisição

    Returns:
        string: treated_url = URL sem parametros de busca e querys.
        string: url = URL completa da requisição.
        
        
    """
    try:
        treated_url = url.split('?')[0]
        return treated_url
    except:
        return url


def intercept_http(
    driver,
    route,
    delay=5
    ) -> ObjectIntercepted:
    
    """
    Obs:
    Recomendado não utilizar a busca pela rota no início da execução do driver, visto que para ser interceptado, é necessário que as rotas já tenham sido finalizadas.
    Intercepta solicitações HTTP feitas por um WebDriver Selenium.
    Pode ser colocado qualquer parte da URL / Rota desejada, contando que não seja parte de uma query.

    Args:
        driver: Uma instância de WebDriver Selenium.
        url_endswith (str): O sufixo da URL para combinar com as solicitações interceptadas.

    Nota:
        Esta função intercepta solicitações HTTP feitas pela instância fornecida de WebDriver. Ela busca
        solicitações cujas URLs terminam com o sufixo especificado (`url_endswith`). Não sendo necessário enviar 
        informações como query na URL, somente a rota necessária.
        Para cada solicitação interceptada, ela recupera informações relevantes, como o corpo da solicitação, 
        código de status, URL e método HTTP, e as encapsula em uma instância de ObjectIntercepted.
    """
    initial_time = time.time()
    
    logs1 = driver.get_log('performance') 
    
    sleep(delay)
    
    object_intercepted = ObjectIntercepted(route)
    
    logs2 = driver.get_log('performance')
    
    logs = logs1 + logs2
    
    
    for log in logs:
        message = json.loads(log.get('message')).get('message')
        params  = json.loads(log.get('message')).get('message').get('params')
        method  = json.loads(log.get('message')).get('message').get('method')
        response  = json.loads(log.get('message')).get('message').get('params').get('response')
        request  = json.loads(log.get('message')).get('message').get('params').get('request')

        response_url = _get_url(params,'response')
        request_url  = _get_url(params,'request')
        
        if 'Network.responseReceived' == method:
            network_response(
                driver,
                params,
                message,
                route,
                response_url,
                object_intercepted,
                response
            )
        
        
        if 'Network.requestWillBeSent' == method:
            network_request(
                params,
                message,
                route,
                request_url,
                object_intercepted,
                request
            )
        
        object_intercepted.set_list_of_responses(response_url)
        object_intercepted.set_list_of_requests(request_url)
        
    end_time = time.time()
    object_intercepted.time = end_time - initial_time
    
    return object_intercepted
