# Instructions for The Laboratory AI, we named Alice.

## ファイル・フォルダ構成
#### client.py
メインソースコード．プログラムはここから実行してください．

#### core.py
ゲームのコアとなるコードをおいてください．ゲームのコアとは，駒を置いたり，季節を進めたりするメソッドです．

#### solver.py
サーバから送られてくるコマンドに対して適切な応答を返すことをsolverと呼びます．
ここでは，適切な応答をsolverに書いてあげます．

### classes:クラスモジュール置き場
ここには各クラスをおいてください．

#### GameState
ゲームの状態を保持しておくクラスです．
GameStateにメソッド類持たせても良かったのだけど，簡単化のためC言語ライクに構造体として扱います．

#### Action
#### Message
#### Worker

### ai: ゲームAIのモジュール置き場



## 命名規則
特に考えてませんが，privateなメソッドには_をつけるようにしてください．


## How to use
Execute this code on terminal.
Use Python 2.X. (We use Python 2.7.10)

```
$ python alice.pyc [LOG_FILE_NAME] [IP] [PORT] 
```

- LOG_FILE_NAME is set to name of log file.  Be careful, overrite to this log file if it exsits.
- IP is set to server IP. (not required, default is localhost)
- PORT is set to server PORT. (not required, default is 18420)

We haven't implemented cheking the arguments. Please check these parameter yourself before execute.
Otherwise, not-expected error will be occured.

## History
## ver 1.0.4
bug fix
    - make actions "1-1 S"

### ver 1.0.3
apply 6-1, 6-2

### ver 1.0.2
Output assumptions.

### ver.1.0.1
Cheking arguments is improved.

#### ver 1.0.0 Alice
Alice was born.