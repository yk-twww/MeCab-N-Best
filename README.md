# MeCab-N-Best

## 概要
MeCabのNベスト解を正しいコスト付きで出力するためのラッパー

MeCabは -N オプションによってNベスト解を出力することができる。しかし、Nベスト解を求める際、コストまで出力しようとした場合、正しいコストが出力されないという問題がある。  
例えば、mecab(0.996)、辞書ipadic(2.7.0)のもと、コスト付きでNベスト解を求めようとすると以下のように、全て同じコストになってしまう。  
(-E オプションは文末記号の出力形式を指定するオプションで、%pc は累積コストを表す変数である)

```
$ echo "今夜はカレー" | mecab -N4 -E"EOS(%pc)\n"
今夜    名詞,副詞可能,*,*,*,*,今夜,コンヤ,コンヤ
は      助詞,係助詞,*,*,*,*,は,ハ,ワ
カレー  名詞,一般,*,*,*,*,カレー,カレー,カレー
EOS(8955)
今夜    名詞,副詞可能,*,*,*,*,今夜,コンヤ,コンヤ
は      助詞,係助詞,*,*,*,*,は,ハ,ワ
カレー  名詞,固有名詞,地域,一般,*,*,カレー,カレー,カレー
EOS(8955)
今夜    名詞,副詞可能,*,*,*,*,今夜,コンヤ,コンヤ
は      助詞,係助詞,*,*,*,*,は,ハ,ワ
カレー  名詞,固有名詞,組織,*,*,*,*
EOS(8955)
今夜    名詞,副詞可能,*,*,*,*,今夜,コンヤ,コンヤ
は      助詞,係助詞,*,*,*,*,は,ハ,ワ
カレー  名詞,一般,*,*,*,*,*
EOS(8955)
```

この問題については、以下のブログやMeCab作者のTwitterでも取り上げられている。

* [MeCabでN-Best解を出力した時のコストの表示がおかしい？](http://sucrose.hatenablog.com/entry/2013/09/21/001055)
* [taku910さんのtweet](https://twitter.com/taku910/status/383126956893413376)




## 使い方
前提条件として、mecab及びmecabのPythonラッパーがインストールされている必要がある。  
2.7.3と2.7.5のPythonでは動作確認済み。  
また3系のPythonでは動作未確認。  
辞書はjumadic、ipadic、unidicのどれでもよい。

ダウンロードしてきたMeCab用の辞書のディレクトリには matrix.def というファイルが含まれている。これはコスト計算時に使われるコスト表を載せたファイルである。  
本スクリプトはこの表を参照して、自前でコストの計算を行っている。  

事前にmatrix.defの内容をシリアライズしておく。
以下の例ではカレントディレクトリ直下の matrix.pkl というファイルにシリアライズしているが、パスやファイル名は何でもよい。

```
>>> from mecab_n_best import MeCabNBest
>>> MeCabNBest.serialize("path/to/matrix.def", "./matrix.pkl")
```

解析するときは、インスタンス作成時にシリアライズしたものを読み込む。

```
>>> from mecab_n_best import MeCabNBest
>>> m = MeCabNBest("./matrix.pkl")
>>> result = m.parseNBest("今夜はカレー", 4)
>>> for ith_best in result:   
...   for morph in ith_best["sent"]:
...     print morph.encode('utf-8')
...   print "EOS(" + str(ith_best["cost"]) + ")"
... 
今夜    名詞,副詞可能,*,*,*,*,今夜,コンヤ,コンヤ
は      助詞,係助詞,*,*,*,*,は,ハ,ワ
カレー  名詞,一般,*,*,*,*,カレー,カレー,カレー
EOS(25068)
今夜    名詞,副詞可能,*,*,*,*,今夜,コンヤ,コンヤ
は      助詞,係助詞,*,*,*,*,は,ハ,ワ
カレー  名詞,固有名詞,地域,一般,*,*,カレー,カレー,カレー
EOS(25695)
今夜    名詞,副詞可能,*,*,*,*,今夜,コンヤ,コンヤ
は      助詞,係助詞,*,*,*,*,は,ハ,ワ
カレー  名詞,固有名詞,組織,*,*,*,*
EOS(29858)
今夜    名詞,副詞可能,*,*,*,*,今夜,コンヤ,コンヤ
は      助詞,係助詞,*,*,*,*,は,ハ,ワ
カレー  名詞,一般,*,*,*,*,*
EOS(30689)
```

(なぜか、上のコストと全然違うコストになっている)

MeCabの辞書はコンパイルするときに文字コードを自分で指定することができるが、本スクリプトではutf-8にしか対応していない。従って、辞書はutf-8用にコンパイルされている必要がある。
