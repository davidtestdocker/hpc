<!-- current-curriculum: 2026-09-22 -->
# Week2 Day6 — subprocess

[上一課](<day5-dictionary.md>) · [本週目錄](README.md) · [下一課](<day7-stdout.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「subprocess」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

subprocess.run 用參數列表啟動外部命令，capture_output 接住輸出，timeout 限制等待。returncode 非零表示命令未按成功契約結束；不應把認證 stderr 原樣寫進公開證據。

## 在現在的專案中

本週先閱讀與執行純 Python 小例子；不要直接啟動依賴雲端的 worker。

本課對照：[scripts/platform.py](<../../scripts/platform.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def command(args):
    # 統一由 repo 根目錄執行外部工具，並以 timeout 避免認證或 API server 卡住。
    try:
        result = subprocess.run(
            args, cwd=ROOT, capture_output=True, text=True, timeout=60, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"{args[0]} unavailable or timed out") from exc
    if result.returncode:
        # Avoid putting credential-plugin stderr into saved evidence.
        raise RuntimeError(f"command failed (exit {result.returncode}): {' '.join(args)}")
    return result.stdout


def render():
    # 只渲染 Kustomize／Helm，不會套用任何資源到叢集。
    return command([
        "kubectl", "kustomize", "kustomize/overlays/gpu-sg-platform",
        "--enable-helm", "--load-restrictor", "LoadRestrictionsNone",
    ])


def ready_nodes(nodes, pool, gpu=False):
    # Ready 還不夠：節點也必須可排程；GPU 檢查另外要求公布 NVIDIA 資源。
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 command 函式的 timeout 與錯誤分支；用 subprocess.run(["python3", "--version"], capture_output=True, text=True) 在本機看結果。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '15,38p' 'scripts/platform.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../tests/test_platform_preflight.py>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week2/day6-subprocess.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
