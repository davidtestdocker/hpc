<!-- current-curriculum: 2026-09-22 -->
# Week7 Day3 — Requests、limits 與 QoS

[上一課](<Day2_Secret.md>) · [本週目錄](README.md) · [下一課](<Day4_Liveness_and_Readiness_Probe.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Requests、limits 與 QoS」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

requests 影響 Pod 是否可排入節點，CPU limit 可能節流，memory limit 可能導致 OOM。降低 request 只能改排程宣告，不會讓真實資源消耗自動降低。

## 在現在的專案中

學習現行 chart；歷史 Traefik／NodePort 位址不當作可用入口。

本課對照：[helm/api/values.yaml](<../../helm/api/values.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
resources:
  # 排程器計算需求時採用的資源量；500m CPU 等於 0.5 顆核心。
  requests:
    # CPU 數量：1 代表一顆核心，m 表示千分之一核心。
    cpu: "100m"
    # 記憶體容量；Mi／Gi 是以 1024 為基底的單位。
    memory: "128Mi"
  # 容器可使用的資源上限；GPU 份額的實際意義取決於裝置外掛設定。
  limits:
    cpu: "500m"
    memory: "512Mi"
  # We usually recommend not to specify default resources and to leave this as a conscious
  # choice for the user. This also increases chances charts run on environments with little
  # resources, such as Minikube. If you do want to specify resources, uncomment the following
  # lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  # limits:
  #   cpu: 100m
  #   memory: 128Mi
  # requests:
  #   cpu: 100m
  #   memory: 128Mi

# This is to setup the liveness and readiness probes more information can be found here: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
# 存活探針失敗達門檻時，kubelet 會重啟容器。
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 對照 worker 的 request／limit，設想可用 CPU request 不足時查看 events，而不是先增加 retry 次數。解釋 Pending 和 OOMKilled 不同。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '137,160p' 'helm/api/values.yaml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/platform-after-training-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week7/Day3_Resource_Requests_Limits_QoS.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
