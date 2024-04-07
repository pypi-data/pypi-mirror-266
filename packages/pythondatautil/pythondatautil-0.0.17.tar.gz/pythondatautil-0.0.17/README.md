# pythondatautil
Pythonのファイル処理を簡単にするためのライブラリ

#### インストール

```console
python -m pip install pythondatautil
```

#### アップデート

```console
python -m pip install pythondatautil -U
```

#### アンインストール

```console
python -m pip uninstall pythondatautil
```

## 簡易リファレンス DataUtil(du)

### 概要

ファイルとPythonのデータ型を双方に使いやすく変換

### 使い方
```Python
from pythondatautil import du

# テキストファイルの自動読み込み
"""tmp1.txt
Hi!
"""

# tmp1.txtというファイルを読み込む(パスを指定する)
data = du.r_auto("tmp1.txt")
print(data) # Hi!

# データの自動書き込み
du.w_auto([1,2,3]) 

"""tmp2.txt
1
2
3
"""
```

### メモ
r_auto,w_auto の自動読み込みおよび自動書き込みの対象は⭐️マーク その他は直接指定が必要  
[その他APIリファレンス詳細(ソースコードから自動生成)]( https://m-ippei.github.io/pythondatautil/pythondatautil.html)

#### r:Read系
* r_auto(path_string) 拡張子または中身から自動変換読み込み
* r_txt(path_string) テキストファイル→文字列型
* r_csv(path_string) CSVファイル→リスト型 ⭐️
* r_tsv(path_string) TSVファイル→リスト型 ⭐️
* r_json(path_string) JSONファイル→辞書型またはリスト型 ⭐️
* r_pickle(path_string) pickleファイル→辞書型またはリスト型 ⭐️

#### w:Write系
* w_auto(any_data) ファイルの中身から判断して自動でファイル書き出し setオブジェクトは、ソートしてリストで書き出す。
* w_txt(some_string) テキスト書き込み ⭐️文字列のみの場合
* w_log(string or list ...) ログテキスト書き込み　追記+改行
* w_list(list) リスト書き込み 改行区切り ⭐️w_autoは1次元リストの場合
* w_list_lf(list) w_listの改行コードがLFバージョン
* w_csv(list) 2次元リスト書き込み　通常CSV書き込み 拡張子は.txt
* w_csv_lf(list) w_csvの改行コードがLFバージョン
* w_tsv(list) w_csvのtsvバージョン ⭐️w_autoは2次元リストの場合
* w_tsv(list) w_tsvの改行コードがLFバージョン
* w_dict(dict) 辞書型を整形してテキストファイルで書き出す(pprintによるファイル書き出し) 
* w_json(dict or list) 辞書型またはリスト型をJSONファイルで書き出す ⭐️w_autoは辞書型の場合
* w_pickle(dict or list) 辞書型またはリスト型をPickleファイルで書き出す

### その他

* str_to_list(some_string) 改行の区切りの文字列を直接引数から受け取ってリストにして返す　空白行は除去する
* yyyymmdd <年4桁 月2桁 日2桁>となる形式の現在の日付文字列を返す 例:2024年1月1日の場合→20240101
    * プロパティのため du.yyyymmdd で取得可
* now 現在時刻を返す。例 2024-01-01T00:00:00.000+09:00
    * RFC3339とISO8601に準拠
    * OSのタイムゾーン付き
    * ミリセカンド部分まで
    * プロパティのため du.now で取得可

### ファイル書き込み時のfilename省略
* 同じ階層からtmp<数字>のファイル名を見つけ出し、<maxの数字>+1の連番で作成。
* w_logの場合でfilenameを省略した場合は、yyyymmdd.txtでファイルを作成

## 簡易リファレンス TableUtil

### 概要
テーブル形式のCSV(TSV)ファイルにおいて、インデックス指定を簡易化するライブラリ

### 使い方
```Python
from pythondatautil import TableUtil

# tsvも可能 拡張子はtxtでも問題なし
tu = TableUtil(r"table.csv")

"""table.csv
order,fruit,price
1,grape,500
2,lemon,300
"""

# ヘッダー行のインデックスを表示 write_headerで書き出しする
tu.show_header()
"""
0	order
1	fruit
2	price
"""

# キー名からインデックス番号を取得
print(tu.getIndex("fruit"))
"""
1
"""
```

## その他

ビルド
```console
python -m build
```

Wheelインストール
```console
python -m pip install <wheel>
```

## シェルコマンド一覧(GitHubからパッケージインストール等をする場合)
#### インストール
```console
python -m pip install git+https://github.com/m-ippei/pythondatautil.git
```
#### アップデート
```console
python -m pip install git+https://github.com/m-ippei/pythondatautil.git -U
```
#### アンインストール
```console
python -m pip uninstall pythondatautil
```

## 備考
デフォルトで取り扱う文字コードはUTF-8


