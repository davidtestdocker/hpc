# 將 MPI YAML 樣板中的工作名稱占位符換成本次 job_id，產生待提交的資源內容。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
from pathlib import Path

# __file__ 是目前模組路徑；Path.parent 取得所在目錄，/ 用於串接路徑。
TEMPLATE_PATH = Path(__file__).parent / "templates" / "jobset-mpi.yaml"
PLACEHOLDER = "__JOBSET_NAME__"


# 建立小寫 JobSet 名稱，讀入樣板並替换占位符。
def render_mpi_jobset(job_id: str) -> str:
    jobset_name = f"mpi-{job_id}".lower()

    template = TEMPLATE_PATH.read_text()

    if PLACEHOLDER not in template:
        raise ValueError(f"Missing placeholder: {PLACEHOLDER}")

    # 字串 replace 替換所有占位符，讓 JobSet 名稱及 worker DNS 使用同一個識別碼。
    return template.replace(PLACEHOLDER, jobset_name)
