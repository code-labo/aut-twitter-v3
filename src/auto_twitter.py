from pathlib import Path
ROOT=Path(__file__).parent.parent

import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

import re
from copy import deepcopy
from math import ceil
from tqdm import tqdm
import random
from datetime import datetime

from .driver import init_driver
from.utils import print_tweet,Color,write_logs

class AutoTwitter():


    def __init__(self,profile_name,profile_path,account_name,is_headless=True):
        self.driver=init_driver(
            profile_name=profile_name,
            profile_path=profile_path,
            is_headless=is_headless
        )
        self.wait=WebDriverWait(driver=self.driver, timeout=15)
        self.actions=ActionChains(self.driver)
        self.account_name=account_name

        self.twitter_url="https://twitter.com"

    
    def __del__(self):
        """
        最後にドライバーを閉じる
        """
        print("Driver is closed.")
        self.driver.close()
        self.driver.quit()
        

    def access_url(self,url):
        # self.driver.set_window_size(1280,720)
        self.driver.get(url=url)
        time.sleep(random.uniform(3.5,5.5))

        # #>> ページの拡大率を調整 >>
        # script = "document.body.style.zoom='75%';"
        # self.driver.execute_script(script)
        # time.sleep(1)
        # #>> ページの拡大率を調整 >>


    
    def get_status(self,account_url)->dict:
        """
        アカウントの情報を取得する関数
        """
        status={
            "num_follower":0,
            "num_followed":0
        }

        self.access_url(account_url)

        class_value="css-175oi2r.r-13awgt0.r-18u37iz.r-1w6e6rj" #フォロー中 フォロワーのクラス名. ちょくちょく変わるっぽい
        profile_element=self.driver.find_element(
            by=By.CLASS_NAME,
            value=class_value
            ) #プロフィール要素
        
        ancher_elements=profile_element.find_elements(by=By.TAG_NAME,value="a")
        for ancher in ancher_elements:
            text=ancher.get_attribute("textContent")

            if "フォロー中" in text:
                status["num_followed"]=int(re.sub("\D","",text))
                
            elif "フォロワー" in text:
                status["num_follower"]=int(re.sub("\D","",text))

        return status


        
    def search_tweet(self,keyword=""):
        """
        キーワードの検索
        """
        print("="*25)
        print("***Now Searching...***")
        print(f"keyword : {keyword}")

        ###START テキスト検索の要素を取得
        element_search=None
        element_search_list=self.driver.find_elements(by=By.TAG_NAME,value="input")
        for e in element_search_list:
            if e.get_attribute("type")=="text":
                element_search=e
        ###END

        ###START word検索
        element_search.send_keys(Keys.CONTROL+"a") #一旦綺麗にする. そうしないと連続で検索できない
        time.sleep(random.uniform(0.3,0.8))
        element_search.send_keys(Keys.DELETE)
        time.sleep(random.uniform(0.3,0.8))
        element_search.send_keys(keyword)
        time.sleep(random.uniform(0.3,0.8))
        element_search.send_keys(Keys.ENTER)
        ###END

        time.sleep(abs(random.gauss(mu=2,sigma=0.8)))
        # time.sleep(random.uniform(1.0,2.0))

        print("Seaching OK")
        
    
    def select_tab(self,tab_name="最新"):
        """
        self.search_tweet()の後に実行する

        検索後のタブを選択するメソッド

        -input-
            tab_name:
                [話題, 最新, アカウント, 画像, 動画]の中からタブを選ぶ
        """
        print("="*25)
        element_ancher_list=self.driver.find_elements(by=By.TAG_NAME,value="a") #ancherタグを抽出
        element_tab_list=[]
        for e in element_ancher_list:
            try:
                role=e.get_attribute("role")
                if role=="tab":
                    element_tab_list.append(e)
            except:
                pass
        
        for tab in element_tab_list:
            text=tab.find_element(by=By.TAG_NAME,value="span").get_attribute("textContent") #タブのテキストを調べる
            if tab_name in text:
                tab.send_keys(Keys.ENTER) #タブをクリック
                break

        print(f"moved to {tab_name} tab")
        time.sleep(abs(random.gauss(2,0.8)))
        # time.sleep(random.uniform(1.0,2.0))


    def scroll_page(self,speed=5, is_up=False)->int:
        """
        ページをスクロールする.  
        入出力は現在の高さ
        スクロール量は、画面の0.5~1.5倍の量がランダムにスクロールされる
        :param is_up: Trueで上へのスクロール
        """

        scroll_rate=random.uniform(0.5, 1.5) #スクロール量をランダムに決める

        window_height=self.driver.get_window_size()["height"] #現在のページ高さ
        top_height=self.driver.execute_script("return window.scrollY;") #今のページの頭位置

        N=ceil(scroll_rate*window_height/speed)
        for _ in range(N):
            top_height+=(speed*(-1*(is_up)) + speed*(not is_up)) #is_up=Trueで上にスクロールされる
            if top_height<0: #0より小さくなることは無いので, そのときは0に
                top_height=0
            self.driver.execute_script(f"window.scrollTo(0,{top_height});")
        
        sleep_time=random.gauss(1.5,0.5) #ランダムに停止
        # sleep_time=random.uniform(0.5,1.0) #ランダムに停止
        time.sleep(abs(sleep_time))


    
    def select_nav(self,nav_label:str):
        """
        ナビゲ―ションバーの移動

        -input-
            nav_label:
                [ホーム,検索,通知,ダイレクトメッセージ,ブックマーク,Blue,プロフィール]の中から選ぶ
        """
        print("="*25)
        print(f"***moving to {nav_label}***")

        element_header=self.driver.find_element(by=By.TAG_NAME,value="header")
        elements_nav=element_header.find_elements(by=By.TAG_NAME,value="a")
        for nav in elements_nav:
            label=nav.get_attribute("aria-label")
            if nav_label in label:
                nav.click()
                break
        
        time.sleep(random.uniform(1.0,2.0))


    def is_html_class(self,html_classes:dict,log_file_path):
        """
        htmlクラスが変わってないか確認する関数
        :return is_class_value: True->ちゃんとある. False->ない
        :return error_msg:
        """

        is_class_val=True
        error_msg=""
        for key,val in html_classes.items():
            elms=self.driver.find_elements(by=By.CLASS_NAME,value=val)
            if len(elms)==0:
                is_class_val=False
                error_msg=f"{Color.RED}!!!{Color.RESET}"+"-"*25+f"{Color.RED}there is no html class@{key}{Color.RESET}"+"-"*25+f"{Color.RED}!!!{Color.RESET}"
                print(error_msg)
                write_logs(log_file_path,error_msg)
                break

        return is_class_val,error_msg


    
    def _scrape_tweet(self,article, html_text_class):
        """
        ツイートを投稿者名, アカウント名, 内容テキストに分解する関数. フィルタリングする際に便利
        :param article : driver.find_element(by=TAG_NAME, value=article)で取ってきた1要素
        :param html_text_class: ツイートのテキストのクラス
        :return tweet_info: dict:{account_id, account_name, tweet_text,tweet_link,tweet_ancher}
        """

        #>> ツイートのテキスト内容 >>
        tweet_text=article.find_elements(
            by=By.CLASS_NAME,value=html_text_class
        )
        tweet_text=tweet_text[0].text if len(tweet_text)>0 else ""
        # print(tweet_text)
        #>> ツイートのテキスト内容 >>


        #>> アカウント名＆ID取得 >>
        for elm in article.find_elements(by=By.TAG_NAME,value="a"):
            account_id=elm.get_attribute("href").replace("https://twitter.com/","")
            account_name=elm.text

            if not len(account_name)==0:
                break
        # print(account_id,account_name)
        #>> アカウント名＆ID取得 >>
            

        #>> 画像or動画があるか調査 >>
        is_img=False
        video_elms=article.find_elements(by=By.TAG_NAME,value="video")
        if len(video_elms)>0: #動画でもOK
            is_img=True
        else:
            img_elms=article.find_elements(by=By.TAG_NAME,value="img")
            for elm in img_elms:
                src=elm.get_attribute("src")
                if not "profile" in src:
                    is_img=True
                    break
        #>> 画像or動画があるか調査 >>
                

        #>> ツイートページへのボタン要素とリンクを取得 >>
        ancher_elms=article.find_elements(by=By.TAG_NAME,value="a")
        link_pattern=r"/([^/]+)/status/(\d+)"
        for elm in ancher_elms:
            href=elm.get_attribute("href").replace(self.twitter_url,"")
            # print("href:",href)
            if re.match(link_pattern,href) and href.count("/")==3: #/abc123/status/11228990 みたいなパターンがリンクパターン
                tweet_link=href
                tweet_ancher=elm #これをクリックすればツイートページに飛べる
                break
        #>> ツイートページへのボタン要素とリンクを取得 >>
                
                
        tweet_info={
            "account_id":account_id, "account_name":account_name, 
            "is_img":is_img, "tweet_text":tweet_text,
            "tweet_link":tweet_link,"tweet_ancher":tweet_ancher,
        }

        return tweet_info
    

    def _is_element_visible(self,element):
        """
        要素が画面内にあるかどうかチェックする関数
        """
        pos_y=element.location["y"]

        window_height=self.driver.get_window_size()["height"] #現在のページ高さ
        top_y=self.driver.execute_script("return window.scrollY;") #今のページの頭位置
        bottom_y=top_y+window_height #今のページのおしり位置

        if bottom_y>pos_y and pos_y>top_y:
            return True
        else:
            return False
        

    def favo_tweet(self,article,favo_p,html_favo_class):
        """
        確率的にarticleのいいねボタンをクリック
        :return action_state: None->画面上にいいねボタンなし, favo->いいね, skip->スキップ
        """

        #>> 確率的にいいねをクリック >>

        action_state="None" #画面内にいいねボタンが写ってない状態

        icon_elms=article.find_elements(
            by=By.CLASS_NAME,value=html_favo_class
        )
        for elm in icon_elms:

            if not self._is_element_visible(elm): #画面内になければクリックできないので次へ
                continue

            aria_label=elm.get_attribute("aria-label") #要素のラベル取得

            if "いいね" in aria_label and not ("済" in aria_label or "しました" in aria_label): #いいねボタンであり, かつまだいいねしていない時
                is_favo=True if random.random() < favo_p else False #いいねするかどうかを確率で決める
                if is_favo:
                    self.actions.move_to_element(elm)
                    time.sleep(random.uniform(0.1,0.2))
                    elm.click() #いいね
                    time.sleep(random.uniform(0.5,1.5)) #いいねしたらちょっと待つ
                    action_state="favo"
                else:
                    action_state="skip"
        #>> 確率的にいいねをクリック >>
                    
        return action_state
    

    def scroll_downup(self,max_scroll_num=7,min_scroll_num=2):
        """
        下にちょっとスクロールして一番上まで戻ってくる関数
        コメント見るときとか, アカウントの投稿見るときとかに使う
        :param max_scroll_num, min_scroll_num
        """

        #>> まずは下へスクロール >>
        scroll_num=round(random.uniform(min_scroll_num,max_scroll_num))
        for n in range(scroll_num):
            prev_height=self.driver.execute_script("return window.scrollY;") #今のページの頭位置
            self.scroll_page(speed=4)
            current_height=self.driver.execute_script("return window.scrollY;")
            if abs(prev_height-current_height)<10: #差がほぼなければ
                break
        #>> まずは下へスクロール >>


        #>> 次に上にスクロール >>
        for n in range(scroll_num):
            self.scroll_page(speed=4,is_up=True)
            if abs(prev_height-current_height)<3: #差がほぼなければ
                break
        #>> 次に上にスクロール >>
            

    def jump_to_account(self,article,max_scroll_num=7,min_scroll_num=2,html_back_class=""):
        """
        アカウントページに一旦とんで帰って来る関数
        """

        #>> アカウントページへのアンカーを見つけ出してクリック >>
        ancher_elms=article.find_elements(by=By.TAG_NAME,value="a")
        for elm in ancher_elms:
            href=elm.get_attribute("href").replace(self.twitter_url,"")
            # print(href)
            if href.count("/")==1:
                account_ancher=elm
                break
        self.actions.move_to_element(account_ancher)
        time.sleep(random.uniform(0.1,0.4))
        elm.click()
        time.sleep(random.uniform(1,2.5))
        #>> アカウントページへのアンカーを見つけ出してクリック >>


        #>> スクロール >>
        scroll_num=round(random.uniform(min_scroll_num,max_scroll_num))
        for n in range(scroll_num):
            prev_height=self.driver.execute_script("return window.scrollY;") #今のページの頭位置
            self.scroll_page(speed=4)
            current_height=self.driver.execute_script("return window.scrollY;")
            if abs(prev_height-current_height)<10: #差がほぼなければ
                break
        #>> スクロール >>
            
        
        #>> ツイートページに戻る >>
        self.click_back_button(html_back_class)
        #>> ツイートページに戻る >>


    def click_back_button(self,html_back_class):
        """
        twitter上の戻るボタンを押す(webブラウザの戻るボタンではない)
        """
        anc_elms=self.driver.find_elements(by=By.CLASS_NAME,value=html_back_class)

        if len(anc_elms)>0:
            for anc in anc_elms:
                test_id=anc.get_attribute("data-testid")
                if "back" in test_id:
                    back_ancher=anc
                    break
            self.actions.move_to_element(back_ancher)
            time.sleep(random.uniform(0.3,1.3))
            back_ancher.click()
            time.sleep(random.uniform(5.0,8.0))
        else:
            pass


    def scroll_favo(self, favo_num, favo_p,max_process_seconds,filter_words:list,
                    log_file_path,html_favo_class,html_text_class,html_back_class,
                    direct_favo_p=0.5,favo_onpage_p=0.5,view_comment_p=0.5,jumpto_account_p=0.5,
                    random_scrollup_p=0.1
                    ):
        """
        人間の挙動と同じように, 現在のページをスクロールしながらfavoしていく
        :param favo_num: いいねする数
        :param favo_p: いいねする確率
        :param html_favo_class: いいねマークのhtmlクラス
        :param html_text_class:ツイートのテキストのクラス
        :param max_process_seconds: 最大可動時間 [sec]
        :param filter_words: このリストに入っている言葉が, アカウント名・ID・ツイート内容にあればfiltering
        """
        init_url=self.driver.current_url

        checked_tweet=[] #既に見たツイートはここに貯める

        log_txt=""

        process_start_time=time.time()
        favo_count=0
        while favo_count<favo_num and (time.time()-process_start_time)<max_process_seconds: #数がmaxいったら or 時間を超えたらおしまい
            try:
                #ツイート一つ一つを要素として抽出
                article_elms=self.driver.find_elements(
                    by=By.TAG_NAME,value="article"
                )

                for article in article_elms:

                    if not self._is_element_visible(article):
                        continue

                    #>> フィルターに引っかかれば、スキップする >>
                    tweet_info=self._scrape_tweet(article,html_text_class=html_text_class)
                    info=tweet_info["account_name"]+tweet_info["account_id"]+tweet_info["tweet_text"]   
                    is_filtering=False
                    if tweet_info["tweet_link"] in checked_tweet: #既に見たやつはスキップ
                        log_txt+="\n"+print_tweet(header=f"filtering tweet @already checked",tweet_info=tweet_info,color=Color.MAGENTA)
                        is_filtering=True
                    elif info.count("#")>7: #ハッシュタグの数が多すぎたら省く
                        log_txt+="\n"+print_tweet(header=f"filtering tweet @too many '#'",tweet_info=tweet_info,color=Color.MAGENTA)
                        is_filtering=True
                    elif not tweet_info["is_img"]: #画像があるかフィルター
                        log_txt+="\n"+print_tweet(header=f"filtering tweet @no Image",tweet_info=tweet_info,color=Color.MAGENTA)
                        is_filtering=True

                    if not is_filtering:
                        for word in filter_words:
                            if word in info: #禁止ワードが入ってるかフィルター
                                log_txt+="\n"+print_tweet(header=f"filtering tweet @{word}",tweet_info=tweet_info,color=Color.MAGENTA)
                                is_filtering=True
                                break

                    if is_filtering:
                        checked_tweet.append(tweet_info["tweet_link"]) #フィルターかけたやつはいれる
                        continue
                    #>> フィルターに引っかかれば、スキップする >>
                

                    if random.random()<direct_favo_p: #タイムライン上のいいねをダイレクトでいいね
                        #>> 確率的にいいねをクリック >>
                        action=self.favo_tweet(
                            article,favo_p,html_favo_class
                        )
                        if action=="favo":
                            log_txt+="\n"+print_tweet(header="favo tweet",tweet_info=tweet_info,color=Color.GREEN)
                            favo_count+=1
                            checked_tweet.append(tweet_info["tweet_link"]) #チェック済みリストに追加する
                        elif action=="skip":
                            log_txt+="\n"+print_tweet(header="skip tweet",tweet_info=tweet_info,color=Color.CYAN)
                            checked_tweet.append(tweet_info["tweet_link"]) #チェック済みリストに追加する
                        #>> 確率的にいいねをクリック >>
                         

                    else: #タイムライン上からツイートページへ飛ぶ

                        if self._is_element_visible(tweet_info["tweet_ancher"]):
                            tweet_info["tweet_ancher"].click()
                        else:
                            break #画面上になければ次にいく

                        time.sleep(random.uniform(0.8,2.0))

                        #>> ツイートページへ移動して操作 >>
                        max_scroll_num=5
                        min_scroll_num=1

                        func_args=[] #関数と引数の組を確率で追加
                        if random.random()<favo_onpage_p:
                            func_args.append((
                                self.favo_tweet, (1.0,html_favo_class), "favo on page" #これが発動したら100%いいね
                            ))
                        if random.random()<view_comment_p:
                            func_args.append((
                                self.scroll_downup, (max_scroll_num,min_scroll_num), "view comment"
                            ))
                        if random.random()<jumpto_account_p:
                            func_args.append((
                                self.jump_to_account, (max_scroll_num,min_scroll_num,html_back_class), "jump to account"
                            ))

                        random.shuffle(func_args) #実行順序をシャッフル
                        msg=""
                        for func,args,func_msg in func_args: #実行
                            if not "comment" in func_msg:
                                article_onpage=self.driver.find_elements(
                                                    by=By.TAG_NAME,value="article"
                                                )[0]
                                args=(article_onpage,)+args
                            if "favo" in func_msg:
                                favo_count+=1
                            func(*args) 
                            msg+=(func_msg+"/")
                        if len(msg)>0:
                            log_txt+="\n"+print_tweet(header=f"action on page@{msg}",tweet_info=tweet_info,color=Color.CYAN)   
                            checked_tweet.append(tweet_info["tweet_link"])
                        #>> ツイートページへ移動して操作 >>

                        self.click_back_button(html_back_class) #タイムラインに帰って来る


            except Exception as e:
                log_txt+=("\n"+str(e))
                print(e)


            finally:

                #>> 最初のページに戻れてなかったら戻るボタン押しまくる >>
                current_url=self.driver.current_url
                loop_count=0
                while not init_url==current_url:
                    self.click_back_button(html_back_class)
                    current_url=self.driver.current_url
                    loop_count+=1
                    if loop_count>5: #5回以上戻るボタンクリックしたらおかしいのでbreak
                        break
                #>> 最初のページに戻れてなかったら戻るボタン押しまくる >>
                    

                #>> finallyにスクロールを持ってくることで, エラーはいたときも強制的にスクロールできる >>
                if random.random()<random_scrollup_p:
                    self.scroll_page(speed=4,is_up=True) #たまに上にスクロールする
                else:
                    self.scroll_page(speed=4)
                #>> finallyにスクロールを持ってくることで, エラーはいたときも強制的にスクロールできる >>


        write_logs(log_file_path=log_file_path,log=log_txt)
        
                