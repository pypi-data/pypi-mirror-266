
ERR_CODE_400 = 400
ERR_CODE_404 = 404
ERR_CODE_401 = 401
ERR_CODE_403 = 403
ERR_CODE_500 = 500
ERR_CODE_502 = 502

class Error:
    def __init__(self,errorCode, desc):
        self.error_code = errorCode
        self.error = desc