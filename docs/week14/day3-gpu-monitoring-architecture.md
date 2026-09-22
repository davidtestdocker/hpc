<!-- current-curriculum: 2026-09-22 -->
# Week14 Day3 — GPU 監控架構

[上一課](<day2-kubernetes-gpu-scheduling.md>) · [本週目錄](README.md) · [下一課](<Day4-GKE-GPU-Node-Pool-GPU-Scheduling.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「GPU 監控架構」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

DCGM exporter 可暴露 GPU 指標，Prometheus 抓取，Grafana 顯示；另有 nvidia-smi 獨立取樣。兩條路徑不能因都叫 GPU monitoring 就混成同一次驗證。

## 在現在的專案中

現存 Week14 從 Day2 開始，維持原檔案命名；不捏造不存在的 Day1 實驗。

本課對照：[benchmark/k8s/dcgm-exporter.yaml](<../../benchmark/k8s/dcgm-exporter.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
spec:
  # 選取要關聯的物件；不同資源種類支援的 selector 格式不同。
  selector:
    # 以完全相等的標籤鍵值選取物件。
    matchLabels:
      app: nvidia-dcgm-exporter

  # 子物件模板；控制器以此內容建立 Pod 或相關工作資源。
  template:
    metadata:
      # 鍵值標籤，供 selector、監控或排程控制器識別資源。
      labels:
        app: nvidia-dcgm-exporter

    spec:
      # Run only on our GPU node pool
      # 要求節點具有指定標籤，限制 Pod 可排入的節點。
      nodeSelector:
        cloud.google.com/gke-nodepool: gpu-pool

      # Allow scheduling on GPU node taint
      # 容忍節點 taint；只解除排程限制，不保證會選中該節點。
      tolerations:
        - key: nvidia.com/gpu
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 exporter manifest 的資源和端口，再對照新訓練 telemetry 程式，畫出兩種資料來源；不宣稱 exporter 當下有 Running。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '39,62p' 'benchmark/k8s/dcgm-exporter.yaml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../performance/causal-lm-l4-20260922.md>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week14/day3-gpu-monitoring-architecture.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
