from django.core.signing import  SignatureExpired, TimestampSigner
from django.http import JsonResponse

def encryption_userid(value):
    #定义加密userid函数
    signer = TimestampSigner()
    return signer.sign(value)

def decrypt_userid(value):
    #定义解密userid函数
    signer = TimestampSigner()
    try:
        user_id = signer.unsign(value,max_age=3600)
    except SignatureExpired:
        return JsonResponse({'code':400,'errmsg':'链接已超时'})
    else:
        return user_id