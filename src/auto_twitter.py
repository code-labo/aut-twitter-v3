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

from .envs import *
from .driver import init_driver
from .html_class_values import *
from.utils import print_tweet,Color,write_logs,load_logs

class AutoTwitter():


    def __init__(self):
        self.driver=init_driver(
            profile_name=PROFILE_NAME,
            profile_path=PROFILE_PATH
        )
        self.wait=WebDriverWait(driver=self.driver, timeout=15)
        self.actions=ActionChains(self.driver)
        self.account_name=ACCOUNT_NAME

    
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
        time.sleep(3)

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
        element_search.send_keys(Keys.DELETE)
        element_search.send_keys(keyword)
        element_search.send_keys(Keys.ENTER)
        ###END

        time.sleep(1.5)

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
        time.sleep(1.5)


    # def get_tweet(self,filters:list=[]):
    #     """
    #     今の画面のツイートを取得する.
    #     :return tweet_url
    #     :return account_url
    #     """

    #     tweet_list=[]

    #     articles=self.driver.find_elements(by=By.TAG_NAME,value="article") #ツイートのリストをゲット
    #     for i,article in enumerate(articles):

    #         try:
    #             #--フィルターにかける
    #             is_skip=False
    #             for filter in filters:
    #                 is_skip=filter(article=article) #ここで記事をフィルターにかける.
    #                 if is_skip==True:
    #                     break
    #             if is_skip==True:
    #                 continue
    #             #--

    #             #--すでにいいねされているかをチェック
    #             button_bar_class_value="css-175oi2r.r-1kbdv8c.r-18u37iz.r-1wtj0ep.r-1ye8kvj.r-1s2bzr4"
    #             is_favo=False #すでにいいねされているかフラグ
    #             buttons=article.find_elements(
    #                 By.CLASS_NAME,
    #                 value=button_bar_class_value
    #                 )
    #             # print(buttons)
    #             for button in buttons:
    #                 button_text=button.get_attribute("aria-label")
    #                 if ("いいね" in button_text) and ("しました" in button_text):
    #                     is_favo=True
    #                     # print(button) #<-いいねボタン
    #                     # button.click() #<-これでクリックできる
    #             if is_favo:
    #                 continue #既にいいねされていたら次のツイートに移る
    #             #--

    #             anchers=article.find_elements(by=By.TAG_NAME,value="a")
    #             for a in anchers:
    #                 href=a.get_attribute("href")
    #                 if a.get_attribute("dir") and ("status" in href):
    #                     account=re.sub("status.*","",href) #ツイート持ち主のアカウント
    #                     tweet_list.append([href,account]) #ツイートのリンクと持ち主のアカウントを追加
    #                     # print(href) #←ツイートのurl
    #                     # print(account)

    #         except Exception as e:
    #             print(e)
        
    #     return tweet_list
    

    def scroll_page(self,speed=5,scroll_rate=0.5)->int:
        """
        ページを1.2ページくらいスクロールする.  
        入出力は現在の高さ
        :param scroll_rate: ページの何割でスクロールするか
        """

        window_height=self.driver.get_window_size()["height"] #現在のページ高さ
        top_height=self.driver.execute_script("return window.scrollY;") #今のページの頭位置

        N=ceil(scroll_rate*window_height/speed)
        for _ in range(N):
            top_height+=speed
            self.driver.execute_script(f"window.scrollTo(0,{top_height});")
        time.sleep(1)


    
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
        
        time.sleep(1)


    # def get_follower_links(self,account_url,max_minutes=20)->list:
    #     """
    #     プロフィールページから,フォロワーのプロフィールページのリンクを取得
    #     :param max_minutes: 最大の検索時間[minutes]
        
    #     -return-
    #         follower_links:
    #             フォロワーのリンクをlistでreturn
    #     """

    #     self.driver.get(account_url)
    #     time.sleep(2)

    #     elements_ancher=self.driver.find_elements(by=By.TAG_NAME,value="a") #まずはアンカー取ってくる
    #     for ancher in elements_ancher:
    #         href=ancher.get_attribute("href")
    #         if "followers" in href:
    #             span=ancher.find_elements(by=By.TAG_NAME,value="span")
    #             for s in span:
    #                 print(s.text)
    #                 if str(s.text).isdigit():
    #                     num_followers=int(s.text) #フォロワー数の取得
    #                     break
    #             ancher.click() #フォロワー一覧の表示
    #             break

    #     time.sleep(1)
    #     self.access_url(account_url+"/followers") #<-直リンクはロックの原因になる. ボタンをクリックすべし

    #     class_value="css-175oi2r.r-1wbh5a2.r-dnmrzs.r-1ny4l3l.r-1loqt21" #フォロワー一覧のそれぞれのアカウントのリンクのクラス名
    #     followers_links=[]
    #     current_height=0
    #     t=time.time()
    #     with tqdm(total=num_followers) as pbar:
    #         print("***Getting Followers***")
    #         count_no_update=0 #updateされないカウント数. 2カウントたまったらbreakする
    #         while True:

    #             is_update=False

    #             try:
    #                 section_follower=self.driver.find_elements(by=By.TAG_NAME,value="section")[0] #最初のセクションが多分フォロワー
    #                 elements_follower=section_follower.find_elements(
    #                     by=By.CLASS_NAME,
    #                     value=class_value
    #                     )
                    
    #                 for follower in elements_follower:
    #                     href=follower.get_attribute("href")
    #                     if not href in followers_links:
    #                         followers_links.append(href)
    #                         pbar.update(1)
    #                         is_update=True
    #                         count_no_update=0

    #                 if not is_update:
    #                     count_no_update+=1

    #                 if not is_update and count_no_update>2:
    #                     break #おそらくなんだけど,自分のアカウントしか全てのフォロワーは取得できない

    #                 current_height=self.scroll_page(current_height,speed=7)
    #             except:
    #                 pass

    #             if (time.time()-t)>max_minutes*60:
    #                 break

    #     return followers_links
    

    # def _open_favoer_page(self,tweet_url):

    #     #ツイートにアクセス
    #     self.driver.get(tweet_url)
    #     time.sleep(2)

    #     ##いいねしたユーザー一覧の確認画面を開く
    #     element_anchers=self.driver.find_elements(by=By.TAG_NAME,value="a") #まずはアンカーを取得
    #     for ancher in element_anchers:
    #         href=ancher.get_attribute("href")
    #         #print(href)
    #         if "like" in href:
    #             ancher.click()
    #             break
    #     time.sleep(3)
    #     ##

    #     #幅を狭めることでpopupページじゃなくする & サイドバーのおすすめアカウントを消す
    #     self.driver.set_window_size(400,self.driver.get_window_size()["height"]) 


    # def get_favoers(self,tweet_url,max_account_num=30):
    #     """
    #     あるツイートにいいねした人のアカウントリンクのリスト
    #     全部は取らない.そんなに取っても一気にフォローできないから.
    #     3スクロール分くらいしかとらない
    #     :param tweet_url
    #     :param max_account_num : 最大のアカウントの数
    #     :return favoer_list
    #     """

    #     #いいねした人の一覧画面を開く
    #     self._open_favoer_page(tweet_url+"/likes") #直リンクはロックの原因になる. ボタンを辿らないとダメ


    #     #スクロールしながら
    #     favoer_list=[]
    #     current_height=0
    #     class_value="css-175oi2r.r-1wbh5a2.r-dnmrzs.r-1ny4l3l.r-1loqt21" #いいね一覧のそれぞれのアカウントのリンクのクラス
    #     while True:

    #         #今の画面のいいねした人を取得
    #         is_update=False
    #         favoer_list_per_page=[]
    #         account_elms=self.driver.find_elements(by=By.CLASS_NAME,value=class_value)
    #         for elm in account_elms:
    #             try:
    #                 href=elm.get_attribute("href")
    #                 if self.account_name in href:
    #                     break
    #                 favoer_list_per_page.append(href)
    #             except Exception as e:
    #                 print(e)
    #                 continue
    #         #

    #         #リストに追加
    #         for favoer in favoer_list_per_page:
    #             if not favoer in favoer_list:
    #                 favoer_list.append(favoer)
    #                 is_update=True
    #         #

    #         #更新がなくなったらおしまい
    #         if not is_update:
    #             break

    #         if len(favoer_list)>=max_account_num: #指定以上のサイズになったらおしまい
    #             favoer_list=favoer_list[:max_account_num]
    #             break

    #         #ページのスクロール
    #         current_height=self.scroll_page(current_height)


    #     return favoer_list
    

    # def favo(self,tweet_url):
    #     """
    #     ツイートページのtweet_urlにアクセスしてファボる
    #     """

    #     self.driver.get(url=tweet_url) #ダメ. 直リンクはロックの原因
    #     time.sleep(1)

    #     #クリックできる要素を取得

    #     #リツイート、いいねなどのボタンのクラス名
    #     class_value="css-175oi2r.r-1777fci.r-bt1l66.r-bztko3.r-lrvibr.r-1loqt21.r-1ny4l3l"
    #     clickable_elements=self.driver.find_elements(
    #         by=By.CLASS_NAME,
    #         value=class_value
    #     )

    #     #クリックできる要素の中で, いいねボタンをクリックする
    #     for element in clickable_elements:
    #         element_label=element.get_attribute("aria-label")
    #         if "いいね" in element_label:
    #             if not "しました" in element_label:
    #                 element.click() #まだいいねしてなければいいねする
    #                 title_name=re.sub("/.*","",self.driver.title)
    #                 print(f"favo **{title_name}**")
    #             break

    #     time.sleep(3)
        
    
    def _reset_mouse_position(self):
        """
        マウスの位置をホームボタンへリセットする. これをしないといいねした後にホバーが出る可能性がある
        """
        target_elm=self.driver.find_element(by=By.CLASS_NAME,value=NAV_CLASS)

        # ビューポートの中央に移動する
        self.actions.move_to_element(target_elm).perform()

    
    def _scrape_tweet(self,article, html_text_class=TWEET_TEXT_CLASS):
        """
        ツイートを投稿者名, アカウント名, 内容テキストに分解する関数. フィルタリングする際に便利
        :param article : driver.find_element(by=TAG_NAME, value=article)で取ってきた1要素
        :param html_text_class: ツイートのテキストのクラス
        :return tweet_info: dict:{account_id, account_name, tweet_text}
        """

        #ツイートのテキスト内容
        tweet_text=article.find_element(
            by=By.CLASS_NAME,value=html_text_class
        ).text
        # print(tweet_text)

        for elm in article.find_elements(by=By.TAG_NAME,value="a"):
            account_id=elm.get_attribute("href").replace("https://twitter.com/","")
            account_name=elm.text

            if not len(account_name)==0:
                break
        # print(account_id,account_name)
            
        tweet_info={
            "account_id":account_id, "account_name":account_name, "tweet_text":tweet_text
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

        # print(f"top:{top_y}, bottom:{bottom_y}, elm:{pos_y}")

        if bottom_y>pos_y and pos_y>top_y:
            return True
        else:
            return False
        
    
    # def _find_with_no_element_error(self,element,by:By,value,is_single=False):
    #     """
    #     指定した方法で要素を検索し、見つからない場合にカスタムエラーメッセージを表示する
    #     :param driver: WebDriver インスタンス
    #     :param by: 要素を検索する方法（Byクラスからの定数を使用）
    #     :param value: 要素を検索する値
    #     :param error_message: 要素が見つからなかった場合に表示するエラーメッセージ
    #     :param is_single: True->find_element, False->find_elements
    #     :return: 見つかった要素
    #     """
    #     try:
    #         if is_single:
    #             element = element.find_element(by, value)
    #         else:
    #             element=element.find_elements(by,value)
    #         return element
    #     except NoSuchElementException as e:
    #         return e


    def scroll_favo(self, favo_num, favo_p,max_process_seconds,filter_words=[],log_file_path="./",html_favo_class=FAVO_ICON_CLASS):
        """
        人間の挙動と同じように, 現在のページをスクロールしながらfavoしていく
        :param favo_num: いいねする数
        :param favo_p: いいねする確率
        :param html_favo_class: いいねマークのhtmlクラス
        :param max_process_seconds: 最大可動時間 [sec]
        :param filter_words: このリストに入っている言葉が, アカウント名・ID・ツイート内容にあればfiltering
        """

        log_txt=load_logs(log_file_path)+f"\n{datetime.now()}"

        process_start_time=time.time()
        favo_count=0
        while favo_count<favo_num and (time.time()-process_start_time)<max_process_seconds: #数がmaxいったら or 時間を超えたらおしまい
            try:
                #ツイート一つ一つを要素として抽出
                article_elms=self.driver.find_elements(
                    by=By.TAG_NAME,value="article"
                )

                for article in article_elms:

                    #>> フィルター単語がツイートの中に含まれていれば、スキップする >>
                    tweet_info=self._scrape_tweet(article)
                    is_filtering=False
                    for word in filter_words:
                        if word in " ".join(tweet_info.values()):
                            log_txt+="\n"+print_tweet(header=f"filtering tweet /filtered@{word}",tweet_info=tweet_info,color=Color.MAGENTA)
                            is_filtering=True
                            break
                    if is_filtering:
                        continue
                    #>> フィルター単語がツイートの中に含まれていれば、スキップする >>
                

                    #>> 確率的にいいねをクリック >>
                    icon_elms=article.find_elements(
                        by=By.CLASS_NAME,value=html_favo_class
                    )
                    for elm in icon_elms:

                        if not self._is_element_visible(elm): #画面内になければクリックできないので次へ
                            continue

                        aria_label=elm.get_attribute("aria-label") #要素のラベル取得

                        if "いいね" in aria_label and not "済" in aria_label: #いいねボタンであり, かつまだいいねしていない時
                            is_favo=True if random.random() < favo_p else False #いいねするかどうかを確率で決める
                            if is_favo:
                                log_txt+="\n"+print_tweet(header="favo tweet",tweet_info=tweet_info,color=Color.GREEN)
                                self.actions.move_to_element(elm)
                                time.sleep(0.1)
                                elm.click() #いいね
                                favo_count+=1
                                time.sleep(1) #いいねしたらちょっと待つ
                            else:
                                log_txt+="\n"+print_tweet(header="skip tweet",tweet_info=tweet_info,color=Color.CYAN)
                    #>> 確率的にいいねをクリック >>

            except Exception as e:
                log_txt+=("\n"+str(e))
                print(e)

            finally:
                self.scroll_page(speed=4,scroll_rate=0.8) #finallyにスクロールを持ってくることで, エラーはいたときも強制的にスクロールできる


        write_logs(log_file_path=log_file_path,log=log_txt)
        
                

    # def follow(self,account_url):
    #     """
    #     アカウントのページにとんでフォローする
    #     """

    #     #アクセス
    #     self.driver.get(url=account_url) #ダメ. 直リンクはロックの原因
    #     time.sleep(0.8)

    #     #フォローボタンを取得
    #     #ちょっとクラス名が不安定かもしんない
    #     #階層構造で選択した方が良いかも...
    #     class_value="css-175oi2r.r-sdzlij.r-1phboty.r-rs99b7.r-lrvibr.r-2yi16.r-1qi8awa.r-ymttw5.r-1loqt21.r-o7ynqc.r-6416eg.r-1ny4l3l"
    #     follow_button=self.driver.find_elements(
    #         by=By.CLASS_NAME,
    #         value=class_value
    #     )

    #     #フォロー
    #     if len(follow_button)>0:
    #         follow_button=follow_button[0]
    #         aria_label=follow_button.get_attribute("aria-label")
    #         if not "中" in aria_label: #フォロー中じゃなければクリック
    #             follow_button.click()
    #             accout_name=re.sub("/.*","",self.driver.title)
    #             print(f"follow **{accout_name}**")
