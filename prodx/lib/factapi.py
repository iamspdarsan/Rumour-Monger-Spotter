import json

import requests as req


def factApi(query):
    parameters={
        'key':'',
        'query':query,
        'languageCode':'en-US',
        'pageSize':1000,
    }
    response = req.get('https://factchecktools.googleapis.com/v1alpha1/claims:search',params=parameters)
    #print("status code",response.status_code)
    claims=json.loads(response.content.decode('utf-8'))['claims']
    print(f'\n\n{len(claims)} claims are available')
    return claims