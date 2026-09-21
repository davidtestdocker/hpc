# 定義 runtime 的抽象介面，具體實作須提供初始化、執行與資訊查詢方法。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
from abc import ABC, abstractmethod


# class 定義 Runtime 類別；括號內是繼承的父類別。
class Runtime(ABC):
    # 準備 runtime 所需的模型或運算裝置。
    # 抽象方法要求子類別實作；pass 是空敘述，介面本身不執行運算。
    @abstractmethod
    def initialize(self):
        pass

    # 定義 run 函式；參數由呼叫端傳入，return 將結果交還呼叫端。
    @abstractmethod
    def run(self, request):
        pass

    # 回傳 runtime 的名稱、類型或裝置資訊。
    @abstractmethod
    def get_info(self):
        pass
