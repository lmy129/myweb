#创建任务队列，任务队列放在本地的redis数据库中的15号库【reids总共有16个库0-15】
broker_url = "redis://127.0.0.1:6379/15"