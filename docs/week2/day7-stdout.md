<!-- current-curriculum: 2026-09-22 -->
# Week2 Day7 — stdout 與結構化結果

[上一課](<day6-subprocess.md>) · [本週目錄](README.md) · [下一週](../week3/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「stdout 與結構化結果」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

stdout 是文字通道，可能是 JSON、日誌或空字串；成功判定還要看 exit code 與資料欄位。混入 log 的文字不能直接當 JSON 解析。

## 在現在的專案中

本週先閱讀與執行純 Python 小例子；不要直接啟動依賴雲端的 worker。

本課對照：[scripts/platform.py](<../../scripts/platform.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def inspect(context, require_gpu=True):
    # 這份盤點只讀 Kubernetes metadata，不讀 Secret data，也不執行 workload。
    checks = []
    base = ["kubectl", "--context", context, "--request-timeout=15s"]

    def check(name, args, predicate=lambda data: True):
        # 單項失敗留在報告中，讓操作者一次看到所有前置條件，而不是遇到第一項就退出。
        try:
            data = json.loads(command(base + args + ["-o", "json"]))
            passed = bool(predicate(data))
            detail = "verified" if passed else "resource exists but readiness condition not met"
        except (RuntimeError, ValueError, KeyError, TypeError) as exc:
            passed, detail = False, str(exc)
        checks.append({"name": name, "passed": passed, "detail": detail})

    check("system node ready", ["get", "nodes"], lambda d: ready_nodes(d, "system-pool"))
    if require_gpu:
        check("GPU resource advertised", ["get", "nodes"],
              lambda d: ready_nodes(d, "gpu-pool", True))
    check("namespace", ["get", "namespace", NAMESPACE])
    for crd in ["jobsets.jobset.x-k8s.io", "localqueues.kueue.x-k8s.io"]:
        check(crd, ["get", "crd", crd], lambda d: any(
            c["type"] == "Established" and c["status"] == "True"
            for c in d.get("status", {}).get("conditions", [])))
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 對照 command 回傳 stdout 和 inspect 呼叫 json.loads 的位置，描述若命令成功但輸出不是合法 JSON會怎麼處理。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '52,75p' 'scripts/platform.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../tests/test_platform_preflight.py>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week2/day7-stdout.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
