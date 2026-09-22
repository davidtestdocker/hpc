<!-- current-curriculum: 2026-09-22 -->
# Week8 Day6 — Helm 與 Kustomize 整合

[上一課](<Day5_Kustomize_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day7-GitOps_Multi_Environment_Integration.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Helm 與 Kustomize 整合」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

本專案先讓 Kustomize 使用 helmCharts 產生資源，再套 patches。load restrictor 設定允許引用 repo 內 chart；這不是對叢集發起 apply。

## 在現在的專案中

主線是 Helm／Kustomize 渲染與 deploy 工具；Argo CD 為獨立 GitOps 設定教材。

本課對照：[scripts/platform.py](<../../scripts/platform.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def render():
    # 只渲染 Kustomize／Helm，不會套用任何資源到叢集。
    return command([
        "kubectl", "kustomize", "kustomize/overlays/gpu-sg-platform",
        "--enable-helm", "--load-restrictor", "LoadRestrictionsNone",
    ])


def ready_nodes(nodes, pool, gpu=False):
    # Ready 還不夠：節點也必須可排程；GPU 檢查另外要求公布 NVIDIA 資源。
    for node in nodes.get("items", []):
        if node["metadata"].get("labels", {}).get("cloud.google.com/gke-nodepool") != pool:
            continue
        if node.get("spec", {}).get("unschedulable", False):
            continue
        status = node.get("status", {})
        ready = any(c["type"] == "Ready" and c["status"] == "True"
                    for c in status.get("conditions", []))
        if ready and (not gpu or int(status.get("allocatable", {}).get("nvidia.com/gpu", 0)) > 0):
            return True
    return False


def inspect(context, require_gpu=True):
```

## 閱讀與練習

本次主部署鏈的讀法：

1. `kustomization.yaml` 的 `helmCharts` 選 api／redis／postgres charts，`valuesFile` 指向主環境覆寫。
2. chart 的模板把 values 展開成資源；此時仍只是文字／物件內容。
3. Kustomize 的 `patches` 對被 target 選中的資源增加 nodeSelector／serviceAccount 等差異。
4. `scripts/platform.py render` 只產生結果；`scripts.deploy_platform.py` 才有 server dry-run／apply／rollout 步驟。

離線練習可用 `PYTHONPATH=. .venv/bin/python scripts/platform.py render` 印出完整主 overlay。需要本機 kubectl、Helm 和 chart；不會發起 apply。本次渲染為 14 個物件，含 api-worker、Redis PVC 和 API HPA，但不含 controllers／queue／runtime Secrets，這些由 bootstrap 前置處理。

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 platform.render 的完整參數，使用離線 render 檢視 Deployment／StatefulSet／PVC，最後才對照 deploy 如何套用和等待 rollout。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '29,52p' 'scripts/platform.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/platform-deployment-20260921.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week8/Day6-Helm-Kustomize-Integration.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
