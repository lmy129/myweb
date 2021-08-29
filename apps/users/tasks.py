from celery_tasks.main import app
from django.core.mail import send_mail

@app.task
def celery_send_email(username,token,email):
    subject = '主题'

    html_message = '<p>尊敬的用户:%s您好</p>'\
        '<p>感谢您使用美多商城。</p>'\
        '<p>您的邮箱为%s，请点击此链接激活您的邮箱</p>'\
        "<a>href='http://www.meiduo.site:8000/activation_emails/?token=%s'</a>" % (username,token,email)
        

    from_email = '1292689898@qq.com'

    recipient_list = [email]

    send_mail(subject=subject,
    message="",
    from_email=from_email,
    recipient_list=recipient_list,
    html_message=html_message)