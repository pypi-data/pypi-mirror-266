import json
from selenium_network_intercept.objected import ObjectIntercepted


def network_response(
    driver,
    params,
    message,
    route,
    url,
    object_intercepted : ObjectIntercepted,
    response,
    ): 
        # if 'route or url complete' in url:
        #     print('Debug') #Only to debug
    try:
        if route in url:
            try:                
                body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': params['requestId']})
                try:
                    if body['body'] == '':
                        object_intercepted.body = 'Sem conteúdo no body da requisição'
                    else:
                        body_decoded = json.loads(body['body'])
                        object_intercepted.body = body_decoded
                except json.decoder.JSONDecodeError:
                    object_intercepted.body = body['body']        
            except (KeyError,Exception) as error: object_intercepted.has_error = error


            try:
                object_intercepted.status_code = response['status']
            except KeyError as error: object_intercepted.has_error = error
            
            try: 
                object_intercepted.url = response['url']
            except KeyError as error: object_intercepted.has_error = error

            
    except:
        object_intercepted.error = {
            'erro': object_intercepted.has_error,
            'resposta' : 'Parâmetro não encontrado',
            'url': url,
            }
