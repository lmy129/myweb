'''
生产者消费者设计模式
生产者产生任务【客户端访问产生任务】-----任务队列【将客户端产生的任务放在任务队列里；这里redis充当任务队列角色】-------接收任务队列的任务进行执行
这里后端服务器充当消费者角色
异步方案
使用celery搭配redis进行实现【主流是使用celery搭配RabbitMQ实现】
'''

import os
from celery import Celery

#为celery的运行设置django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings')

#创建celery实例,这里的main参数是给这个实例设置一个名字；到这里celery实例就已经有了
app = Celery(main='celery_tasks')

#设置broker
app.config_from_object('celery_tasks.config')

#让celery自动检测指定包的任务,autodiscover_tasks的参数是一个列表
#如果有多个包任务，在列表中添加tasks的路径,这里如果不写参数celery就会自动去子应用里去搜索tasks文件
app.autodiscover_tasks(['celery_tasks.sms'])

'''
完成之后需要执行【celery -A celery_tasks.main worker -l INFO】来启动消费者，也就是执行任务者来执行任务
'''