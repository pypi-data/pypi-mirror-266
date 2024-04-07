# -*- coding: utf-8 -*-

import os
import parser
import time
from datetime import datetime

import requests

from ks3.connection import Connection
from ks3.exception import S3ResponseError
from ks3.key import Key
from ks3.objectTagging import Tag
from ks3.xmlParsers.bucketCors import BucketCors, CORSRule
from ks3.xmlParsers.bucketCrossReplicate import BucketCrossReplicate
from ks3.xmlParsers.bucketLifecycle import BucketLifecycle, Rule as LifecycleRule, Filter as LifecycleFilter, \
  Expiration as LifecycleExpiration, Transition as LifecycleTransition, AbortIncompleteMultipartUpload
from ks3.xmlParsers.bucketLogging import BucketLogging
# 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
# 通过环境变量获取，或者把诸如“<你的AccessKeyId>”替换成真实的AccessKeyId等。
from ks3.xmlParsers.bucketMirror import BucketMirror, AsyncMirrorRule, SyncMirrorRules, MirrorRequestSetting, \
  HeaderSetting
from ks3.xmlParsers.bucketRetention import BucketRetention, Rule as RetentionRule
from base64 import urlsafe_b64encode
import asyncio

ak = os.getenv('KS3_IAM_ACCESS_KEY_ID', '<YOUR_ACCESS_KEY>')
sk = os.getenv('KS3_IAM_ACCESS_KEY_SECRET', '<YOUR_SECRET_KEY>')
bucket_name = os.getenv('KS3_BUCKET', '<KS3_TEST_BUCKET>')
endpoint = 'ks3-cn-beijing.ksyuncs.com' #os.getenv('KS3_TEST_ENDPOINT', 'ks3-cn-shanghai-internal.ksyuncs.com')

conn = Connection(ak, sk, host=endpoint, port=80, ua_addon='test-ua/1') #port=8091,
key_name = 'test_key'


def getAllBuckets(project_ids=None):
  buckets = conn.get_all_buckets(project_ids=project_ids) #
  for b in buckets:
    print(b.name, b.region, b.Region, b.creation_date)

def headBucket(bucket_name):
  # 如果正常返回，则Bucket存在；如果抛出S3ResponseError
  conn.head_bucket(bucket_name)

def getBucketLocation(bucket_name):
  print(conn.get_bucket_location(bucket_name))

def createBucket(bucket_name, location=''):
  conn.create_bucket(bucket_name, location=location, headers={
    'x-kss-bucket-type': 'ARCHIVE'
  })

def deleteBucket(bucket_name):
  try:
    conn.delete_bucket(bucket_name)
  except S3ResponseError as error:
    print('error')
    print(error)

def getBucketAcl(bucket_name):
  b = conn.get_bucket(bucket_name)
  policy = b.get_acl()
  # print(policy)
  for grant in policy.acl.grants:
    print(grant.permission, grant.display_name, grant.email_address, grant.id)

def setBucketAcl(bucket_name):
  b = conn.get_bucket(bucket_name)
  b.set_acl("private")

def manageBucketPolicy(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  bucket.set_bucket_policy(
    policy='{"Statement":[{"Resource":["krn:ksc:ks3:::jiangran123","krn:ksc:ks3:::jiangran123/*"],"Principal":{"KSC":["krn:ksc:iam::32432423:root"]},"Action":["ks3:*"],"Effect":"Allow"}]}')
  # policy = bucket.get_bucket_policy()
  # bucket.delete_bucket_policy()

def manageBucketReplication(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  try:
    print(bucket.get_bucket_crr().to_xml())
  except:
    bucket.set_bucket_crr('test-bucket-project', deleteMarkerStatus='Disabled', prefix_list=['hello'])

def getBucketLifeCycle(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  lifecycle = bucket.get_bucket_lifecycle()
  print(lifecycle.to_xml())

def setBucketLifeCycle(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  lifecycle = BucketLifecycle()
  # id 和 status 必须
  rule = LifecycleRule(id='rule1', status='Enabled')
  date = datetime(2021, 9, 12).strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
  rule.expiration = LifecycleExpiration(date=date)
  lifecycle.rule = [rule]
  bucket.set_bucket_lifecycle(lifecycle)


def setBucketLifeCycle2(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  tag = Tag(key="tag1", value="test1")
  # 筛选前缀为 prefix1、标签为 tag1:test1 的 objects，设置过期规则，在其最后修改时间3天后过期。
  rule1 = LifecycleRule('rule1', LifecycleFilter('prefix1', tags=[tag]),
                        status='Enabled',
                        expiration=LifecycleExpiration(days=3))

  # 设置过期规则，筛选标签为 tag1:test1 的 objects，最后修改时间在指定日期之前的，过期
  rule2 = LifecycleRule('rule2', LifecycleFilter(tags=[tag]),
                        status='Enabled',
                        expiration=LifecycleExpiration(
                          date=datetime(2021, 12, 12).isoformat(timespec='seconds') + '+08:00'))

  # 设置存储类型转换规则，筛选前缀为 prefix3 的 objects，在其最后修改时间20天之后转为低频访问类型，在其最后修改时间30天之后转为归档类型。
  rule3 = LifecycleRule('rule3', LifecycleFilter('prefix3'),
                        status='Enabled',
                        transitions=[LifecycleTransition(days=20, storage_class='STANDARD_IA'),
                                     LifecycleTransition(days=60, storage_class='ARCHIVE')])

  # 设置存储类型转换规则，筛选前缀为 prefix3 的 objects，最后修改时间在指定日期之前的，转为低频访问类型
  rule4 = LifecycleRule('rule4', LifecycleFilter('prefix4'),
                        status='Enabled',
                        transitions=[
                          LifecycleTransition(date=datetime(2021, 12, 12).isoformat(timespec='seconds') + '+08:00',
                                              storage_class='STANDARD_IA')])
  # 设置分片上传碎片清理规则，筛选前缀为 prefix5 的 part，在最后修改时间7天后删除
  rule5 = LifecycleRule('rule5', LifecycleFilter('prefix5'),
                        status='Enabled',
                        abort_incomplete_multipart_upload=AbortIncompleteMultipartUpload(days_after_initiation=7))

  # print(rule1.to_xml())
  # print(rule2.to_xml())
  # print(rule3.to_xml())
  # print(rule4.to_xml())
  # print(rule5.to_xml())
  lifecycle = BucketLifecycle([rule1, rule2, rule3, rule4, rule5])
  bucket.set_bucket_lifecycle(lifecycle)

def deleteBucketLifeCycle(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  bucket.delete_bucket_lifecycle()

def getBucketLogging(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  print(bucket.get_bucket_logging().to_xml())

def setBucketLogging(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  blogging = BucketLogging(target=bucket_name, target_prefix='test_log')
  print(bucket.set_bucket_logging(blogging.to_xml()))

def enableBucketLogging(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  print(bucket.enable_logging(bucket, target_prefix='hehehehe'))

def disableBucketLogging(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  print(bucket.disable_logging())

def getBucketCors(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  print(bucket.get_bucket_cors().to_xml())

def putBucketCors(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  cors = BucketCors([CORSRule(origins=["http://dev.ksyun.com"], methods=["GET", "HEAD"], max_age="200", headers=["content-type"], exposed_headers=["content-type", "x-kss-acl"])])
  print('cors: ', cors.to_xml())
  print(bucket.set_bucket_cors(cors))

def deleteBucketCors(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  print(bucket.delete_bucket_cors())

def getBucketCrr(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  print(bucket.get_bucket_crr().to_xml())

def setBucketCrr(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  # deleteMarkerStatus 的值为 Enabled 和 Disabled
  # historicalObjectReplication 表示是否开启存量复制，值为 Enabled 和 Disabled
  print(bucket.set_bucket_crr('test-bucket-repli', deleteMarkerStatus=BucketCrossReplicate.ENABLED,
                              historicalObjectReplication=BucketCrossReplicate.ENABLED, prefix=['hello']))

def deleteBucketCrr(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  print(bucket.delete_bucket_crr())

def getBucketLogging(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  print(bucket.get_bucket_logging().to_xml())

def setBucketLogging(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  blogging = BucketLogging(target=bucket_name)
  print(bucket.set_bucket_logging(blogging.to_xml()))

def getBucketMirror(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  print(bucket.get_bucket_mirror())

def setBucketMirror(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  set_headers = [{
      "key": "d",
      "value": "b"
  }]
  remove_headers = [{
      "key": "d"
  }]
  pass_headers = [{
      "key": "abc"
  }]
  header_setting = HeaderSetting(set_headers=set_headers, remove_headers=remove_headers, pass_all=False, pass_headers=pass_headers)
  mirror_request_setting = MirrorRequestSetting(pass_query_string=False, follow3xx=False, header_setting=header_setting)
  async_mirror_rule = AsyncMirrorRule.rule_with_acl(mirror_urls=["http://abc.om", "http://www.wps.cn"], saving_setting_acl="private")
  sync_mirror_rules = SyncMirrorRules.rules_with_prefix_acl(key_prefixes=["abc"], mirror_url="http://v-ks-a-i.originalvod.com", mirror_request_setting=mirror_request_setting, saving_setting_acl="private")
  mirror = BucketMirror(use_default_robots=False, async_mirror_rule=async_mirror_rule, sync_mirror_rules=[sync_mirror_rules])
  print(bucket.set_bucket_mirror(mirror))

def deleteBucketMirror(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  print(bucket.delete_bucket_mirror())


def setBucketRetention(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  bucket_retention = BucketRetention()
  # 设置回收站规则：启用/禁用、文件保留天数
  rule = RetentionRule(RetentionRule.ENABLED, 2)
  # rule = RetentionRule(RetentionRule.DISABLED, 2)
  bucket_retention.rule = rule
  bucket.set_bucket_retention(bucket_retention)


def getBucketRetention(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  ret = bucket.get_bucket_retention()
  print(ret.to_xml())


def listRetention(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  keys = bucket.list_retention()
  for k in keys:
    print(k.name)
    print(k.retention_id)
    print(k.storage_class)


def clearObject(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.new_key('clear_key_name')
  k.clear_object('<retention_id>')


def recoverObject(bucket_name):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.new_key('recover_key_name')
  # 如果retention_id为空，默认恢复回收站中指定key的最新版本
  k.recover_object(overwrite=True, retention_id='<retention_id>')


#####################  ks3.billing  ###########################
from ks3.billing import get_buckets_data

def getBucketsData(bucket_names=None):
  data = get_buckets_data(ak, sk, start_time="202111192300", end_time="202111192359", bucket_names=bucket_names, products="DataSize,RequestsGet")
  print(data)

#####################  ks3.object  ###########################
def getObjectMeta(bucket_name, object_key_name, headers=None):
  bucket = conn.get_bucket(bucket_name)
  resp = bucket.get_key_meta(object_key_name, headers=headers)
  if resp:
    print("获取文件header成功: ", resp.headers)

def uploadObjectFromFile(filename):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.new_key(filename)
  ret = k.set_contents_from_filename(os.path.expanduser("~") + '/Downloads/' + filename)
  if ret and ret.status == 200:
    print("上传成功")

def upload_async(filename):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.new_key(filename)
  ret = asyncio.run(k.upload_file_async(os.path.expanduser("~") + '/Downloads/' + filename))
  if ret and ret.status == 200:
    print("上传成功")

def uploadObjectFromString():
  bucket = conn.get_bucket(bucket_name)
  k = bucket.new_key('大家好')
  # # key 和 value 需要 url 编码
  # taggingStr = 'name=jh'
  # headers = {'x-kss-tagging': taggingStr}
  ret = k.set_contents_from_string(' world')
  # # 请求ID。请求ID是本次请求的唯一标识，强烈建议在程序日志中添加此参数。
  # print(ret.headers['x-kss-request-id'])
  # # ETag是put_object方法返回值特有的属性，用于标识一个Object的内容。
  # print(ret.headers)
  # HTTP返回码。
  if ret and ret.status == 200:
    print("上传成功")

def headObject():
  bucket = conn.get_bucket(bucket_name)
  k = bucket.get_key('test_encryption')
  if k:
    print(k.name, k.size, k.last_modified, k.object_type, k.tagging_count)

def downloadObjectAndPrint(keyname, byte_range=(0, 1), headers=None):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.get_key(keyname)
  s = k.get_contents_as_string(byte_range=byte_range, headers=headers).decode()
  print(s)

def download_async(keyname, headers=None):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.get_key(keyname)
  try:
    asyncio.run(k.download_file_async(os.path.expanduser("~") + '/Downloads/' + keyname))
    print('下载成功')
  except:
    print('下载失败')

def downloadObjectAsStreamAndPrint():
  bucket = conn.get_bucket(bucket_name)
  k = bucket.get_key('shake.txt')
  bytes = k.read(300)
  print('start: ', datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
  while bytes:
    s = bytes.decode()
    print('bytes decoded:', s)
    time.sleep(5)
    bytes = k.read(300)
  print('end: ', datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))

def downloadObjectAndSave(key_name, byte_range=(0, 1), headers=None):
  bucket = conn.get_bucket(bucket_name)
  k = bucket.get_key(key_name)
  k.get_contents_to_filename('/Users/jabbar/Downloads/DSC03380.encrypt.非分块.jpg.download', headers=headers)

def deleteObject(key_name):
  bucket = conn.get_bucket(bucket_name)
  try:
    bucket.delete_key(key_name)
    print("删除成功")
  except Exception as e:
    print("删除失败")
    print(e)
    pass

def getObjectAcl():
  bucket = conn.get_bucket(bucket_name)
  policy = bucket.get_acl('article.txt')
  print(policy.to_xml())

def setObjectAcl():
  bucket = conn.get_bucket(bucket_name)
  # object policy : private | public-read | public-read-write
  bucket.set_acl("public-read", '<YOUR_KEY_NAME>')

def setObjectMeta():
  b = conn.get_bucket(bucket_name)
  b.copy_key('<yourKeyName>', '<yourBucketName>', '<yourKeyName>',
             headers={'content-type': 'text/plain', 'x-kss-metadata-directive': 'REPLACE'})

def setObjectStorageClass():
  b = conn.get_bucket(bucket_name)
  b.copy_key('<yourKeyName>', '<yourBucketName>', '<yourKeyName>', headers={'x-kss-storage-class': 'STANDARD_IA'})

def copy(dstKey, srcKey, dst_bucket_name=None, headers=None):
  # bucket_name = 'happyhour'
  b = conn.get_bucket(bucket_name)
  return b.copy_key(dstKey, dst_bucket_name, srcKey, headers=headers)

def copy_encryption(dstKey, srcKey, encrypt_key=None):
  b = conn.get_bucket(bucket_name)
  b.copy_key(dstKey, bucket_name, srcKey, encrypt_key=encrypt_key)

def list_objects():
  bucket = conn.get_bucket('test-bucket')
  keys = bucket.list(prefix='16')
  res1 = [k.name for k in keys]
  print('res1 : ', res1)

  keys2 = bucket.listObjects(prefix='16')
  # res2 = [k.name for k in keys2]
  print('keys2 : ', keys2)
  # for k in keys:
  #   print('object:', k.name)

def list_objects_v2(delimiter='#', prefix=None, max_keys=None, marker=None, encoding_type='', fetch_owner=True):
  bucket = conn.get_bucket(bucket_name)
  keys = bucket.list_v2(delimiter=delimiter, prefix=prefix, max_keys=max_keys, marker=marker, encoding_type=encoding_type, fetch_owner=fetch_owner)
  for k in keys:
    print('object:', k.name)

def listObjectsMore(bucket_name, delimiter=None, prefix=None, max_keys=None, marker=None):
  bucket = conn.get_bucket(bucket_name)
  keys = bucket.list(delimiter=delimiter, prefix=prefix, max_keys=max_keys, marker=marker)
  # print(len(keys))
  res = [k.name for k in keys]
  print('res: ', res)
  # print('item:', k.name, type(k))

def listAndDelete():
  bucket = conn.get_bucket(bucket_name)
  keys = bucket.list(delimiter='/', max_keys=10, prefix='15')
  print(keys.marker)
  for k in keys:
    print('object:', k.name)
    deleteObject(k.name)

def listObjectsAndFilter(endTime=None):
  bucket = conn.get_bucket('auto-test-bucket')
  keys = bucket.listObjects(delimiter='/', max_keys=2) # start_time=1640331446, end_time=1641895096
  for k in keys:
    print(k)

def getObjectTagging():
  bucket = conn.get_bucket(bucket_name)
  key = bucket.get_key('testTagging')
  tagging = key.get_object_tagging()
  print(tagging.to_xml())

def setObjectTagging():
  bucket = conn.get_bucket(bucket_name)
  key = bucket.get_key('testTagging')
  tagging = [Tag('0'), Tag('1', '1')]
  key.set_object_tagging(tagging)

def deleteObjectTagging():
  bucket = conn.get_bucket(bucket_name)
  key = bucket.get_key('hehe')
  key.delete_object_tagging()

def calcFolderSize(bucket, folder):
  length = 0
  keys = bucket.list(prefix=folder)
  for k in keys:
    if isinstance(k, Key):
      length += k.size
  return length

from ks3.prefix import Prefix

# 列举指定目录下的文件大小
def getFolderSizeInBucket():
  bucket = conn.get_bucket(bucket_name)
  keys = bucket.list(delimiter='/')
  for k in keys:
    if isinstance(k, Prefix):
      print('dir: ' + k.name + '  size:' + str(calcFolderSize(bucket, k.name)) + "Byte")


def test_multipart_upload(encrypt_key=None):
  import math, os
  from filechunkio import FileChunkIO
  bucket = conn.get_bucket(bucket_name)

  source_path = '/Users/jabbar/Downloads/DSC03380.JPG'
  # 源文件大小
  source_size = os.stat(source_path).st_size

  mp = bucket.initiate_multipart_upload("DSC03380.mp.jpg", encrypt_key=encrypt_key)
  print(mp)

  chunk_size = 5242880
  chunk_count = int(math.ceil(source_size * 1.0 / chunk_size * 1.0))

  # 通过 FileChunkIO 将文件分片
  for i in range(chunk_count):
    offset = chunk_size * i
    bytes = min(chunk_size, source_size - offset)
    with FileChunkIO(source_path, 'r', offset=offset, bytes=bytes) as fp:
      # 逐个上传分片
      mp.upload_part_from_file(fp, part_num=i + 1)
  print(mp.to_xml())
  # 发送请求，合并分片，完成分片上传
  ret = mp.complete_upload()
  if ret and ret.status == 200:
    print("上传成功")

def test_fetch_object():
  bucket = conn.get_bucket(bucket_name)
  key = bucket.new_key('www-logo')
  key.fetch_object(source_url='http://fe.ksyun.com/project/resource/img/www-logo.png',
                      headers={'x-kss-acl': 'public-read'})
  print('fetch成功')

def test_generate_url(key_name, image_attrs=None):
  b = conn.get_bucket(bucket_name)
  k = b.get_key(key_name)
  if k:
    url = k.generate_url(600, image_attrs=image_attrs)  # 60s 后该链接过期
    print(url)
  else:
    print('object not found')

def test_get_presigned_url(key_name):
  b = conn.get_bucket(bucket_name)
  # 新建对象key
  k = b.new_key(key_name)
  if k:
    url = k.get_presigned_url(60000)  # 60s 后该链接过期
    print(url)
    return url

def restoreObject(key_name):
  b = conn.get_bucket(bucket_name)
  k = b.get_key(key_name)
  k.restore_object()

def test_put_via_presigned_url(key):
  url = test_get_presigned_url(key)
  with open('./article.txt', 'rb') as fp:
    result = requests.put(url, data=fp)
    print(result)

from ks3.sts import assumeRole
def test_assumeRole():
  print(assumeRole(ak, sk, "krn:ksc:iam::xxx:role/xx-test-bucket", "ks3", 3600))


def put_object_callback(key_name):
  b = conn.get_bucket('hanjing-test000')
  # 新建对象key
  k = b.new_key(key_name)
  # 上传成功后，向回调地址POST数据
  # 需要设置`x-kss-callbackurl`和`x-kss-callbackbody`请求头，详见文档[上传回调处理](https://docs.ksyun.com/documents/956)。
  # x-kss-callbackurl 为发起回调时请求的服务器地址
  # x-kss-callbackbody 为发起回调时请求的body的值
  headers = {"x-kss-callbackurl": "https://yh-sh.ks3-cn-shanghai.ksyuncs.com", "x-kss-callbackbody": "objectKey=${key}&etag=${etag}&bucket=${bucket}&objectSize=${objectSize}&mimeType=${mimeType}&createTime=${createTime}", "x-kss-callbackauth":1}
  ret = k.set_contents_from_string("test-callback", headers=headers)
  if ret and ret.status == 200:
    print("上传成功")

# getAllBuckets()
# headBucket('bj')
# getBucketLocation('test-host-style')
# createBucket('test-bucket-archive-test-shanghai2', location='SHANGHAI')
# deleteBucket('test-bucket')
# getBucketAcl('test-bucket')
# setBucketAcl('test-bucket')
# manageBucketReplication('test-bucket')
# getBucketLifeCycle(bucket_name)
# setBucketLifeCycle(bucket_name)
# setBucketLifeCycle2(bucket_name)
# deleteBucketLifeCycle(bucket_name)
# getBucketLogging(bucket_name)
# setBucketLogging(bucket_name)
# disableBucketLogging(bucket_name)
# enableBucketLogging(bucket_name)
# putBucketCors(bucket_name)
# getBucketCors(bucket_name)
# deleteBucketCors(bucket_name)
# deleteBucketCrr(bucket_name)
# getBucketCrr(bucket_name)
# setBucketCrr(bucket_name)
# setBucketMirror(bucket_name)
# deleteBucketMirror(bucket_name)
# getBucketMirror(bucket_name)
##### object #####
# getObjectMeta(bucket_name, 'article.txt')
# list_objects()
# listObjectsMore("auto-test-bucket", delimiter='/', max_keys=2, marker='1050')
# listObjectsMore("auto-test-bucket", delimiter='/', max_keys=2, marker='105/')
# listObjectsMore("auto-test-bucket", delimiter='/', max_keys=2, marker='105%2F')
# listObjectsAndFilter()
# setObjectTagging()
# getObjectTagging()
# deleteObjectTagging()
# getFolderSizeInBucket();
# downloadObjectAndPrint()
# downloadObjectAsStreamAndPrint()
# downloadObjectAndSave(bucket_name, 'DSC03380.encrypt.非分块.jpg', headers={
#   'range': 'bytes=0-5242880'
# })
# count = 20
# while True:
# uploadObjectFromFile('法治.jpeg')
upload_async('法治.jpeg')
download_async('1659684872.torrent')
# uploadObjectFromFile('xab')
# uploadObjectFromFile('xac')
#   time.sleep(5)
#   count = count - 1
# uploadObjectFromString()
# headObject()
# downloadObjectAndPrint('test_directory/')
# deleteObject("tellmewhy")
# getObjectAcl()

# test_multipart_upload(encrypt_key=True)

# test_fetch_object()
# def test_generate_url(key_name, image_attrs=None):
#   b = conn.get_bucket(bucket_name)
#   k = b.get_key(key_name)
#   if k:
#     url = k.generate_url(600, image_attrs=image_attrs)  # 60s 后该链接过期
#     print(url)
#   else:
#     print('object not found')

# bucket = conn.get_bucket('test-bucket')
# keys = bucket.list()
# for k in keys:
#   print(k)
#   if isinstance(k, Key):
#     url = k.generate_url(600)
#     res = requests.get(url)
#     if res.status_code != 200:
#       print(url)


# res = requests.get(url)
# assert res.status_code != 403
# test_generate_url('\\a\\\\:<>*?|:q.jpeg')
# test_generate_url('#x2;.jp.csv')
# test_generate_url('10086/198.18-reset-共计9条.txt')
# test_generate_url('10086/getbucket.csv')
# test_get_presigned_url('~*c/heckData+sdf=%2F.json')
# test_put_via_presigned_url('index.html')
# list_objects_v2(delimiter='/', encoding_type='url', fetch_owner=False)
# list_objects()
# listObjectsMore()
# deleteObject()
# listObjectsAndFilter()
# listAndDelete()
# restoreObject("www-logo")
# getBucketsData("test-bucket")
# test_assumeRole()

# copy_encryption('article.encryption.txt', 'article.txt', encrypt_key=True)

# fileName = "\u006b\u0073\u005f\u0073\u0063\u0061\u006e\u005f\u006f\u0063\u0072\u002f\u0032\u0030\u0031\u0038\u002d\u0030\u0033\u002d\u0031\u0032\u002f\u0010\ufffd\u0070\ufffd\ufffd\ufffd\u0002\u002e\u0057\u007f\u005b\ufffd\u0008\ufffd\u002a\ufffd\u002e\u006a\u0070\u0067";
# hehe = "�p���.W[�*�.jpg"
# for c in hehe:
#     print(repr(c), c)
# urlcoded = urllib.parse.quote(fileName)
# unquoted = urllib.parse.unquote('%FF')
# quoted = urllib.parse.quote(unquoted)
# print(unquoted)
# print(quoted)

# getObjectMeta('test-bucket', 'article.txt')
# key = copy('article.txt', 'article.txt', dst_bucket_name='test-bucket')
# print('after copy\n\n')
# getObjectMeta('test-bucket', 'article.txt')
# getObjectMeta('test-bucket', 'DSC03380.ssec.jpg')
# uploadObjectFromFile('DSC03380.encrypt.jpg')

# import base64
# import hmac
# import hashlib
# import urllib
# h = hmac.new("accesskey",
#              "GET\n\n\n1141889120\n/examplebucket/oss-api.pdf",
#              hashlib.sha1)
# urllib.quote (base64.encodestring(h.digest()).strip())

# b = conn.get_bucket(bucket_name)
# # for p in b.get_all_multipart_uploads(key_marker='test-multi', upload_id_marker='bbfcf0bab5e845d895d0cfcd2632bf18'):    '7e6b7b7912d14eb0942413f262c488ec'
# all_uploads = b.get_all_multipart_uploads(key_marker='DSC03380.encrypt.jpg-dddddddd')#max_uploads=27)
# print(len(all_uploads))
# for p in all_uploads:
#   print(p, p.id)
# put_object_callback('test-callback')