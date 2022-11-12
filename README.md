# Discord読み上げボット(カズマサ読み上げボット)
# 実行環境
Herokuでの実行を確認しました

# 使い方
1.herokuへ登録

2.コマンドプロンプトを立ち上げて`heroku login`

3.2.でheroku: Press any key to open up the browser to login or q to exit:が出たら q以外のキーを押す

4.`heroku create YOUR_APP_NAME`でherokuアプリの作成をする

5.`git init heroku` でリポジトリを新規作成し，`git:remote -a YOUR_APP_NAME`でherokuのgitのレポジトリをフォルダに定義する

6.`git add .`を入力後`git commit -m "First commit"`,`git push heroku master`をそれぞれ入力してデプロイする

# ソースコードについて
`read_bot.py`のTOKEN_IDをご自身のDiscordボットのトークンと置き換えてお使いください．そのまま実行しても動作しません


# カズマサコマンド集
1.`.join`でVC参加

2.`.bye`でVCから抜ける(.byeし忘れてもVCに誰もいなくなったら勝手に抜けます)

3.`.register` `単語` `読み方`で単語の読み方を登録する

4.`.kazumasa`でカズマサの使い方一覧を表示する
