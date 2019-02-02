
def error(msg, code=400):
    return {'error': {
                'code': code,
                'message': msg,
            }}
