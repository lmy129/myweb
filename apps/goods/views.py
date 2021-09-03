from django.shortcuts import render
#导入Fdfs_client类用于创建实例上传文件，另外导入get_tracker_conf方法用于处理配置文件路径
from fdfs_client.client import Fdfs_client,get_tracker_conf

# Create your views here.
tracker_path = get_tracker_conf('utils/fastdfs/client.conf')

client = Fdfs_client(tracker_path)

client.upload_by_filename('/home/liumengyan/pkq.jpg')
