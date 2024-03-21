import pandas as pd
import os

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
            msg+=("\n"+(f"{key} : {val}"))
        else:
            msg+=("\n"+(f"{key} : \n{val}"))
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

def load_logs(log_file_path):

    if not os.path.exists(log_file_path):
        with open(log_file_path,"w",encoding="utf-8") as f:
            f.write("")

    with open(log_file_path,"r",encoding="utf-8") as f:
        log="".join(f.readlines())
        
    return log

def write_logs(log_file_path,log):
    with open(log_file_path,"w",encoding="utf-8") as f:
        f.write(log)