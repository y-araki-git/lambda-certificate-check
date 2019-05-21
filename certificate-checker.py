#!/bin/python
# coding: utf-8
 
#モジュールインポート
from pytz import timezone
from datetime import datetime,tzinfo
from urlparse import urljoin
from urllib import
import urllib2 as urlrequest
import json
import boto3
import os
 
#変数定義
SLACK_POST_URL = os.environ['WEB_HOOK_URL']
SLACK_MESSAGE_TITLE = 'Amazon Certificate Checker'
 
#ACMのAPIを使用
client = boto3.client('acm')
 
#イベントハンドラ
def handler(event, context):
    post_msg = build_message()
 
    if post_msg["text"] != "":
        return post(post_msg)
 
#SLACKメッセージ作成関数
def build_message(**kwargs):
    post_message = {}
    post_message["pretext"] = SLACK_MESSAGE_TITLE
    post_message["text"] = get_not_after_date('ISSUED', 'Asia/Tokyo')
    post_message.update(kwargs)
    return post_message
 
 
def post(payload):
    data = urlencode({"payload": payload_json})
    req = urlrequest.Request(SLACK_POST_URL)
    response = urlrequest.build_opener(urlrequest.HTTPHandler()).open(req, data.encode('utf-8')).read()
    return response.decode('utf-8')
 
def get_not_after_date(certificate_status, time_zone):
    payload_json = json.dumps(payload)
    certificate_dict = get_certificate_arn_list(certificate_status, time_zone)
    arn_list = certificate_dict.values()
    domain_name = certificate_dict.keys()
     
    not_after_date = []
 
    for i in arn_list:
        response = client.describe_certificate(
            CertificateArn=i
        )
 
        certificate = response['Certificate']
        not_after_date.append(certificate['NotAfter'])
 
    return get_days_left_list(time_zone, not_after_date, domain_name)
 
def get_certificate_arn_list(certificate_status, time_zone):
    certificate_dict = {}
 
    response = client.list_certificates(
    CertificateStatuses=[
        certificate_status
    ]
    )
    certificate_summary_list = response['CertificateSummaryList']
    for i in certificate_summary_list:
        certificate_dict[i['DomainName']] = i['CertificateArn']
 
    return certificate_dict
 
def get_days_left_list(time_zone, not_after_date, domain_name):
    days_left_list = []
    now = datetime.now()
    now = timezone(time_zone).localize(now)
 
    for i in not_after_date:
    days_left = i - now
    days_left = days_left.days
    days_left_list.append(days_left)
 
    return create_dict(domain_name, days_left_list)
 
def create_dict(domain_name, days_left_list):
    target_and_left_list = dict(zip(days_left_list, domain_name))
 
    return create_message(target_and_left_list)
 
def create_message(target_and_left_list):
    target_and_left_keys = target_and_left_list.keys()
    message_list = []
    for i in target_and_left_keys:
        if i == 30 or i == 14 or i <= 7:
            message_list.append(str(target_and_left_list[i])+'が'+str(i)+"日で期限です。")
     
    message = "\n".join(message_list)
 
    return message