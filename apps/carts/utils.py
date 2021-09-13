'''
合并购物车数据，以cookie数据为主
'''
import pickle
import base64
from django_redis import get_redis_connection
def merge_cookie_to_redis(request,response):
    user = request.user
    #读取cookie数据然后更新到redis中
    carts = request.COOKIES.get('carts')
    #判断购物车中有没有数据
    if carts != None:
        #对cookie中的购物车数据进行解密
        carts = pickle.loads(base64.b64decode(carts))

        #初始化存放数据的容器
        #存放购物车中的商品ID和数量数据
        cookie_dict = {}
        #存放选中数据
        selected_ids = []
        #存放未选中数据
        unselected_ids = []

        #遍历解码后的cookie数据
        for sku_id,count_selected_dict in carts.items():
            cookie_dict[sku_id] = count_selected_dict['count']
            if count_selected_dict['selected']:
                selected_ids.append[sku_id]
            else:
                unselected_ids.append[sku_id]
        
        #将数据添加到redis中
        redis_cli = get_redis_connection('carts')
        #创建管道
        pipeline = redis_cli.pipeline()
        #将字典数据添加到redis中,hmset可以使用字典添加数据【key,dict】形式
        pipeline.hmset('carts_%s' % user.id,cookie_dict)
        #将选中商品数据添加到redis中
        if len(selected_ids) > 0:
            #*list代表解包，将列表中的所有数据解包后添加到redis中
            pipeline.sadd('selected_%s' % user.id,*selected_ids)
        if len(unselected_ids) > 0:
            pipeline.srem('selected_%s' % user.id,*unselected_ids)

        #将cookie中的购物车数据删除
        response.delete_cookie('carts')
        #将拿到的修改后的响应，返回回去
        return response



        
