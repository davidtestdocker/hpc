<!-- current-curriculum: 2026-09-22 -->
# Week10 Day1 — CI／CD 基礎

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2-First-GitHub-ActionsCI-Pipeline.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「CI／CD 基礎」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

測試、build、push image、改 GitOps tag 是不同階段，後兩者有外部副作用。workflow 可在 pull_request 觸發，不代表每個 PR 都應具備發佈權限；需要分開看事件和 permissions。

## 在現在的專案中

只跑本機測試／離線讀 CI；不觸發 push、映像發佈或 Argo 同步。

本課對照：[.github/workflows/ci.yml](<../../.github/workflows/ci.yml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
permissions:
  contents: write
  id-token: write

# GitHub Actions 的工作清單，每個 job 可有自己的 runner。
jobs:

  test:

    runs-on: ubuntu-latest

    # 依序執行的步驟清單。
    steps:

      - name: Checkout Repository
        # 引用現成 GitHub Action，@ 後方是版本或提交。
        uses: actions/checkout@v4
        with:
          persist-credentials: true

      - name: Authenticate to Google Cloud
        id: auth
        uses: google-github-actions/auth@v3
        with:
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 on、permissions、steps，標出哪幾步只檢查、哪幾步會改外部狀態；不要為了讀教材手動觸發整條流程。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '15,38p' '.github/workflows/ci.yml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../tests/test_worker.py>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week10/Day1-CICD-Foundation.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
