
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
        self.status= errorCode

class APIError(Exception):
    def __init__(self, errCode, errorInfo):
        self.errorinfo = errorInfo
        self.errorCode = errCode
        self.status = errCode

    def __str__(self):
        return '{}(ErrCode={})'.format(self.errorinfo, str(self.errorCode))

class ErrorCodeException(APIError):
    def __init__(self, errCode, errorInfo):
        super().__init__(errCode,errorInfo)

    def __str__(self):
        return 'ErrCode: {}, {}'.format(self.errorinfo, str(self.errorCode))