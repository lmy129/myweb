from celery_tasks.main import app
from django.core.mail import send_mail

@app.task
def celery_send_email(token,email):
    subject = '主题'

    html_message = "点击按钮激活邮箱<a href='http://www.meiduo.site:8000/activation_emails/?token=%s'>激活</a>" % token

    from_email = '1292689898@qq.com'

    recipient_list = [email]

    send_mail(subject=subject,
    message="",
    from_email=from_email,
    recipient_list=recipient_list,
    html_message=html_message)