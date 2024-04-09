import json
from selenium_network_intercept.objected import MethodError
from selenium_network_intercept.objected import ObjectIntercepted


def network_request(
    params,
    message,
    route,
    url,
    object_intercepted : ObjectIntercepted,
    request
):
    if object_intercepted.method is None:
        object_intercepted.is_filled = False
    
    try:
        if route in url and not object_intercepted.is_filled:      
            try:
                if params.get('loaderId') and request.get('method') not in (None,'OPTIONS') :
                    object_intercepted.method = request['method']
                    object_intercepted.is_filled = True
            except KeyError as error: method_error = error
            
            try:
                object_intercepted.method = params['headers'][':method']
                object_intercepted.is_filled = True
            except KeyError as error: method_error = error
                
            try:
                object_intercepted.method = params['headers']['method']
                object_intercepted.is_filled = True
            except KeyError as error: method_error = error

            try:
                URL = params['request']['url']
                object_intercepted.query_params = {'url': URL} 
                querys = URL.split('?')[1].split('&')
                object_intercepted.query_params = {'querys': querys}
            except IndexError as error: method_error = error
            
            if object_intercepted.is_filled:
                return 'Método já preenchido'
        
        elif object_intercepted.is_filled:
            return 'Método já preenchido'
        else:
            raise MethodError(f'Rota: {route} não foi encontrada na última URL: {url}, verifique a lista de responses se está retornando a URL desejada.')
        
    except MethodError as error:
        method_error = error
        if method_error and not object_intercepted.is_filled:
            object_intercepted.method = {
                'resposta' : 'Parâmetro method não encontrado',
                'erro': method_error,
                'url': url,
                }
