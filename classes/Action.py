# -*- coding:utf-8 -*-

"""
アクションを表すクラス
例: Action("2-A", "S")
player_id: 0 or 1 
action_id: 場所
kind_id: 種類 S/P/A
trend_id: T1/T2/T3(optional)
TODO: 不正値に対するエラー処理
"""
class Action:
    def __init__(self, player_id, action_id, kind_id, trend_id=None):
        self.action_id = action_id
        self.kind_id = kind_id
        self.player_id = player_id
        self.trend_id = trend_id
    def __str__(self):
        # Return value examples, like S 2-A
        if self.trend_id:
            return "Player"+str(self.player_id) + " "+ self.kind_id + " " +self.action_id + " " + self.trend_id
        return "Player"+str(self.player_id) + " "+ self.kind_id + " " +self.action_id
