
# 基类注解
def base(annotation):
    def decorator_annos(*args, **kwargs):
        # print(args,kwargs)
        def decorator(fn):
            sub_annos_name = annotation.__name__
            if fn.__annotations__.get(sub_annos_name) is None:
                # 以子类注解名作为key生成一个字典，用于区分注解
                fn.__annotations__[sub_annos_name] = {}
            # 放钩子，调用子类注解
            annotation(fn, *args, **kwargs)
            return fn
        return decorator
    return decorator_annos

@base
def annotationA(fn, *args, **kwds):
    if args != None and len(args) != 0:
        if len(args) > 1:
            raise RuntimeError("nums of @annotationA parameter can only be one! eg. @annotationA('功能A')")
        fn.__annotations__["annotationA"]["value"] = args[0]

    elif len(kwds) != 1 or (not kwds.keys().__contains__("value")):
        raise RuntimeError("If the form of @annotationA parameter is k,v \
    , then key can only be 'value' str! eg. @annotationA(value='功能A')")

    else:
        for k, v in kwds.items():
            fn.__annotations__["annotationA"][k] = v


@annotationA("this is A function")
def test_fun1():
    pass


@annotationA(value="this is A function")
def test_fun2():
    print('-------------')
"""
————————————————
版权声明：本文为CSDN博主「青春依旧_」的原创文章，遵循CC
4.0
BY - SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https: // blog.csdn.net / qq_37960007 / article / details / 115017587
"""

if __name__ == '__main__':
    #assert test_fun1.__annotations__ == test_fun2.__annotations__
    #print(test_fun1.__annotations__)
    #print(test_fun2.__annotations__)

    test_fun2()