import configparser
import pandas as pd
from pypinyin import lazy_pinyin
import re
import requests
import json
from PIL import Image
import base64
import io
import inspect
import warnings
import sqlite3
from datetime import datetime
from lyylog import log
from sqlalchemy import create_engine, text, exc
import lyytext
from pdf2image import convert_from_path
from urllib.parse import urlparse, unquote
import lyyimage
import lyyddsender
import subprocess
import lyyprocess
import http.client

"""
markdown_json发送前：
data= {'msgtype': 'markdown', 'markdown': {'title': '图片', 'text': '![](@lAPPM25bqxb_A7PNApTNAcI)', 'at': {},'name':"luofei",'chinesename':'洛飞"}}
wss收到的图片和文本格式：
{'msg': '{"type":"text","markdown":{"from":"洛飞笔记","id":"77315199515","text":"充策略] 2023-12-28 11:09:47德业，建议取关一半。","image":""}}', 'mb': '77315199515'}
{'msg': '{"type":"image","markdown":{"from":"傅峙峰","id":"77091290576","text":"","image":"https://static.d0P8eefTNBTwpng?auth_bizType=IM&bizType=im"}}', 'mb': '77091290576'}    
{'msgtype': 'markdown', 'markdown': {'at': {'atMobiles': [], 'isAtAll': False}, 'text': '二个高标都板确认', 'title': '二个高标都板，突破7板，新的'}, 'name': 'dachenglupang', 'chinesename': '大成路旁', 'mb': 1756, 'cmd': 'mengxia'}

"""



def get_img_size_from_url(url):
    regex=r'_\d{2,4}_(\d{2,4})\.png'
    match = re.search(regex,url)
    if match:
        width=match.group(1)
        print("Width=",width)

u="https://static.dingtalk.com/media/lALPD1za8UFzIqnNAsXNA0A_832_709.png?auth_bizType=IM&bizType=im"
get_img_size_from_url(u)

def is_weekday_time():
    # 获取当前日期和时间
    now = datetime.now()

    # 判断是否是周一到周五
    weekday = now.weekday() < 5

    # 判断是否在9点到11点之间
    time_interval = (920<=(now.hour*10 +now.minute) <=1000)

    return weekday and time_interval
def process_ocr(msg_json, text_rule_dict, deny_ocr_text_patterns_list,ocr_engine,retry=True,debug=False):
    try: 
        if "img" not in msg_json.keys() or msg_json["chinesename"]  in deny_ocr_text_patterns_list:
            print("if ocr:","img" not in msg_json.keys() , msg_json["chinesename"]  in deny_ocr_text_patterns_list)
            return None

        print("有img字段且未在禁止ocr名单中，尝试ocr")
        ocr_result_text = lyyimage.ocr_panddle_jd_server(msg_json['img'] )
        if ocr_result_text is None:
            return
        ocr_result_text = process_format_msg_text(ocr_result_text, text_rule_dict)

        print(f"来自{msg_json['chinesename']}群的图片ocr结束，过滤看是否有用：，无用则直接跳过回到正常图片处理流程")

        if lyytext.ocr_text_is_useful(ocr_result_text, deny_ocr_text_patterns_list):
            print("排除了其它不保留的OCR情况。开始处理")
            msg_json_with_ocr_text = msg_json
            msg_json_with_ocr_text["markdown"]["text"] = ocr_result_text
            del msg_json_with_ocr_text["img"]
            # lyyddforward.dd_to_db(engine, ocr_result_text, 消息中文群名, 来源群拼音,                                     msg_json['groupid'], msg_json['cmd'])

            if len(ocr_result_text) < 4:
                log("---------ok ocr result--------" + ocr_result_text + ",img=" + str(msg_json))
                return
            else:
                print("<<<<OK ocr_yext=",msg_json_with_ocr_text)
                return msg_json_with_ocr_text
    except Exception as e:
        return None




def try_to_ocr_by_ocr_panddle_jd_server(img_link, ocr_red_text=False, debug=False):
    # 目标URL
    url = "http://117.72.45.252:10028/ocr"
    print("img urlll=",img_link)
    # 要发送的数据
    post_data = {"img_url": img_link}

    # 发送POST请求
    response = requests.post(url, json=post_data)

    # 检查响应是否成功
    if response.status_code == 200:
        if debug:
            print(response.text)
        # 解析JSON响应
        result = response.json()
        ocr_text = result.get("ocr_text")
        if len(ocr_text) != 0 and not ocr_text.startswith("error"):            
            return result.get("ocr_text")
    
    # 如果响应不成功，打印错误信息
    print(f"Error: {response.status_code}, response={response}")
    return None


                
def try_to_ocr_old(msg_json, deny_ocr_text_patterns_list,ocr_engine,retry=True,debug=False):
    if ocr_engine  =="tesseract":
        ocr_function = lyyimage.ocr_img_file_to_text_by_tesseract
    elif ocr_engine  =="baidu-api" and  is_weekday_time():
        print("current ocr engine=`","百度OCR")

        ocr_function = lyyimage.百度OCR
    else:
        ocr_function = lyyimage.ocr_panddle_jd_server
        print("current ocr engine=`","ocr_panddle")
        #ocr_function = lyyimage.ocr_panddle

    msg_json_with_ocr_text = msg_json
    file_url = get_to_ocr_image_pdf_url(msg_json["img"])
    try:
        file = download_file(file_url)
    except Exception as e:
        print("download file error=",e)
        return None
    print("download is as " + file)
    if ".pdf" in file:
        ocr_text_result = ocr_pdf_file(file)
    elif ".jpg" in file or ".png" in file or ".bmp" in file or ".jpeg" in file:
        try:
            ocr_red_text = True if msg_json['chinesename'] in deny_ocr_text_patterns_list else False               
            ocr_text_result = ocr_function(file, ocr_red_text=ocr_red_text, debug=debug)

            return ocr_text_result
        except Exception as e:
            log("in ocr function, error msg="+ str(e)+"if retry then retry:"+ str(retry))
            if retry:
                ocr_engine  ="ocr_panddle" if ocr_engine  =="baidu-api" else "baidu-api"
                try_to_ocr(msg_json, deny_ocr_text_patterns_list, ocr_engine,retry=False)

def forward_msg_group_by_group(df,msg_json,debug=False):

    for index, row in df.iterrows():
        to = row['to']
        fromgroup = row['from']
        fromuser = row['fromuser']
        from_group_name = row['from_group_name']
        # prefix = row['prefix']
        remove_patterns = row['remove_patterns']
        markdown_text = re.sub(remove_patterns, '', msg_json['markdown']['text'])
        # print("fromuser=",fromuser,type(fromuser))
        if len(fromuser) > 5:
            if "uid" in msg_json.keys():
                if fromuser != msg_json['uid']:
                    #print(f"{消息中文群名}群的指定用户不符合，忽略")
                    return "remove_sql"

        #replace=
        if len(to) < 10:
            return "no target to send"
        toArray = to.strip("|").split("|")
        for i in range(len(toArray)):
            parts = toArray[i].split("***")
            if len(parts) == 3:
                if debug: print("prefix have value")
                钉钉webhook, 钉钉sign, prefix = parts
            elif len(parts) == 2:
                钉钉webhook, 钉钉sign = parts
                prefix = None
            timerange = None

            dd = lyyddsender.DingtalkChatbot(webhook=钉钉webhook, secret=钉钉sign)

            #self.text1.insert(tk.END, str(msg_json)+"\n")
            #result = send_dingtalk_message( msg_json,钉钉webhook, 钉钉sign)
            if 'img' in msg_json.keys():
                if debug: print(f"收到图片{prefix} {msg_json['img']}")
                title = prefix if prefix is not None else "图片"
                result = dd.send_markdown_img(title, msg_json['img'])

            else:
                if debug: print(f"{msg_json['chinesename']} 不是图片")
                if markdown_text and prefix is not None and "https" not in markdown_text:
                    markdown_text = prefix + "：" + markdown_text
                msg_json_full = msg_json_from_text_or_imgurl(
                    markdown_text)
                result = lyy_send_msg_json_by_pass_hosts(
                    钉钉webhook, 钉钉sign, msg_json_full)
        return result



def download_file(url,debug=False):
    if debug: print("in download file")
    response = requests.get(url)
    filename = get_filename_from_url(url)
    if debug: print("to saved as "+filename)
    with open(filename, 'wb') as output_file:
        output_file.write(response.content)
    if debug: print("in download_file,  finished")
    return filename

def get_to_ocr_image_pdf_url(text,debug=False):
    if debug: print("enter get_to_ocr_image_pdf_url")
    pattern = r'https?://[\w/\-?=%.]+\.(pdf|png|jpeg|jpg|bmp)'
    if debug: print("try to search")
    match = re.search(pattern,text)
    if match:        
        if debug: print("找到匹配=",match.group())
        return match.group()
    else:
        if debug: print("没有匹配，返回False")
        return False

def get_filename_from_url(url):
    print("get_filename_from_url")
    extension =  url[-4:]
    return "tmp"+extension



def ocr_pdf_file(pdf_file_path):
    images = convert_from_path(pdf_file_path)
    result_text_list = []
    for i, image in enumerate(images):
        image.save(f'image{i}.png', 'PNG')
        ocr_text_result = lyyimage.ocr_img_file_to_text(f'image{i}.png')
        result_text_list.append(ocr_text_result)
    return "\n".join(result_text_list)



def lyytimer时间没超(时间文本):
    nowtime_full = str(datetime.now())
    现在时 = nowtime_full[11:13]
    现在分 = nowtime_full[14:16]
    现在时间 = nowtime_full[11:16]

    # print(现在时)
    # print(时间文本)

    if len(时间文本) > 2:
        时间文本 = 时间文本.replace("：", ":")
        参数数组 = 时间文本.split(":")
        参数时 = 参数数组[0]
        参数分 = 参数数组[1]
        时没到 = int(现在时) < int(参数时)
        时到了分钟没到 = int(现在时) == int(参数时) and int(现在分) < int(参数分)
        if 时没到 or 时到了分钟没到:
            return True
        else:
            return False
    else:
        if int(现在时) < int(时间文本):
            return True
        else:
            return False


def 符合时间(时间文本):
    nowtime_full = str(datetime.now())
    现在时间 = nowtime_full[11:16]
    if 现在时间 == 时间文本:
        return True
    else:
        return False


def lyytimer处于时间范围或者符合时间(范围文本):
    范围文本 = 范围文本.replace("：", ":")
    范围文本 = 范围文本.replace(" ", "-")
    范围文本 = 范围文本.replace("　", "-")
    范围文本 = 范围文本.replace("~", "-")

    if "-" in 范围文本:
        范围数组 = 范围文本.split("-")
        if lyytimer时间达到(范围数组[0]) and lyytimer时间没超(范围数组[1]):
            return True
        else:
            return False
    else:
        return 符合时间(范围文本)


def lyytimer时间达到(时间范围的起始时间):
    nowtime_full = str(datetime.now())
    现在时 = nowtime_full[11:13]
    现在分 = nowtime_full[14:16]
    现在时间 = nowtime_full[11:16]
    # print(现在时)
    # print(时间范围的起始时间)

    if len(时间范围的起始时间) > 2:
        时间文本 = 时间范围的起始时间.replace("：", ":")
        参数数组 = 时间范围的起始时间.split(":")
        参数时 = 参数数组[0]
        参数分 = 参数数组[1]
        时没到 = int(现在时) < int(参数时)
        时到了分钟没到 = int(现在时) == int(参数时) and int(现在分) < int(参数分)
        if 时没到 or 时到了分钟没到:
            return False
        else:
            return True
    else:
        if int(现在时) < int(时间范围的起始时间):

            return False
        else:
            return True



def process_format_msg_text(msg, text_rule_dict,debug=False):
    #if debug: print("enter fun process_msg_text,text_rule_dict=",text_rule_dict)
    #根据字典中的设置对文本对待处理
    #1. 删除re模式 2.删除文本 3.替换文本 4.删除首尾
    #参数1如果是str直接处理

    markdown_text=msg if isinstance(msg,str) else msg['markdown']['text']
    if markdown_text.startswith("http")  :
        return markdown_text

    #if debug: print("#批量删除特定re模式")
    #if debug: print("in process_msg_text, text_rule_dict=",text_rule_dict['global_remove_patterns'].keys())
    
    markdown_text = lyytext.batch_remove_regex_strings_by_list(text_rule_dict['global_remove_patterns'].keys(),markdown_text,debug=debug)

    #if debug: print("#删除特定文本")
    markdown_text = lyytext.batch_format_remove_subtext(markdown_text,text_rule_dict["global_remove_subtext"].keys(),debug=debug)

    #if debug: print("#替换特定文本")
    markdown_text = lyytext.batch_replace_text_by_dict(markdown_text, text_rule_dict['global_replace_patterns'],debug=debug)

    #if debug: print("#去除收尾特定字符。")
    markdown_text = lyytext.batch_strip_text(markdown_text,text_rule_dict["strip_characters"].keys(),debug=debug)
    #if debug: print("in process_msg_text, result=",markdown_text)
    return markdown_text

def get_img_url_from_server(img_url="@lALPM25brIffogLNASPNAl8"):
    conn = http.client.HTTPConnection("127.0.0.1", 12888)
    conn.request("GET", f"/?{img_url}")
    response = conn.getresponse()
    data = response.read().decode("utf-8")
    return data

def extracet_img_packet(text):
    pattern = r'!\[screenshot\]\(@([a-zA-Z0-9\-\_]+?)\)'
    # 使用正则表达式搜索
    matches = re.search(pattern, text)

    # 检查是否有匹配
    if matches:
        # 提取匹配的组
        extracted_text = matches.group(1)

        log("找到图片包,imgpacket=",extracted_text)
        url = get_img_url_from_server(extracted_text)
        return(extracted_text)  # 输出: lALPM2OzMXg0v_7NBOLNArI

    else:
        print("No match found")
        return text


def format_xmpro(original_data, pinyin2token,token,dict_group_pinyin):
    if isinstance(original_data,str):
        original_data=json.loads(original_data)
    json_new = {'msgtype': 'markdown', 'markdown': {'at': {}}}
    if original_data['msgtype']=="text":
        json_new['markdown']['text']=original_data['text']['content']   
        json_new['markdown']['title'] = original_data['text']['title'] if "title" in original_data['text'] else original_data['text']['content'] [:20]

    
    elif original_data['msgtype']=="markdown":
        if "![screenshot](@" in original_data['markdown']['text']:
            #flsk_msg_json =  {'msgtype': 'markdown', 'markdown': {'title': '#### 扑影: 茅台     ![screenshot](@lALPM2OzMXg0v_7NBOLNArI)         > 2024-04-08 上午 10:33:39   ', 'text': '####  扑影: 茅台     ![screenshot](@lALPM2OzMXg0v_7NBOLNArI)         > 2024-04-08 上午 10:33:39   '}, 'at': {'atMobiles': [], 'isAtAll': False}}
            print("format_xmpro, startswith screenshot")
            url = extracet_img_packet(original_data['markdown']['text'])
            json_new['markdown']['text'] = json_new['img']=url
            json_new ['title']="图片"
        else:
            print("markdown, but not screenshot")
            json_new['markdown']['text'] = original_data['markdown']['text']
            json_new['markdown']['title'] = original_data['markdown']['title']

    elif original_data['msgtype']== 'actionCard':
        print("you got an actionCard")
        json_new['markdown']['text'] = original_data['actionCard']['text']
        json_new ['markdown']['title']=original_data['actionCard']['title']

    else:
        #flsk_msg_json =  {'actionCard': {'title': 'certificate.pem', 'text': 'certificate.pem', 'hideAvatar': '0', 'btnOrientation': '1', 'singleTitle': '立即查看', 'singleURL': ''}, 'msgtype': 'actionCard'}
        log("format_xmpro, msg_type不是markdown又不是text,original_data=",str(original_data))
    

    json_new['name']= token
    json_new['chinesename'] = dict_group_pinyin.get(json_new['name'])
    json_new['groupid']=0
    json_new['cmd'] = "showmsg"
    return json_new
# {'msgtype': 'markdown', 'markdown': {'at': {}, 'text': 'd d a ', 'title': 'd d a '}, 'name': '7823f3682963d60828b772cd8d08206b219bcbd51bb823045bf4e8e607a34fad***SECa5ec4cb87b097f4b48d0249be3b3505e6dd8c29a8fb2bb68639e09348ef8de93***好的', 'chinesename': None, 'cmd': 'showmsg'}
    # data_type = original_data['msg']['type']
    # data_text = original_data['msg']['text']
    # data_title = original_data['msg']['title']
    #text:1,image:2,link:102,file:501,voice:3,richtext:3100

    #msg_json =  {'msgtype': 'markdown', 'markdown': {'title': '[ͼƬ]', 'text': '![screenshot](https://static.dingtalk.com/media/lQLPJxuMEduq0pE0eLCK5L7vMiTxswYACJrskR4A_120_52.png?auth_bizType=IM&bizType=im)'}, 'at': {'atMobiles': [], 'isAtAll': False}}
    # [23:56:15]jsonStr={"msg":{"id":"18782752867960","type":1200,"title":"DING]() ","text":"DING]() "},"source":{"type":2,"uid":"4184562838","nick":"1","cid":"56752603742","name":"震哥ad"}}
    #[00:05:52]jsonStr={"msg":{"id":"18798625399052","type":1200,"title":"[图片]  ","text":"![](@lADPD0eJ-qyq9jnNBQDNA-E)    "},"source":{"type":2,"uid":"4184562838","nick":"1","cid":"56752603742","name":"震哥ad"}}

def format_mengxia(msg_json, number, number_pinyin_dict,number_chinese_dict,debug=False):
     #{'type': 'text', 'msg': '[52秒] [请用手机APP收听](https://static.dingtalk.com/media/lAXPDf0i9wsXJoXOd3xZy84aeXqv.mp3) \r\n 语音消息 ', 'url': '', 'name': ''}
    json_new = {'msgtype': 'markdown', 'markdown': {'text':'','title':'','at': {}}}
    if msg_json['type'] == "text":
        json_new['markdown']['text']= msg_json["msg"].replace("\\/","/").replace(r"/////",r"//")
    elif msg_json['type'] == "pic" :
        json_new['markdown']['text']= msg_json["url"].replace("\\/","/").replace(r"/////",r"//")
        json_new['img']=json_new['markdown']['text']
    elif msg_json['type'] == "file":
        json_new['markdown']['text']= msg_json["url"].replace("\\/","/").replace(r"/////",r"//")
    else:
        log("in get_msg_content_from_json, 出现第3种情况 ", +str(msg_json))
    #生成标准json，如果黑名单，返回None，后续会跳过处理。
    if len(json_new['markdown']['text']) < 3:
        return None
    if "title" in msg_json.keys():
        json_new['markdown']['title'] = msg_json['title']
    else:
        json_new['markdown']['title'] = json_new['markdown']['text'][:14]
    
    json_new['groupid'] = number
    json_new['cmd'] = "mengxia"
    # print("try to get pinyin from number_pinyin_dict")

    if "name" in msg_json.keys() and "chinesename" in msg_json.keys():
        json_new['name']=msg_json.get("name")
        json_new['chinesename']=msg_json.get("chinesename")

    else:
        if number in number_pinyin_dict.keys():
            json_new['name'] = number_pinyin_dict[number]
            json_new['chinesename'] = number_chinese_dict[number]

        else:
            log(f"此number{number}没有。message={msg_json}")
            json_new['name'] = "weizhiqunzu"
            json_new['chinesename'] = "未知群组"

    return json_new

def get_chinesename_sign_dict(ddforward_file=r"D:\UserData\resource\ddForward\ddForward.ini"):
    cfdd = configparser.ConfigParser()
    cfdd.read(ddforward_file, encoding="utf-8")
    config_dict = {}
    for section in cfdd.sections():
        group_name = get_config_value(cfdd, section, "from_group_name")
        webhook_sign = get_config_value(cfdd, section, "to")
        config_dict[group_name] = webhook_sign
    return config_dict

def get_dict_from_file(file_path):
    # 读取文件内容
    with open(file_path, 'r',encoding="utf-8") as file:
        content = file.read()
    # 将文本内容转换为字典
    data = {}
    lines = content.split('\n')
    for line in lines:
        if ":" in line:  # 忽略空行
            key, value = line.split(':')
            data[int(key.strip())] = value.strip().replace('"','').replace(',','')
    # 将字典转换为 JSON 格式并打印
    return data

def get_chinese_from_pinyin(pinyin,dict_group_pinyin,debug=False):

    for key, val in dict_group_pinyin.items():
        if pinyin in key:
            return val
    log(f"pinyin没找到匹配的chinese，请检查。pinyin={pinyin} ")
    return "未知群组"
    if debug: print(f"{str(dict_token_pinyin)}")


def get_pinyin_from_token(token,dict_token_pinyin):
    for key, val in dict_token_pinyin.items():
        if token in val:
            return key
    log(f"token没找到匹配的拼音，请检查。token={token}, {str(dict_token_pinyin)}")



# def format_flask(json_data,group_name_replace_dict_flask,dict_groupid_chinese):
#     if "img" not in json_data.keys():
#         txt_content=json_data['markdown']['text']
#         img=get_http_imgurl_from_text(txt_content)
#         if img is not None:
#             json_data['img']=img
#             json_data['markdown']['title']="图片"
#         else:#真的不是图片
#             json_data['markdown']['title']=txt_content[:14]
#     print("in format_flask, json = ",json_data)

#    return json_data
def format_flask2(json_data,group_name_replace_dict_flask,dict_groupid_chinese):
    msg_json={"msgtype": "markdown", "markdown": {"title": "[]", "text": ""}, "at": {}}
    if "source" in json_data.keys():
        msg_json['chinesename'] =群中文名=json_data['source']['name']
        群号=json_data['source']['cid']
        msg_json['fromuser']=json_data['source']['uid']
        msg_json['groupid']=群号
    else:
        msg_json['chinesename'] = json_data['from']
        msg_json['fromuser'] = json_data['uid']
    
    if json_data['groupid']  in dict_groupid_chinese.keys():
        msg_json['chinesename'] =dict_groupid_chinese[json_data['groupid'] ]
    elif  json_data['chinesename']  in group_name_replace_dict_flask.keys():
        msg_json['chinesename'] =group_name_replace_dict_flask[json_data['chinesename'] ]

    if "img" in json_data.keys():
        txt_content=msg_json['img']= json_data['img']
        msg_json['markdown']['title']="图片"
    else:
        txt_content=json_data['msg']['text']
        img=get_http_imgurl_from_text(txt_content)
        # img=extract_link(txt_content)
        if img is not None:
            msg_json['img']=img
            msg_json['markdown']['title']="图片"
        else:#真的不是图片
            msg_json['markdown']['title']=txt_content[:14]

    msg_json['markdown']['text']=txt_content
    msg_json['groupid']= 群号
    
    msg_json['cmd']="showmsg"
    msg_json['name']=get_pinyin(msg_json['chinesename'])
    return msg_json


def format_wss(msg_json,group_name_replace_dict_wss={},debug=False):
    if msg_json['type'] == "text":
        if debug: print("1.type is text")
        msg_json_result = convert_txt_to_markdown(msg_json['markdown']['text'])
        if debug: print("2.new json")
    else:
        if debug: print("1.type is image")
        msg_json_result = convert_img_to_markdown(msg_json['markdown']['image'])

    from_chinese_name = msg_json['markdown']['from']
    if debug:print(f"3.get chinesename={from_chinese_name}")
    msg_json_result['groupid'] = msg_json['markdown']['id']
    if debug:print(f"5.groupid={msg_json_result['groupid'] }")

    msg_json_result['chinesename'] = group_name_replace_dict_wss[from_chinese_name] if from_chinese_name in group_name_replace_dict_wss.keys() else from_chinese_name
    
    msg_json_result['name'] = "".join(get_pinyin(msg_json_result['chinesename'] ))
    if debug:print(f"4.get name={msg_json_result['name'] }")

    msg_json_result['cmd'] = "showwss"
    return msg_json_result


def convert_txt_to_markdown(txt):
    mk = {
        'msgtype': 'markdown',
        'markdown': {
            'title': '',
            'text': ' ',
            'at': {},
        }
    }
    mk['markdown']['text'] = txt
    mk['markdown']['title'] = txt[:14]
    return mk


def convert_img_to_markdown(image_url):
    mk = {
        'msgtype': 'markdown',
        'markdown': {
            'title': '',
            'text': ' ',
            'at': {},
        }
    }
    mk['markdown']['text'] = image_url
    mk['markdown']['title'] = "图片"
    mk['img'] = image_url
    return mk



# 解析 INI 配置文件
def parse_ini_config(ini_config_file):
    ini_config = configparser.ConfigParser()
    ini_config.read(ini_config_file, encoding="utf-8")
    return ini_config


def get_config_value(config, section, option,debug=False):
    try:
        txt = config.get(section, option)
        
    except (configparser.NoSectionError, configparser.NoOptionError):
        if debug: print(f"读取字典{config}/{section}/{option}失败，使用默认空值")
        txt = ""
    return txt

def config2dict(config, section:str, option:str, sep="|", sub_sep="*", debug=False):
    #单值
    txt = get_config_value(config, section, option)
    #txt = "47904542011*特定群名|47696677108*特定输出|52625333512*涨停猫|47904542011*输入群"
    txt_list = txt.strip(sep).split(sep)

    result = {}
    for item in txt_list:
        key_value = item.split(sub_sep,1)
        if len(key_value) == 1:
            key = key_value[0]
            if debug: print("只有一项，赋空值")
            result[key] = ""
        else:
            key, value = key_value
            result[key] = value
    if debug: print(f"config2dict 读取字典{config}/{section}/{option} = ", result)
    return result


def get_pinyin(string):

    def is_chinese(char):
        return 'u4e00' <= char <= '\u9fa5'

    result = ""
    for char in string:
        if not is_chinese(char):
            #print(char+"is notcn")
            result += char
        else:
            pinyin = lazy_pinyin(char)
            #print("pinyin-",pinyin)
            result += pinyin[0] if pinyin else char
    return result


def create_dataframe_from_ini(ini_config, cfg_columns=['from_group_name', 'from', 'to', 'prefix', 'fromuser']):
    data = []
    for section in ini_config.sections():

        tmp_list = []
        for col in cfg_columns:
            tmp_list.append(get_config_value(ini_config, section, col))

        #print(tmp_list)
        data.append(tmp_list)

    #print(data)
    #print(data[:5])
    df = pd.DataFrame(data, columns=cfg_columns)
    df['pinyin'] = df['from_group_name'].apply(lambda x: get_pinyin(x))
    return df


import psutil
import socket
import subprocess
import time
import hashlib, base64
import requests
import json
import hmac, urllib


def send_dingtalk_message(access_token, secret, msg_text):
    url = f"https://oapi.dingtalk.com/robot/send?access_token={access_token}"

    timestamp = str(round(time.time() * 1000))
    string_to_sign = timestamp + "\n" + secret
    hmac_code = hashlib.sha256(string_to_sign.encode()).digest()
    signature = base64.b64encode(hmac_code).decode()

    headers = {"Content-Type": "application/json"}

    payload = {"msgtype": "text", "text": {"content": msg_text}, "at": {"isAtAll": False}}

    params = {"access_token": access_token, "timestamp": timestamp, "sign": signature}
    print("url:", url, "params:", params, "headers:", headers, "payload:", payload)
    response = requests.post(url, params=params, headers=headers, data=json.dumps(payload))
    result = json.loads(response.text)
    print("result:", result, "response.txt:", response.text)
    return response.text


# webhook = "Your_Webhook_URL"
# sign = "Your_Secret_Key"
# message = "Your_Message"

# response = send_dingtalk_message(webhook, sign, message)

# print(response)


def calculateSignature(secret):
    timestamp = int(time.time() * 1000)
    stringToSign = str(timestamp) + '\n' + secret
    hmacSha256 = hmac.new(secret.encode('utf-8'), stringToSign.encode('utf-8'), hashlib.sha256)
    return base64.encodebytes(hmacSha256.digest()).rstrip().decode("utf-8")


def get_timestamp_sign(secret):
    timestamp = str(round(time.time() * 1000))
    # secret = # SEC开头的
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return (timestamp, sign)


def 获取带签URL(webhookstr, signstr):
    timestamp, sign = get_timestamp_sign(signstr)
    webhook = webhookstr + "&timestamp=" + timestamp + "&sign=" + sign
    return webhook


def 生成最终url(webhookstr, signstr, mode):

    if mode == 0:  # only 敏感字
        webhook = URL
    elif mode == 1 or mode == 2:  # 敏感字和加签 或 # 敏感字+加签+ip
        # 加签： https://oapi.dingtalk.com/robot/send?access_token=XXXXXX&timestamp=XXX&sign=XXX
        webhook = 获取带签URL(webhookstr, signstr)
    else:
        webhook = ""
        print("error! mode:   ", mode, "  webhook :  ", webhook)
    return webhook


def get_message(content, is_send_all):
    # 和类型相对应，具体可以看文档 ：https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq
    # 可以设置某个人的手机号，指定对象发送
    message = {
        "msgtype": "text",  # 有text, "markdown"、link、整体跳转ActionCard 、独立跳转ActionCard、FeedCard类型等
        "text": {
            "content": content  # 消息内容
        },
        "at": {
            "atMobiles": [
                "1862*8*****6",
            ],
            "isAtAll": is_send_all  # 是否是发送群中全体成员
        }
    }
    # print(message)
    return message


def lyy_send_ding_message(webhookstr, signstr, content, 是否图片, is_send_all):
    #print("进入send_ding_message处理dd信息")
    baseurl = "https://oapi.dingtalk.com/robot/send?access_token="
    # 请求的URL，WebHook地址
    最终url = 生成最终url(baseurl + webhookstr, signstr, 1)
    # 主要模式有 0 ： 敏感字 1：# 敏感字 +加签 3：敏感字+加签+IP

    # print("最终提交的URL=: ",最终url)
    # 构建请求头部
    header = {"Content-Type": "application/json", "Charset": "UTF-8"}
    # 构建请求数据
    if 是否图片:
        msg_json = lyy_make_markdown_img_json(content)

    msg_json = get_message(content, is_send_all) if not 是否图片 else lyy_make_markdown_img_json(content)

    # 对请求的数据进行json封装
    json_str = json.dumps(msg_json)
    # 发送请求
    info = requests.post(url=最终url, data=json_str, headers=header)
    print("token=", webhookstr)
    # 打印返回的结果
    return info.text


def lyy_send_msg_json_by_pass_hosts(webhookstr, signstr, msg_json, debug=False):
    #print("进入send_ding_message处理dd信息")
    warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

    baseurl = "https://106.11.23.24/robot/send?access_token="
    最终url = 生成最终url(baseurl + webhookstr, signstr, 1)
    header = {"Host": "oapi.dingtalk.com", "Content-Type": "application/json", "Charset": "UTF-8"}
    json_str = json.dumps(msg_json)
    if debug and "screenshot" in json_str:
        print("发送前，json_str_img=" + json_str)
    # 设置自定义DNS服务器
    #socket.getaddrinfo = lambda host, port, family=0, type=0, proto=0, flags=0: [(2, 1, 6, '', (host, port))]
    #print("json_str=", json_str)
    info = requests.post(url=最终url, data=json_str, headers=header, verify=False)
    return info.text


def lyy_send_msg_json(webhookstr, signstr, msg_json):
    #print("进入send_ding_message处理dd信息")
    baseurl = "https://oapi.dingtalk.com/robot/send?access_token="
    # 请求的URL，WebHook地址
    最终url = 生成最终url(baseurl + webhookstr, signstr, 1)
    # 主要模式有 0 ： 敏感字 1：# 敏感字 +加签 3：敏感字+加签+IP

    # print("最终提交的URL=: ",最终url)
    # 构建请求头部
    header = {"Content-Type": "application/json", "Charset": "UTF-8"}
    # 构建请求数据

    # 对请求的数据进行json封装
    json_str = json.dumps(msg_json)
    # 发送请求
    info = requests.post(url=最终url, data=json_str, headers=header)
    # 打印返回的结果
    return info.text


def lyy_make_markdown_img_json(content):
    message = {"msgtype": "markdown", "markdown": {"title": "。", "text": "####  \n> \n> ![screenshot](" + content + ")\n> "}, "at": {"isAtAll": False}}
    # print(message)
    return message


def get_headers_payload_params(access_token, secret, content, display=False):
    timestamp = str(round(time.time() * 1000))
    string_to_sign = timestamp + "\n" + secret
    hmac_code = hashlib.sha256(string_to_sign.encode()).digest()
    signature = base64.b64encode(hmac_code).decode()
    headers = {"Content-Type": "application/json"}
    payload = {"msgtype": "text", "text": {"content": content}, "at": {"isAtAll": False}}
    params = {"access_token": access_token, "timestamp": timestamp, "sign": signature}
    if display: print(headers, payload, params)
    return headers, payload, params

def get_http_imgurl_from_text(msg_text,debug=False):
    # 定义正则表达式模式
    pattern = r'(https?://(tc|gchat|static).*(jpg|auth_bizType=IM|png|jpg|/0))'
    match = re.search(pattern, msg_text)
    if match:
        matched_text = match.group()
        if debug: print(f"匹配成功", match.group())
        return matched_text


def msg_json_from_text_or_imgurl(msg_text,debug=False):
    # 定义正则表达式模式
    pattern = r'(https://(gchat|static).*(jpg|auth_bizType=IM|png|jpg|/0))'
    match = re.search(pattern, msg_text)
    if match:
        matched_text = match.group()
        if debug: print(f"匹配成功", match.group())

        is_pic = True
        msg_json = message = {"msgtype": "markdown", "markdown": {"title": "[图片]", "text": "####  \n> \n> ![screenshot](" + matched_text + ")\n> "}, "at": {"isAtAll": False}}
    else:
        if debug: print("非https图片链接")
        msg_json = {"msgtype": "text", "text": {"content": msg_text}, "at": {"isAtAll": False}}
    return msg_json


def remove_time_from_text(text):
    # 匹配时间格式的正则表达式
    time_pattern = r"\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{2}:\d{2}|\d{4}-\d{1,2}-\d{1,2}|\d{1,2}:\d{2}:\d{2}|(?=\s)"

    # 使用正则表达式替换时间格式为空字符串
    clean_text = re.sub(time_pattern, "", text).strip().lstrip(".")

    return clean_text


#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# create time: 07/01/2018 11:35
__author__ = 'Devin - https://zhuifengshen.github.io'

import re
import sys
import json
import time
import logging
import requests
import urllib
import hmac
import base64
import hashlib
import queue
import warnings

warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

_ver = sys.version_info
is_py3 = (_ver[0] == 3)

try:
    quote_plus = urllib.parse.quote_plus
except AttributeError:
    quote_plus = urllib.quote_plus

try:
    JSONDecodeError = json.decoder.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError


def is_not_null_and_blank_str(content):
    """
    非空字符串
    :param content: 字符串
    :return: 非空 - True，空 - False

    >>> is_not_null_and_blank_str('')
    False
    >>> is_not_null_and_blank_str(' ')
    False
    >>> is_not_null_and_blank_str('  ')
    False
    >>> is_not_null_and_blank_str('123')
    True
    """
    if content and content.strip():
        return True
    else:
        return False


class DingtalkChatbot(object):
    """
    钉钉群自定义机器人（每个机器人每分钟最多发送20条），支持文本（text）、连接（link）、markdown三种消息类型！
    """

    def __init__(self, webhook, secret=None, pc_slide=False, fail_notice=False):
        """
        机器人初始化
        :param webhook: 钉钉群自定义机器人webhook地址
        :param secret: 机器人安全设置页面勾选“加签”时需要传入的密钥
        :param pc_slide: 消息链接打开方式，默认False为浏览器打开，设置为True时为PC端侧边栏打开
        :param fail_notice: 消息发送失败提醒，默认为False不提醒，开发者可以根据返回的消息发送结果自行判断和处理
        """
        super(DingtalkChatbot, self).__init__()
        self.headers = {"Host": "oapi.dingtalk.com", 'Content-Type': 'application/json; charset=utf-8', 'Connection': 'close'}  # fix issue #53
        self.queue = queue.Queue(20)  # 钉钉官方限流每分钟发送20条信息
        self.webhook = webhook.replace("oapi.dingtalk.com", "106.11.23.24")

        self.secret = secret
        self.pc_slide = pc_slide
        self.fail_notice = fail_notice
        self.start_time = time.time()  # 加签时，请求时间戳与请求时间不能超过1小时，用于定时更新签名
        if self.secret is not None and self.secret.startswith('SEC'):
            self.update_webhook()

    def update_webhook(self):
        """
        钉钉群自定义机器人安全设置加签时，签名中的时间戳与请求时不能超过一个小时，所以每个1小时需要更新签名
        """
        if is_py3:
            timestamp = round(self.start_time * 1000)
            string_to_sign = '{}\n{}'.format(timestamp, self.secret)
            hmac_code = hmac.new(self.secret.encode(), string_to_sign.encode(), digestmod=hashlib.sha256).digest()
        else:
            timestamp = round(self.start_time * 1000)
            secret_enc = bytes(self.secret).encode('utf-8')
            string_to_sign = '{}\n{}'.format(timestamp, self.secret)
            string_to_sign_enc = bytes(string_to_sign).encode('utf-8')
            hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()

        sign = quote_plus(base64.b64encode(hmac_code))
        if 'timestamp' in self.webhook:
            self.webhook = '{}&timestamp={}&sign={}'.format(self.webhook[:self.webhook.find('&timestamp')], str(timestamp), sign)  # 更新时间戳
        else:
            self.webhook = '{}&timestamp={}&sign={}'.format(self.webhook, str(timestamp), sign)  # 首次初始化

    def msg_open_type(self, url):
        """
        消息链接的打开方式
        1、默认或不设置时，为浏览器打开：pc_slide=False
        2、在PC端侧边栏打开：pc_slide=True
        """
        encode_url = quote_plus(url)
        if self.pc_slide:
            final_link = 'dingtalk://dingtalkclient/page/link?url={}&pc_slide=true'.format(encode_url)
        else:
            final_link = 'dingtalk://dingtalkclient/page/link?url={}&pc_slide=false'.format(encode_url)
        return final_link

    def send_text(self, msg, is_at_all=False, at_mobiles=[], at_dingtalk_ids=[], is_auto_at=True):
        """
        text类型
        :param msg: 消息内容
        :param is_at_all: @所有人时：true，否则为false（可选）
        :param at_mobiles: 被@用户的手机号
        :param at_dingtalk_ids: 被@用户的UserId（企业内部机器人可用，可选）
        :param is_auto_at: 是否自动在msg内容末尾添加@手机号，默认自动添加，也可设置为False，然后自行在msg内容中自定义@手机号的位置，才有@效果，支持同时@多个手机号（可选）
        :return: 返回消息发送结果
        """
        data = {"msgtype": "text", "at": {}}
        if is_not_null_and_blank_str(msg):
            data["text"] = {"content": msg}
        else:
            logging.error("text类型，消息内容不能为空！")
            raise ValueError("text类型，消息内容不能为空！")

        if is_at_all:
            data["at"]["isAtAll"] = is_at_all

        if at_mobiles:
            at_mobiles = list(map(str, at_mobiles))
            data["at"]["atMobiles"] = at_mobiles
            if is_auto_at:
                mobiles_text = '\n@' + '@'.join(at_mobiles)
                data["text"]["content"] = msg + mobiles_text

        if at_dingtalk_ids:
            at_dingtalk_ids = list(map(str, at_dingtalk_ids))
            data["at"]["atUserIds"] = at_dingtalk_ids

        logging.debug('text类型：%s' % data)
        return self.post(data)

    def send_image(self, pic_url):
        """
        image类型
        :param pic_url: 图片链接
        :return: 返回消息发送结果
        """
        if is_not_null_and_blank_str(pic_url):
            data = {"msgtype": "image", "image": {"picURL": pic_url}}
            logging.debug('image类型：%s' % data)
            return self.post(data)
        else:
            logging.error("image类型中图片链接不能为空！")
            raise ValueError("image类型中图片链接不能为空！")

    def send_link(self, title, text, message_url, pic_url=''):
        """
        link类型
        :param title: 消息标题
        :param text: 消息内容（如果太长自动省略显示）
        :param message_url: 点击消息触发的URL
        :param pic_url: 图片URL（可选）
        :return: 返回消息发送结果

        """
        if all(map(is_not_null_and_blank_str, [title, text, message_url])):
            data = {"msgtype": "link", "link": {"text": text, "title": title, "picUrl": pic_url, "messageUrl": self.msg_open_type(message_url)}}
            logging.debug('link类型：%s' % data)
            return self.post(data)
        else:
            logging.error("link类型中消息标题或内容或链接不能为空！")
            raise ValueError("link类型中消息标题或内容或链接不能为空！")

    def send_markdown(self, title, text, is_at_all=False, at_mobiles=[], at_dingtalk_ids=[], is_auto_at=True):
        """
        markdown类型
        :param title: 首屏会话透出的展示内容
        :param text: markdown格式的消息内容
        :param is_at_all: @所有人时：true，否则为：false（可选）
        :param at_mobiles: 被@人的手机号
        :param at_dingtalk_ids: 被@用户的UserId（企业内部机器人可用，可选）
        :param is_auto_at: 是否自动在text内容末尾添加@手机号，默认自动添加，也可设置为False，然后自行在text内容中自定义@手机号的位置，才有@效果，支持同时@多个手机号（可选）
        :return: 返回消息发送结果
        """
        if all(map(is_not_null_and_blank_str, [title, text])):
            # 给Mardown文本消息中的跳转链接添加上跳转方式
            text = re.sub(r'(?<!!)\[.*?\]\((.*?)\)', lambda m: m.group(0).replace(m.group(1), self.msg_open_type(m.group(1))), text)
            data = {"msgtype": "markdown", "markdown": {"title": title, "text": text}, "at": {}}
            if is_at_all:
                data["at"]["isAtAll"] = is_at_all

            if at_mobiles:
                at_mobiles = list(map(str, at_mobiles))
                data["at"]["atMobiles"] = at_mobiles
                if is_auto_at:
                    mobiles_text = '\n@' + '@'.join(at_mobiles)
                    data["markdown"]["text"] = text + mobiles_text

            if at_dingtalk_ids:
                at_dingtalk_ids = list(map(str, at_dingtalk_ids))
                data["at"]["atUserIds"] = at_dingtalk_ids

            logging.debug("markdown类型：%s" % data)
            return self.post(data)
        else:
            logging.error("markdown类型中消息标题或内容不能为空！")
            raise ValueError("markdown类型中消息标题或内容不能为空！")

    def send_action_card(self, action_card):
        """
        ActionCard类型
        :param action_card: 整体跳转ActionCard类型实例或独立跳转ActionCard类型实例
        :return: 返回消息发送结果
        """
        if isinstance(action_card, ActionCard):
            data = action_card.get_data()

            if "singleURL" in data["actionCard"]:
                data["actionCard"]["singleURL"] = self.msg_open_type(data["actionCard"]["singleURL"])
            elif "btns" in data["actionCard"]:
                for btn in data["actionCard"]["btns"]:
                    btn["actionURL"] = self.msg_open_type(btn["actionURL"])

            logging.debug("ActionCard类型：%s" % data)
            return self.post(data)
        else:
            logging.error("ActionCard类型：传入的实例类型不正确，内容为：{}".format(str(action_card)))
            raise TypeError("ActionCard类型：传入的实例类型不正确，内容为：{}".format(str(action_card)))

    def send_feed_card(self, links):
        """
        FeedCard类型
        :param links: FeedLink实例列表 or CardItem实例列表
        :return: 返回消息发送结果
        """
        if not isinstance(links, list):
            logging.error("FeedLink类型：传入的数据格式不正确，内容为：{}".format(str(links)))
            raise ValueError("FeedLink类型：传入的数据格式不正确，内容为：{}".format(str(links)))

        link_list = []
        for link in links:
            # 兼容：1、传入FeedLink实例列表；2、CardItem实例列表；
            if isinstance(link, FeedLink) or isinstance(link, CardItem):
                link = link.get_data()
                link['messageURL'] = self.msg_open_type(link['messageURL'])
                link_list.append(link)
            else:
                logging.error("FeedLink类型，传入的数据格式不正确，内容为：{}".format(str(link)))
                raise ValueError("FeedLink类型，传入的数据格式不正确，内容为：{}".format(str(link)))

        data = {"msgtype": "feedCard", "feedCard": {"links": link_list}}
        logging.debug("FeedCard类型：%s" % data)
        return self.post(data)

    def post(self, data):
        """
        发送消息（内容UTF-8编码）
        :param data: 消息数据（字典）
        :return: 返回消息发送结果
        """
        print("plan to post, data=", data)
        now = time.time()

        # 钉钉自定义机器人安全设置加签时，签名中的时间戳与请求时不能超过一个小时，所以每个1小时需要更新签名
        if now - self.start_time >= 3600 and self.secret is not None and self.secret.startswith('SEC'):
            self.start_time = now
            self.update_webhook()

        # 钉钉自定义机器人现在每分钟最多发送20条消息
        self.queue.put(now)
        if self.queue.full():
            elapse_time = now - self.queue.get()
            if elapse_time < 60:
                sleep_time = int(60 - elapse_time) + 1
                logging.debug('钉钉官方限制机器人每分钟最多发送20条，当前发送频率已达限制条件，休眠 {}s'.format(str(sleep_time)))
                time.sleep(sleep_time)

        try:
            post_data = json.dumps(data)

            response = requests.post(self.webhook, headers=self.headers, data=post_data, verify=False)
        except requests.exceptions.HTTPError as exc:
            logging.error("消息发送失败， HTTP error: %d, reason: %s" % (exc.response.status_code, exc.response.reason))
            raise
        except requests.exceptions.ConnectionError:
            logging.error("消息发送失败，HTTP connection error!")
            raise
        except requests.exceptions.Timeout:
            logging.error("消息发送失败，Timeout error!")
            raise
        except requests.exceptions.RequestException:
            logging.error("消息发送失败, Request Exception!")
            raise
        else:
            try:
                result = response.json()
            except JSONDecodeError:
                logging.error("服务器响应异常，状态码：%s，响应内容：%s" % (response.status_code, response.text))
                return {'errcode': 500, 'errmsg': '服务器响应异常'}
            else:
                logging.debug('发送结果：%s' % result)
                # 消息发送失败提醒（errcode 不为 0，表示消息发送异常），默认不提醒，开发者可以根据返回的消息发送结果自行判断和处理
                if self.fail_notice and result.get('errcode', True):
                    time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    error_data = {"msgtype": "text", "text": {"content": "[异常通知]钉钉机器人消息发送失败，失败时间：%s，失败原因：%s，要发送的消息：%s，请及时跟进，谢谢!" % (time_now, result['errmsg'] if result.get('errmsg', False) else '未知异常', post_data)}, "at": {"isAtAll": False}}
                    logging.error("消息发送失败，自动通知：%s" % error_data)
                    requests.post(self.webhook, headers=self.headers, data=json.dumps(error_data))
                return result


class ActionCard(object):
    """
    ActionCard类型消息格式（整体跳转、独立跳转）
    """

    def __init__(self, title, text, btns, btn_orientation=0, hide_avatar=0):
        """
        ActionCard初始化
        :param title: 首屏会话透出的展示内容
        :param text: markdown格式的消息
        :param btns: 按钮列表：（1）按钮数量为1时，整体跳转ActionCard类型；（2）按钮数量大于1时，独立跳转ActionCard类型；
        :param btn_orientation: 0：按钮竖直排列，1：按钮横向排列（可选）
        :param hide_avatar: 0：正常发消息者头像，1：隐藏发消息者头像（可选）
        """
        super(ActionCard, self).__init__()
        self.title = title
        self.text = text
        self.btn_orientation = btn_orientation
        self.hide_avatar = hide_avatar
        btn_list = []
        for btn in btns:
            if isinstance(btn, CardItem):
                btn_list.append(btn.get_data())
        if btn_list:
            btns = btn_list  # 兼容：1、传入CardItem列表；2、传入数据字典列表
        self.btns = btns

    def get_data(self):
        """
        获取ActionCard类型消息数据（字典）
        :return: 返回ActionCard数据
        """
        if all(map(is_not_null_and_blank_str, [self.title, self.text])) and len(self.btns):
            if len(self.btns) == 1:
                # 整体跳转ActionCard类型
                data = {"msgtype": "actionCard", "actionCard": {"title": self.title, "text": self.text, "hideAvatar": self.hide_avatar, "btnOrientation": self.btn_orientation, "singleTitle": self.btns[0]["title"], "singleURL": self.btns[0]["actionURL"]}}
                return data
            else:
                # 独立跳转ActionCard类型
                data = {"msgtype": "actionCard", "actionCard": {"title": self.title, "text": self.text, "hideAvatar": self.hide_avatar, "btnOrientation": self.btn_orientation, "btns": self.btns}}
                return data
        else:
            logging.error("ActionCard类型，消息标题或内容或按钮数量不能为空！")
            raise ValueError("ActionCard类型，消息标题或内容或按钮数量不能为空！")


class FeedLink(object):
    """
    FeedCard类型单条消息格式（已废弃，直接使用 CardItem 即可）
    """

    def __init__(self, title, message_url, pic_url):
        """
        初始化单条消息文本
        :param title: 单条消息文本
        :param message_url: 点击单条信息后触发的URL
        :param pic_url: 点击单条消息后面图片触发的URL
        """
        super(FeedLink, self).__init__()
        self.title = title
        self.message_url = message_url
        self.pic_url = pic_url

    def get_data(self):
        """
        获取FeedLink消息数据（字典）
        :return: 本FeedLink消息的数据
        """
        if all(map(is_not_null_and_blank_str, [self.title, self.message_url, self.pic_url])):
            data = {"title": self.title, "messageURL": self.message_url, "picURL": self.pic_url}
            return data
        else:
            logging.error("FeedCard类型单条消息文本、消息链接、图片链接不能为空！")
            raise ValueError("FeedCard类型单条消息文本、消息链接、图片链接不能为空！")


class CardItem(object):
    """
    ActionCard和FeedCard消息类型中的子控件
    
    注意：
    1、发送FeedCard消息时，参数pic_url必须传入参数值；
    2、发送ActionCard消息时，参数pic_url不需要传入参数值；
    """

    def __init__(self, title, url, pic_url=None):
        """
        CardItem初始化
        @param title: 子控件名称
        @param url: 点击子控件时触发的URL
        @param pic_url: FeedCard的图片地址，ActionCard时不需要，故默认为None
        """
        super(CardItem, self).__init__()
        self.title = title
        self.url = url
        self.pic_url = pic_url

    def get_data(self):
        """
        获取CardItem子控件数据（字典）
        @return: 子控件的数据
        """
        if all(map(is_not_null_and_blank_str, [self.title, self.url, self.pic_url])):
            # FeedCard类型
            data = {"title": self.title, "messageURL": self.url, "picURL": self.pic_url}
            return data
        elif all(map(is_not_null_and_blank_str, [self.title, self.url])):
            # ActionCard类型
            data = {"title": self.title, "actionURL": self.url}
            return data
        else:
            logging.error("CardItem是ActionCard的子控件时，title、url不能为空；是FeedCard的子控件时，title、url、pic_url不能为空！")
            raise ValueError("CardItem是ActionCard的子控件时，title、url不能为空；是FeedCard的子控件时，title、url、pic_url不能为空！")

def dd_to_db(msg_json, 替换字典, cmd,groupid="0", debug=False):
    mysql_text = lyytext.batch_replace_text_by_dict(msg_json["markdown"]["text"], 替换字典)
    dd_to_SQLite(engine,mysql_text, msg_json['chinesename'], msg_json['name'], cmd,groupid=groupid, debug=debug)
    dd_to_MySql(engine,mysql_text, msg_json['chinesename'], msg_json['name'], cmd,groupid=groupid, debug=debug)

def dd_to_SQLite(msg_json, msg_text, conn_text=None, debug=False):
    if debug: print("in dd_to_SQLite",msg_json)
    中文群名= msg_json["chinesename"]
    群拼音=msg_json["name"]
    cmd=msg_json["cmd"]
    groupid = msg_json["groupid"]

    conn = sqlite3.connect(conn_text)

    if debug: print("    # SQLite创建数据库dddata.db")
    
    cursor = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if debug: print("    # SQLite创建表stock_info")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            name TEXT,
            chinesename TEXT,
            new TEXT,
            groupid TEXT,
            message TEXT
        )
    """)
    if debug: print("sqlite准备查询")

    cursor.execute("INSERT INTO stock_info (time, name, chinesename, new, groupid, message) VALUES (?, ?, ?, ?, ?, ?)", (current_time, 群拼音, 中文群名, cmd, groupid, msg_text))
    affected_rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return affected_rows



def dd_to_MySql(engine,msg_text, 中文群名, 群拼音, cmd,groupid="0", debug=False):
    debug=True
    # 创建MySQL连接
    # conn = engine.connect()
    # if "http" not in msg_text:
    #     from dd01msg import recovery_text_mysql
    #     msg_text = recovery_text_mysql(msg_text,mysql替换文本对数组)
    if len(msg_text)<1:
        if debug: print("in dd_to_MySql, msg_text<1")
        return
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if debug: print("# 插入数据到 MySQL")
    insert_query = text("INSERT INTO stock_info (time, name, chinesename, new, groupid, message) VALUES (:time, :name, :chinesename, :new, :groupid, :message) ON DUPLICATE KEY UPDATE time = IF(groupid = :groupid AND message = :message AND time >= NOW() - INTERVAL 1 MINUTE, VALUES(time), time);")
    params = {
        'time': current_time,
        'name': 群拼音,
        'chinesename': 中文群名,
        'new':cmd,
        'groupid': groupid,
        'message': msg_text

    }

    try:
        with engine.begin() as connection:
            result = connection.execute(insert_query, params)
            affected_rows = result.rowcount  # 获取成功插入的行数
            if debug: print(f"mysql Affected rows: {affected_rows}")
            if affected_rows > 0:
                if debug: print("# 插入成功")
                return affected_rows
            else:
                # 插入失败
                return 0
    except Exception as e:
        log("Insert ddmsg to MySQL error. errormsg =" + str(e))


def remove_from_MySql(engine,msg_text, 中文群名, 群拼音, cmd,groupid="0", debug=False):

    # 插入数据到 MySQL
    if debug: print(f"try to delete no specify user's message,pinyin={群拼音},msg={msg_text}")
    insert_query = text(f'delete from stock_info where name="{群拼音}" and message="{msg_text}"')

    try:
        with engine.begin() as connection:
            result = connection.execute(insert_query)
            affected_rows = result.rowcount  # 获取成功插入的行数
            print(f"delete rows: {affected_rows}")
            if affected_rows > 0:
                return affected_rows
            else:
                return 0
    except Exception as e:
        log("delete ddmsg to MySQL error. errormsg =" + str(e))
        return 0



if __name__ == '__main__':

    webhook = "62153505b1635f6f0a0b0ed41fb0f2e0dff5fd9373ce093be85b3f2db262012f"
    sign = "SECeba7ab6bc8fc2341a25034a5d5e703995279ebedb42455f9d4920752f3468701"
    webhook = "62e08928ef4864af0ccff2cc446d2bbd89591493871565db4d9cc2a7f0304a08"
    sign = "SEC37d6650050af983c66c842dbc9c631f879be6629f4e35cb9d95e024f19f6a114"
    t = '.\r\r![screenshot](https://static.dingtalk.com/media/lADPD1Iyci_hm4bNAr7NBLA_1200_702.jpg_620x10000q90g.jpg?auth_bizType=IM)\r\r.'
    msg_json = msg_json_from_text_or_imgurl(t)
    json_str = '{"msgtype": "markdown", "name":"ggggg", "chinese":"ffdddf","markdown": {"title": "[图片]", "text": "ffghhh"}, "at": { "isAtAll": false}}'
    msg_json = json.loads(json_str)
    result = lyy_send_msg_json(webhook, sign, msg_json)
    print(result)
    exit()

    img_str_ddpng = "https://static.dingtalk.com/media/lALPD2BobLJPUpfNAs3NBME_1217_717.png"
    text1 = "这是一条测试消息，来源于lyyddforward main模块"
    img_str_ddauth = "https://static.dingtalk.com/media/lADPD1W_8MbAK1zNAQTNBTw_1340_260.jpg_620x10000q90g.jpg?auth_bizType=IM"

    #msg_json = msg_json_from_text_or_imgurl(img_str)
    #result = lyy_send_ding_message(webhook, sign, text1,False,False)
    #result = lyy_send_ding_message(webhook, sign, img_str, True, False)
    err_img = "https://static.dingtalk.com/media/lALPD2BobLXfeJ_M8M0B_g_510_240.png"

    json_str = '{"msgtype": "markdown", "markdown": {"title": "[图片]", "text": ""}, "at": { "isAtAll": false}}'
    msg_json = json.loads(json_str)

    #message = {"msgtype": "markdown", "markdown": {"title": "。", "text": "####  \n> \n> ![screenshot](" + content + ")\n> "}, "at": {"isAtAll": False}}

    print(str(msg_json))
    #msg_json['markdown']['text'] = "![screenshot](" + err_img + ")"
    #print(str(msg_json))

    img_qq = "https://gchat.qpic.cn/gchatpic_new/724710691/724710691-2731142198-DC957B415123569CF8016372AD4E8F88/0"
    img_brk = "screenshot](https://static.dingtalk.com/media/lADPD2BobMG4eWPNAR7NAn8_639_286.jpg_620x10000q90g.jpg?auth_bizType=IM)\r\r/n"
    #img_brk = "https://gchat.qpic.cn/gchatpic_new/724710691/724710691-2731142198-075F3A585BF863BC3F43ED7C9499185B/0"

    msg_json = msg_json_from_text_or_imgurl(img_str_ddauth)
    result = lyy_send_msg_json(webhook, sign, msg_json)
    print(result)
    exit()
    task_dict = {'jiepan': 'D:/Soft/_lyytools/_jiepan/_jiepan.exe', 'gui-only': 'D:/Soft/_lyytools/gui-only/gui-only.exe', 'kingtrader': 'D:/Soft/_Stock/KTPro/A.点我登录.exe'}
    stopped = check_processes(task_dict)
    print("stopped=", stopped)

# if __name__ == '__main__':
# cfg_path = r'D:\UserData\resource\ddForward'
# ini_config_file = cfg_path + "/" + "ddForward.ini"
# ini_config = parse_ini_config(ini_config_file)
# df = create_dataframe_from_ini(ini_config)
# # 打印 DataFrame
# print(df[:5])
