import sys
from pathlib import Path
PARENT=str(Path(__file__).parent)
ROOT=str(Path(__file__).parent.parent)
sys.path.append(ROOT)

from src.auto_twitter import AutoTwitter
from src.utils import load_filter_words
from src.envs import SEARCH_AND_FAVO_CFG

def main():

    filter_words=load_filter_words(f"{PARENT}/filter_word.txt")

    url="https://twitter.com"
    auto_twitter=AutoTwitter()
    auto_twitter.access_url(url=url)

    #--ツイートを適当に検索
    key_words=SEARCH_AND_FAVO_CFG["KEY_WORDS"]
    tab_names=SEARCH_AND_FAVO_CFG["TAB_NAMES"]
    for keyword in key_words:

        auto_twitter.search_tweet(keyword="lang:ja "+keyword) #検索
        
        for tab_name in tab_names:

            auto_twitter.select_tab(tab_name=tab_name) #タブ移動

            #>> スクロールしながらいいね >>
            favo_num=SEARCH_AND_FAVO_CFG["NUM_TWEET_MAX"]
            favo_p=SEARCH_AND_FAVO_CFG["FAVO_PROBABLITY"] #60%でいいねする
            max_process_seconds=SEARCH_AND_FAVO_CFG["MAX_PROCESS_SECONDS"]
            auto_twitter.scroll_favo(
                favo_num,favo_p,
                max_process_seconds,
                filter_words=filter_words,
                log_file_path=f"{ROOT}/log/search_and_favo_log.txt"
            )
            #>> スクロールしながらいいね >>


if __name__=="__main__":
    main()