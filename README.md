# Instructions for The Laboratory AI, we named Alice.

## 実行方法
下記コマンドを実行する．IPとPORTは任意パラメータ

```
$ python3 main.py [IP] [PORT]
```

## フォルダ構成
気にするところはここだけ．
### game.GameBoard
現在のゲーム状態．
### game.Action
手のこと．(1-1, S)みたいなやつ．
### ai.IntelligenceIO
- startThinking(state): ゲームの状態が渡されるので，ここで考える
- getNextAction(): 次のActionを返してあげる．
