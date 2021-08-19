from django.urls import converters

#定义路径转换器
class UsernameConverter:
    #给类定义一个regex属性，用于使用正则表达式匹配
    regex = '[a-zA-Z0-9_-]{5,20}'

    #将路径中的匹配的字符串转换为函数的参数
    def to_python(self,value):
        #这里不需要进行转换，如果需要整型等得容可以转换一下返回：int(value)
        return value
    
    #将Python类型转换为url需要的字符串
    #def to_url(self,value):
        #return '%04d' % value