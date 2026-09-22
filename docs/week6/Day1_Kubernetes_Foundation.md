<!-- current-curriculum: 2026-09-22 -->
# Week6 Day1 — Kubernetes 控制迴圈

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2_Pod_Foundation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Kubernetes 控制迴圈」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

kubectl 對 API server 送出宣告，controller 再逐步收斂；apply 成功只表示宣告被接受。CRD 讓 JobSet／Kueue 類型可被辨識，還需要對應 controller 才能執行協調。

## 在現在的專案中

K3s 是獨立基礎練習選項，不是本次主環境；雲端修改只依 runbook。

本課對照：[scripts/bootstrap_cluster.py](<../../scripts/bootstrap_cluster.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def download_controller(name, target):
    # Release URL 與 digest 同時鎖定，避免相同操作取得不同或遭竄改的 manifest。
    metadata = CONTROLLERS[name]
    with urllib.request.urlopen(metadata["url"], timeout=60) as response:
        content = response.read()
    digest = hashlib.sha256(content).hexdigest()
    if digest != metadata["sha256"]:
        raise RuntimeError(f"{name} manifest checksum mismatch")
    target.write_bytes(content)


def validate_postgres_env(path):
    # 僅回傳鍵名集合；錯誤與 evidence 都不包含密碼值。
    values = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise RuntimeError("PostgreSQL env file 格式錯誤")
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    required = {"POSTGRES_USER", "POSTGRES_PASSWORD"}
    if any(not values.get(key) for key in required):
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 bootstrap 安裝順序，解釋 CRD 存在、controller Available、實際 MPI completed 三個檢查各證明什麼。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '40,63p' 'scripts/bootstrap_cluster.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/cpu-bootstrap-acceptance-20260921.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week6/Day1_Kubernetes_Foundation.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
