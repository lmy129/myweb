#创建生产者，这里创建的是发送短信的生产任务
#如果需要创建其他生产任务，可以在对应的子应用文件夹下创建一个tasks来定义
from libs.yuntongxun.sms import CCP
#每个生产者函数都需要用celery实例的task方法来装饰，所以这里导入了celery的实例对象app
from celery_tasks.main import app

@app.task
def celery_send_sms_code(mobile,code):
    #这里5代表短信里提示5分钟内验证码有效，1代表使用的模板编号
    CCP().send_template_sms(mobile,[code,5],1)