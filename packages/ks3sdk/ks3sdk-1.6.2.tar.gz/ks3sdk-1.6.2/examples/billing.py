# -*- coding: utf-8 -*-
from ks3.billing import get_buckets_data
from datetime import datetime

####################公共头#########################

# 金山云主账号 AccessKey 拥有所有API的访问权限，风险很高。强烈建议您创建并使用子账号账号进行 API 访问或日常运维，请登录 https://uc.console.ksyun.com/pro/iam/#/user/list 创建子账号。
# bucket_names 为一个或者多个 bucket 名称，逗号间隔
# start_time 和 end_time 分别为起始时间和结束时间，时间格式为%Y%m%d%H%M%S，比如202111190000
# products 指的是查询单个或者多个计费项名称，逗号间隔；比如DataSize,RequestsGet；如果不填，则查询所有计费项（除带宽，带宽需单独查询）
data = get_buckets_data('<yourAccessKeyId>', '<yourAccessKeySecret>', bucket_names="<yourBucketName1>,<yourBucketName2>", start_time="202111192300", end_time="202111192359", products="DataSize,RequestsGet")
print(data)

