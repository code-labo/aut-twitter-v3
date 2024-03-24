# Auto Twitter v3

人間の挙動に最大限近づける

## 環境
- python 3.10.13
- selenium 3.141.0
- MicrosoftEdge (chronium)

## 使い方
### ライブラリインストール
~~~
pip install -r requirements.txt
~~~

### configの追加
リポジトリ内にはconfigをpushしていないので、後から作る必要がある  
`/config/config.jsonc`を作成する  
その後、以下のような形式でファイル内容を書き加える  
以下の要素については後で説明を加える
- user_config
- html_css_value

~~~jsonc
{"auto_twitter_config":{

    "user_config":{
        "profile_name":"Profile N",
        "profile_path":"C:\\Users\\user-name\\AppData\\Local\\Microsoft\\Edge\\User Data",
        "account_name":"twitter-account-id",
        "is_headless":true
    },

    "gmail_config":{
        "sender":"aaaaaaaaaaaaaaaaaaaaaa@gmail.com",
        "password":"aaaaaaaaaaaaaaaaaaaa",
        "recipient":"bbbbbbbbbbb@gmail.com"
    },

    //これでフィルタリング
    "filter_word":{ 
        "text":"稼,人生,相互フォロー,無料,買取,価格,プレゼント,配布,入荷,ショップ,店,勧誘,発売,販売,教えて,社,めざましじゃんけん,bot,ボット,Bot,出品,商品,配り,フォロー,拡散,メルカリ,女子,顔出し",
        "account":"becky1794094,boke_houdai",
        "additional_word":"代行,チート,裏技"
    },

    //htmlのクラス値
    "html_css_value":{
        "tweet_text":"css-1rynq56.r-8akbws.r-krxsd3.r-dnmrzs.r-1udh08x.r-bcqeeo.r-qvutc0.r-37j5jr.r-a023e6.r-rjixqe.r-16dba41.r-bnwqim",
        "favo_icon":"css-175oi2r.r-1777fci.r-bt1l66.r-bztko3.r-lrvibr.r-1loqt21.r-1ny4l3l", //正しい方
        "back_button":"css-175oi2r.r-sdzlij.r-1phboty.r-rs99b7.r-lrvibr.r-2yi16.r-1qi8awa.r-1loqt21.r-o7ynqc.r-6416eg.r-1ny4l3l"
    },

    "random_action_config":{
        "direct_favo_probability":0.7,
        "favo_onpage_probability":0.8,
        "view_comment_probability":0.6,
        "jumpto_account_probability":0.4
    },

    //検索＆いいねのコンフィグ 最大25いいねくらいにしないとダメ
    "process_searchfavo_config":{
        "process_run_p":0.5, //このプロセス自体を動かす確率
        "mean_favo_num":4, //いいねする平均の数. これにランダム性を持たせる
        "std_favo_num":2, //いいねする数の標準偏差
        "favo_probablity":0.7, //いいねする確率
        "max_searchfavo_seconds":120, // 1つの検索でかける最大時間 [sec]

        "search_word":{ //ここからランダムに1つづつ選ぶ
            "test_key1":"#にゃんこ大戦争",
            "test_key2":"#ねこ,#ネコ,#ねこあつめ,#猫のいる暮らし,#うちのねこ"
        },

        "search_tab":{ //どのタブにするか, どっちから始めるかもランダム
            "key1":"話題,最新",
            "key2":"話題",
            "key3":"最新"
        }
    },

    //timelineいいねのコンフィグ
    "process_favotl_config":{
        "process_run_p":0.9, //このプロセス自体を動かす確率
        "mean_favo_num":20, //いいねするベースの数. 最大値は確率で変動
        "std_favo_num":4, //いいねする数の標準偏差
        "favo_probablity":0.7,
        "max_favotl_seconds":1500 //最大処理時間 [sec]
    }
}}
~~~

#### user_configについて
これはedgeやchromeでログインしたままアクセスするために必要なユーザー情報である.  
- `profile_name, profile_path`  
   ブラウザのアドレスバー上で`edge://version/`と入力すれば確認できる.  

- `account_name`  
  twitterのアカウントID（@の後ろの記号）を設定する  

- `is_headless`  
  `true`:バックグラウンドで稼働(確認はターミナルのみ)  
  `false`:自動で稼働している様子を確認することができる

#### html_css_valueについて
これは要素をfindするために使用するcssクラスを指定している  
twitterはスクレイピング対策としてタグをほとんど使用していない  
そのためcssクラスで検索をかける必要がある  
しかし, このcssクラスも定期的に変わるので, gmailに通知が来たら, その都度チェックして更新しましょう

### 定期実行化
`/batch/run_process.bat`をPCのcronに入れて定期実行化する  
ここで, 注意しなければいけないのが, cronを定時ではなく, ランダムに実行すること  
毎日12時ピッタリにアクセスしてしまうと, twitterに異常検知されてしまう