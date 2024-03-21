import sys
from pathlib import Path
PARENT=str(Path(__file__).parent)
ROOT=str(Path(__file__).parent.parent)
sys.path.append(ROOT)

from src.auto_twitter import AutoTwitter
from src.utils import load_filter_words

def main():

    filter_words=load_filter_words(f"{PARENT}/filter_word.txt")

    url="https://twitter.com"
    auto_twitter=AutoTwitter()
    auto_twitter.access_url(url=url)

    #--ツイートを適当に検索
    key_words=["#b3d"]
    tab_name="話題"
    for keyword in key_words:

        auto_twitter.search_tweet(keyword="lang:ja "+keyword) #検索
        auto_twitter.select_tab(tab_name=tab_name) #タブ移動


        #>> スクロールしながらいいね >>
        favo_num=2
        favo_p=0.6 #60%でいいねする
        max_process_seconds=30
        auto_twitter.scroll_favo(
            favo_num,favo_p,
            max_process_seconds,
            filter_words=filter_words,
            log_file_path=f"{PARENT}/log.txt"
        )
        #>> スクロールしながらいいね >>

if __name__=="__main__":
    main()