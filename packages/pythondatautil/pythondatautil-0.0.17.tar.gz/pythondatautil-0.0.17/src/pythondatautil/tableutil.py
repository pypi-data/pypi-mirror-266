import csv
import os
from collections import Counter

class TableUtil:
    """TableUtilクラス"""

    def __init__(self,filepath,read_encoding='utf-8'):
        """CSVまたはTSVファイルのヘッダー行を読み込んでキー名とインデックス番号のマッピングをする

        read_encoding -> utf-8,cp932
        """
        
        self.filepath = filepath
        self.raw_header_list = None

        with open(self.filepath,mode='r',encoding=read_encoding) as f:
            content = f.readline().rstrip("\n")

            isInComma = "," in content
            isInTab = "\t" in content
        
            if isInComma and isInTab:
                raise ValueError("「,」とタブ文字が混在しているものは変換できません。")
            elif isInComma:
                self.raw_header_list = content.split(",")
            elif isInTab:
                self.raw_header_list = content.split("\t")

        self.counter_obj = Counter(self.raw_header_list)

        self.header_list = []
        self.header_dict = {}

        for i,v in enumerate(self.raw_header_list):
            self.header_list.append([i,v])
            self.header_dict[v] = i
            if self.counter_obj.get(v) > 1:
                # テーブルのキーが重複している時は、キーから消す。
                del self.header_dict[v]
            
    def show_header(self):
        """テーブルのインデックス表示する
        """
        
        for row in self.header_list:
            print("\t".join([str(v) for v in row]))

    def wirte_header(self,filename=None):
        """テーブルのインデックス情報を書き出す。
        
        filenameを省略すると、読み込んでいるファイル名を利用してインデックス情報をテキストファイルに書き出す。
        """
        if filename == None:
            filename_full = os.path.basename(self.filepath)
            filename,_ = os.path.splitext(filename_full)

        with open(f"{filename}_header.txt",mode='w',encoding='utf-8',newline='\n') as f:
            csv.writer(f,delimiter="\t").writerows(self.header_list)
    
    def getIndex(self,key):
        """テーブルのキーからインデックス番号を取得

        存在しないキーやキー名が重複しているものを指定するとエラー
        """

        if key in self.header_dict:
            return self.header_dict[key]
        else:
            raise ValueError(f"指定のキー:「{key}」に対するインデックスを取得するには、指定のキーが存在するか、対象キーがテーブルヘッダー内で重複していない必要があります。")
