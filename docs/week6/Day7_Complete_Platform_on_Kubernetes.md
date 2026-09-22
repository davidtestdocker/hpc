<!-- current-curriculum: 2026-09-22 -->
# Week6 Day7 — 完整平台驗收

[上一課](<Day6_Deploy_API_and_Redis.md>) · [本週目錄](README.md) · [下一週](../week7/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「完整平台驗收」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

rollout 只檢查 workload readiness；DB 初始化、RBAC、queue、JobSet 與結果回收需要不同驗收。全新 CPU bootstrap 與既有單 L4 的 MPI 驗收是兩組證據。

## 在現在的專案中

K3s 是獨立基礎練習選項，不是本次主環境；雲端修改只依 runbook。

本課對照：[scripts/deploy_platform.py](<../../scripts/deploy_platform.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def deploy(context, execute, output, require_gpu=True):
    # 每次都使用顯式 context；報告不保存 Secret、環境變數或 kubectl stderr。
    report = {"context": context, "execute": execute, "passed": False, "steps": []}
    base = ["kubectl", "--context", context, "--request-timeout=30s", "-n", NAMESPACE]

    def run(args, timeout=60):
        result = subprocess.run(base + args, cwd=ROOT, capture_output=True,
                                text=True, timeout=timeout, check=False)
        if result.returncode:
            raise RuntimeError(f"kubectl {args[0]} failed (exit {result.returncode})")
        return result.stdout

    def record(step):
        report["steps"].append(step)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(step, flush=True)

    try:
        report["preflight"] = inspect(context, require_gpu=require_gpu)
        if not report["preflight"]["passed"]:
            raise RuntimeError("前置檢查失敗，詳見 report.preflight")
        record("prerequisites passed")
        existing = run(["get", "deployment", "redis", "--ignore-not-found", "-o", "json"])
        validate_redis(json.loads(existing) if existing.strip() else None)
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 deploy 的 validate_redis 與 rollout 步驟，對照 CPU bootstrap 證據。列出還需哪一份證據才能說 MPI 端到端成功。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '33,56p' 'scripts/deploy_platform.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/cpu-bootstrap-acceptance-20260921.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week6/Day7_Complete_Platform_on_Kubernetes.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
