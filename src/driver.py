import sys
from pathlib import Path
PARENT=str(Path(__file__).parent)
ROOT=str(Path(__file__).parent.parent)
sys.path.append(ROOT)

from webdriver_manager.microsoft import EdgeChromiumDriverManager
from msedge.selenium_tools import Edge,EdgeOptions
import time


def init_driver(profile_path,profile_name):

    ##バックグラウンドで実行する際のオプション
    ##コメント外すとバックグラウンドで実行される
    options=EdgeOptions()
    options.use_chromium=True #これを設定しないとアカウントを保持できない
    # options.add_argument("--headless=new") #selenium4.8以降のheadlessはこうやる
    # options.add_argument('--no-sandbox')
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument(f"--profile-directory={profile_name}")
    # options.add_argument("--ignore-certificate-errors")
    ##

    driver_manager=EdgeChromiumDriverManager().install()
    driver=Edge(
        driver_manager,
        options=options,
    )

    driver.set_window_size(1280,720)
    driver.implicitly_wait(5)
    time.sleep(3)

    return driver
