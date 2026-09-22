<!-- current-curriculum: 2026-09-22 -->
# Week8 Day7 — 多環境與 Argo 邊界

[上一課](<Day6-Helm-Kustomize-Integration.md>) · [本週目錄](README.md) · [下一週](../week9/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「多環境與 Argo 邊界」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

不同 namespace 不代表完全隔離：cluster-scoped 資源、node、配額可能共享。dev／stage／prod 設定目前是 GitOps 教材，不能宣稱三環境都已驗證最新 worker。

## 在現在的專案中

主線是 Helm／Kustomize 渲染與 deploy 工具；Argo CD 為獨立 GitOps 設定教材。

本課對照：[argocd/application-dev.yaml](<../../argocd/application-dev.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
  syncPolicy:
  #automated 是不用手動按sync只要有差異(push完)就會同步
  #prune true 如果git沒有這檔案但cluster 有的話檔案也會刪除變成跟git一樣
  #selfHeal 假設有人編輯了replicas數量 但是git沒變的話 argocd會發現差異自動改回git上的數量 (不用等push)
    automated:
      # 同步時是否刪除 Git 中已移除的受管資源。
      prune: true
      # 是否自動修正叢集狀態與 Git 宣告之間的偏差。
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 比较 Application path 和 values-dev 與主 api-values；列出切換需要審查的資源所有權與 prune 風險。本課只讀，不執行 argocd sync。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '34,44p' 'argocd/application-dev.yaml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/platform-deployment-20260921.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week8/Day7-GitOps_Multi_Environment_Integration.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
