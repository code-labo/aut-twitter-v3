import pandas as pd
import os
import json
import random
import numpy as np
import logging
import sys

import smtplib
from email.mime.text import MIMEText
import traceback


class ConfigSampler():
    def __init__(self,config_path):
        self.config_path=config_path
        with open(config_path,"r",encoding="utf-8") as f:
            json_data=f.read()
        self.config=json.loads(self._remove_comments(json_data))

    def _remove_comments(self,jsonc_text):
        lines = jsonc_text.split('\n')
        cleaned_lines = []
        for line in lines:
            index = line.find('//')
            if index != -1:
                line = line[:index]
            cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)        
    
    def sample(self):
        """
        configから各パラメータを確率的にサンプリングする
        """

        #>> serach & favoのパラメータのサンプリング >>
        searchfavo_cfg=self.config["auto_twitter_config"]["process_searchfavo_config"]
        searchfavo_cfg["is_run"]=True if random.random()<searchfavo_cfg["process_run_p"] else False #実行するかどうか
        
        searchfavo_cfg["max_favo_num"]=round(np.random.normal(loc=searchfavo_cfg["mean_favo_num"],scale=searchfavo_cfg["std_favo_num"]))
        searchfavo_cfg["max_favo_num"]=1 if searchfavo_cfg["max_favo_num"]<1 else searchfavo_cfg["max_favo_num"]
        
        #検索ワードの選出
        search_words=[]
        for keys in searchfavo_cfg["search_word"].values():
            search_words.append(
                random.choice(keys.split(","))
            )
        random.shuffle(search_words)
        searchfavo_cfg["search_word"]=",".join(search_words)

        #検索タブの選出
        search_tabs=[key for key in random.choice(list(searchfavo_cfg["search_tab"].values())).split(",")]
        random.shuffle(search_tabs)
        searchfavo_cfg["search_tab"]=",".join(search_tabs)

        self.config["auto_twitter_config"]["process_searchfavo_config"]=searchfavo_cfg
        #>> serach & favoのパラメータのサンプリング >>


        #>> favo timelineのパラメータサンプリング
        favotl_cfg=self.config["auto_twitter_config"]["process_favotl_config"]
        favotl_cfg["is_run"]=True if random.random()<favotl_cfg["process_run_p"] else False #実行するかどうか
        
        favotl_cfg["max_favo_num"]=round(np.random.normal(loc=favotl_cfg["mean_favo_num"],scale=favotl_cfg["std_favo_num"]))
        favotl_cfg["max_favo_num"]=1 if favotl_cfg["max_favo_num"]<1 else favotl_cfg["max_favo_num"]
        self.config["auto_twitter_config"]["process_favotl_config"]=favotl_cfg
        #>> favo timelineのパラメータサンプリング



    def __del__(self):
        with open(self.config_path.replace(".jsonc","_sampled.json"),"w",encoding="utf-8") as f:
            json.dump(self.config,f,indent=4,ensure_ascii=False)


class Color:
    BLACK          = '\033[30m'#(文字)黒
    RED            = '\033[31m'#(文字)赤
    GREEN          = '\033[32m'#(文字)緑
    YELLOW         = '\033[33m'#(文字)黄
    BLUE           = '\033[34m'#(文字)青
    MAGENTA        = '\033[35m'#(文字)マゼンタ
    CYAN           = '\033[36m'#(文字)シアン
    WHITE          = '\033[37m'#(文字)白
    COLOR_DEFAULT  = '\033[39m'#文字色をデフォルトに戻す
    BOLD           = '\033[1m'#太字
    UNDERLINE      = '\033[4m'#下線
    INVISIBLE      = '\033[08m'#不可視
    REVERCE        = '\033[07m'#文字色と背景色を反転
    BG_BLACK       = '\033[40m'#(背景)黒
    BG_RED         = '\033[41m'#(背景)赤
    BG_GREEN       = '\033[42m'#(背景)緑
    BG_YELLOW      = '\033[43m'#(背景)黄
    BG_BLUE        = '\033[44m'#(背景)青
    BG_MAGENTA     = '\033[45m'#(背景)マゼンタ
    BG_CYAN        = '\033[46m'#(背景)シアン
    BG_WHITE       = '\033[47m'#(背景)白
    BG_DEFAULT     = '\033[49m'#背景色をデフォルトに戻す
    RESET          = '\033[0m'#全てリセット


def add_single_quote(s:str):
    return f"'{s}'"


def print_view(table_name:str,table:pd.DataFrame,color:Color):
    msg="-"*40+f"{color}{table_name}{Color.RESET}"+"-"*40
    print(f"{msg}\n{table}\n{'-'*(len(msg)-len(f'{color}{Color.RESET}'))}")

def print_tweet(header:str,tweet_info:dict,color:Color):

    msg=""
    msg+="-"*40+f"{color}{header}{Color.RESET}"+"-"*40
    for key,val in tweet_info.items():
        if not key=="tweet_text":
            msg+=("\n"+(f"{key} : {str(val)}"))
        else:
            msg+=("\n"+(f"{key} : \n{str(val)}"))
    msg+=("\n"+f"{'-'*80+'-'*(len(header))}")

    print(msg)

    return msg

def load_filter_words(txt_file_path:str):
    with open(txt_file_path,"r",encoding="utf-8") as f:
        lines=[line.split(",") for line in f.read().splitlines()]
    filter_words=[]
    for line in lines:
        filter_words+=line
    return filter_words

# def load_logs(log_file_path):

#     if not os.path.exists(log_file_path):
#         with open(log_file_path,"w",encoding="utf-8") as f:
#             f.write("")

#     with open(log_file_path,"r",encoding="utf-8") as f:
#         log="".join(f.readlines())
        
#     return log

def write_logs(log_file_path,log):

    if not os.path.exists(log_file_path):
        with open(log_file_path,"w",encoding="utf-8") as f:
            f.write("")

    with open(log_file_path,"r",encoding="utf-8") as f:
        prev_log="".join(f.readlines())

    with open(log_file_path,"w",encoding="utf-8") as f:
        f.write(prev_log+"\n"+log)


def send_gmail_notification(error_message, sender_email, sender_password, recipient_email):
    # メールの設定
    msg = MIMEText(error_message)
    msg['Subject'] = 'Error Notification'
    msg['From'] = sender_email
    msg['To'] = recipient_email

    try:
        # GmailのSMTPサーバーに接続してメールを送信
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print('Error notification email sent successfully!')
    except Exception as e:
        print('Failed to send error notification email.')
        print('Error:', e)
