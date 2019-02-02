

def success(data, msg=None):
    return {'status': 'success',
            'data': data,
            'message': msg,
            }

def error(msg, code=400):
    return {'status': 'error',
            'data': {
                'code': code},
            'message': msg,
            }
