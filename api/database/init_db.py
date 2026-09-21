# 依 ORM metadata 建立尚不存在的資料表；這不是既有資料表的結構遷移工具。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
from api.database.connection import engine
from api.database.models import Base


# 以 metadata.create_all 建立缺少的資料表。
def init_db() -> None:
    # 依 ORM 宣告建立缺少的資料表，bind 指定要使用的 engine。
    Base.metadata.create_all(bind=engine)


# __name__ 在直接執行此檔時為 __main__；被 import 時不會執行這個入口。
if __name__ == "__main__":
    init_db()
    print("database initialized")
