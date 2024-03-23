"""
"""

import sys
from pathlib import Path
PARENT=str(Path(__file__).parent)
ROOT=str(Path(__file__).parent.parent)
sys.path.append(ROOT)

import datetime
import time
import json
import random

from src.auto_twitter import AutoTwitter
from src.utils import load_filter_words,ConfigSampler,Color,write_logs,send_gmail_notification

def main():

    try:
        msg="#"*40+f"{Color.GREEN}START PROCESS @{datetime.datetime.now()}{Color.RESET}"+"#"*40
        print(msg)

        cfg_sampler=ConfigSampler(f"{ROOT}/config/config.jsonc")
        cfg_sampler.sample()
        cfg_str=json.dumps(cfg_sampler.config,indent=4,ensure_ascii=False)
        log_path=f"{ROOT}/log/process_log.txt"
        write_logs(
            log_path,msg+f"\nconfig:\n{cfg_str}"
        )

        user_cfg=cfg_sampler.config["auto_twitter_config"]["user_config"]
        searchfavo_cfg=cfg_sampler.config["auto_twitter_config"]["process_searchfavo_config"]
        favotl_cfg=cfg_sampler.config["auto_twitter_config"]["process_favotl_config"]
        html_css_value=cfg_sampler.config["auto_twitter_config"]["html_css_value"]
        random_action_cfg=cfg_sampler.config["auto_twitter_config"]["random_action_config"]
        filter_words="".join(list(cfg_sampler.config["auto_twitter_config"]["filter_word"].values())).split(",")

        #>> そもそも実行するかどうか >>
        is_run=searchfavo_cfg["is_run"] or favotl_cfg["is_run"]
        #>> そもそも実行するかどうか >>

        if not is_run: #trueがなければおしまい
            print("="*40,f"{Color.MAGENTA}there is no process{Color.RESET}","="*40)

        elif is_run:

            url="https://twitter.com"
            auto_twitter=AutoTwitter(
                profile_name=user_cfg["profile_name"],
                profile_path=user_cfg["profile_path"],
                account_name=user_cfg["account_name"],
                is_headless=user_cfg["is_headless"]
            )
            auto_twitter.access_url(url=url)


            #>> htmlクラスが変更されていないかチェック >>
            auto_twitter.scroll_page(speed=4)
            is_class_val,msg=auto_twitter.is_html_class(html_classes=html_css_value,log_file_path=log_path)
            if is_class_val:
                msg=f"{Color.GREEN}o{Color.RESET}"*3+"-"*20+f"{Color.GREEN}pass html class test{Color.RESET}"+"-"*20+f"{Color.GREEN}o{Color.RESET}"*3
                print(msg)
                write_logs(log_path,msg)

            else: #変更されていればメールで通知する
                mail_cfg=cfg_sampler.config["auto_twitter_config"]["gmail_config"]
                send_gmail_notification(
                    error_message=msg,
                    sender_email=mail_cfg["sender"],
                    sender_password=mail_cfg["password"],
                    recipient_email=mail_cfg["recipient"]
                )
                exit(1)
            #>> htmlクラスが変更されていないかチェック >>


            #>> 検索＆いいねを実行 >>
            if searchfavo_cfg["is_run"]: 
                print("="*40,f"{Color.GREEN}START Search & Favo{Color.RESET}","="*40)
                search_words=searchfavo_cfg["search_word"].split(",")
                search_tabs=searchfavo_cfg["search_tab"].split(",")

                for word in search_words:
                    auto_twitter.search_tweet(word)
                    time.sleep(random.uniform(3.0,5.0))
                    
                    for tab in search_tabs:
                        auto_twitter.select_tab(tab)
                        time.sleep(random.uniform(2.0,4.0))
                        auto_twitter.scroll_favo(
                            favo_num=searchfavo_cfg["max_favo_num"],
                            favo_p=searchfavo_cfg["favo_probablity"],
                            max_process_seconds=searchfavo_cfg["max_searchfavo_seconds"],
                            filter_words=filter_words,
                            log_file_path=log_path,
                            html_favo_class=html_css_value["favo_icon"],
                            html_text_class=html_css_value["tweet_text"],
                            html_back_class=html_css_value["back_button"],
                            direct_favo_p=random_action_cfg["direct_favo_probability"],
                            favo_onpage_p=random_action_cfg["favo_onpage_probability"],
                            view_comment_p=random_action_cfg["view_comment_probability"],
                            jumpto_account_p=random_action_cfg["jumpto_account_probability"],
                        )
                print("="*40,f"{Color.GREEN}END Search & Favo{Color.RESET}","="*40)
            #>> 検索＆いいねを実行 >>
                        
            #>> タイムラインのいいねを実行 >>
            if favotl_cfg["is_run"]:
                print("="*40,f"{Color.GREEN}START Favo Timeline{Color.RESET}","="*40)
                auto_twitter.select_nav("ホーム")
                time.sleep(random.uniform(3.0,5.0))
                auto_twitter.scroll_favo(
                    favo_num=favotl_cfg["max_favo_num"],
                    favo_p=favotl_cfg["favo_probablity"],
                    max_process_seconds=favotl_cfg["max_favotl_seconds"],
                    filter_words=filter_words,
                    log_file_path=log_path,
                    html_favo_class=html_css_value["favo_icon"],
                    html_text_class=html_css_value["tweet_text"],
                    html_back_class=html_css_value["back_button"],
                    direct_favo_p=random_action_cfg["direct_favo_probability"],
                    favo_onpage_p=random_action_cfg["favo_onpage_probability"],
                    view_comment_p=random_action_cfg["view_comment_probability"],
                    jumpto_account_p=random_action_cfg["jumpto_account_probability"],
                )
                print("="*40,f"{Color.GREEN}END Favo Timeline{Color.RESET}","="*40)
            #>> タイムラインのいいねを実行 >>
                
    except Exception as e:
        print(e)
        write_logs(
            log_file_path=log_path,
            log=str(e)
        )

    finally:
        msg=("#"*40+f"{Color.GREEN}END PROCESS @{datetime.datetime.now()}{Color.RESET}"+"#"*40)
        print(msg)
        write_logs(
            log_path,msg
        )

if __name__=="__main__":
    main()