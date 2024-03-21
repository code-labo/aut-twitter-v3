"""
タイムラインをスクロールしながらいいねする
"""

import sys
from pathlib import Path
PARENT=str(Path(__file__).parent)
ROOT=str(Path(__file__).parent.parent)
sys.path.append(ROOT)

from src.auto_twitter import AutoTwitter
from src.utils import load_filter_words
from src.envs import FAVO_TIMELINE_CFG

def main():

    filter_words=load_filter_words(f"{PARENT}/filter_word.txt")

    url="https://twitter.com"
    auto_twitter=AutoTwitter()
    auto_twitter.access_url(url=url)

    #>> スクロールしながらいいね >>
    favo_num=FAVO_TIMELINE_CFG["NUM_TWEET_MAX"]
    favo_p=FAVO_TIMELINE_CFG["FAVO_PROBABLITY"] 
    max_process_seconds=FAVO_TIMELINE_CFG["MAX_PROCESS_SECONDS"]
    auto_twitter.scroll_favo(
        favo_num,favo_p,
        max_process_seconds,
        filter_words=filter_words,
        log_file_path=f"{ROOT}/log/favo_timeline_log.txt"
    )
    #>> スクロールしながらいいね >>


if __name__=="__main__":
    main()