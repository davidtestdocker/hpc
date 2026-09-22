<!-- current-curriculum: 2026-09-22 -->
# Week14 Day2 — GPU scheduling

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day3-gpu-monitoring-architecture.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「GPU scheduling」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

GPU request 需要 device plugin 公布資源，taint／toleration 決定允不允許排入，nodeSelector 決定選哪些節點。toleration 不會強制挑 GPU node，更不保證 GPU runtime 成功。

## 在現在的專案中

現存 Week14 從 Day2 開始，維持原檔案命名；不捏造不存在的 Day1 實驗。

本課對照：[benchmark/k8s/pytorch-gpu-pod.yaml](<../../benchmark/k8s/pytorch-gpu-pod.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
      resources:
        # 容器可使用的資源上限；GPU 份額的實際意義取決於裝置外掛設定。
        limits:
          # Request one NVIDIA GPU
          # NVIDIA 裝置外掛提供的 GPU 資源單位；time-slicing 時不等同實體卡數。
          nvidia.com/gpu: 1
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 對照 GPU workload 和主 worker 的 resources，指出 CPU MPI 為何能放 GPU node 卻不使用 GPU 計算。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '47,52p' 'benchmark/k8s/pytorch-gpu-pod.yaml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../performance/causal-lm-l4-20260922.md>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week14/day2-kubernetes-gpu-scheduling.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
