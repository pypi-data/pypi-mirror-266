import uuid


class ApiInfo:
    def __init__(self,path,method,scope=None):
        self.path=path
        self.method=method.upper()
        self.scope=scope
        suid = str(uuid.uuid4())
        self.uid= ''.join(suid.split("-"))

    def createApiEntry(self,prefix):
        api_prefix = '{}.http.routers.{}'.format(prefix, self.uid)
        if self.scope is not None:
            tags=[]
            tags.append("{}.rule=Path(`{}`) && Method(`{}`)".format(api_prefix, self.path, self.method))
            if self.scope is not None and '' != self.scope:
                tags.append("{}.metadata.nezha.scopes={}".format(api_prefix,self.scope))
                tags.append("{}.middlewares=nezha@internal`)".format(api_prefix))
                return tags
            else:
                return []



    @staticmethod
    def parseApiController(file):
        #ToDo: 读取fast api 中controller，解析得到ApiInfo的集合
        pass

class ResourcAPIPath:
    def __init__(self):
        self.paths={}

    def path(self,path:str):
        def wrapper(cls):
            print(cls)

        return wrapper

class RestfulAPI:
    def __init__(self):
        self.apis={}

    def api(self, path:str,**kwds):
        def decorate(fn):
            method=None
            for item in kwds.items():
                key = item[0]
                value = item[1]
                http_path=path #('%s%s' % (self.root_path,'' if path is None else path))
                http_scope=None
                if key == 'scope':
                    http_scope = value
                elif key == 'method':
                    method = value
            http_method = fn.__name__ if method is None else method

            cls_name_index=fn.__qualname__.index(".")
            cls_name=fn.__qualname__[:cls_name_index]
            self.add_api(cls_name,http_path,http_method,http_scope)

            print('======fun.path==== %s' % http_path)
            return fn
        return decorate

    def add_api(self,cls_name,http_path,http_method,http_scope):
        api_info=ApiInfo(http_path,http_method,http_scope)
        if cls_name not in self.apis.keys():
            self.apis[cls_name]=[]
        self.apis[cls_name].append(api_info)



api = RestfulAPI()
paths=ResourcAPIPath()

#@ResourcAPIPath.path('/api/demo')
class demo:
    @api.api(method='GET', path='demo1/{id}', scope='a:b:c')
    def get(self):
        print('yes')

    @api.api(path='demo1', scope='a:b:d')
    def post(self):
        print('yes')

#@ResourcAPIPath.path('/api/demo1')
class demo2:
    @api.api(method='GET', path='demo2/{id}', scope='a:b:c')
    def get(self):
        print('yes')

    @api.api(path='demo/2', scope='a:b:d')
    def post(self):
        print('yes')
if __name__ == '__main__':
    print(api)
    print('-------')

