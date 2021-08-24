from django.urls import converters

class UsernameConverter:
    #定义用户名路径转换器，如果验证通过则可以作为参数传递到视图，如果验证不通过返回404错误

    #定义一个regex属性用于使用匹配的正则表达式，
    # 这里表示全部小写字母和全部大写字母，0-9的数字和下划线都可匹配并且长度为5-20
    regex = '[a-zA-Z0-9-_]{5,20}'

    #将路径中的匹配的字符串转换为函数的参数
    def to_python(self,value):
        #这里不需要进行转换，如果需要整型等得容可以转换一下返回：int(value)
        return value

    '''
    def to_url(self,value):
        #转换为url需要的字符串
        return '%04d' % value   
    '''

class MobileCoverter:
    #定义用于匹配手机号的转换器

    regex = '1[345789]\d{9}'

    def to_python(self,value):
        return value

class UuidCoverter:
    #定义匹配图片验证码的uuid转换器，[\w-]+表示匹配所有字母和符号并且至少有一个
    regex = '[\w-]+'

    def to_python(self,value):
        #这里将匹配到的数据转成字符串再传递给视图作为参数，因为图片的uuid是保存再redis中的
        #而redis中是以字符串形式的数据，所以转换成字符串好比对
        return str(value)
