<!-- current-curriculum: 2026-09-22 -->
# Week10 Day6 — CI 建置映像

[上一課](<Day5-Pytest-MockCI-Integration.md>) · [本週目錄](README.md) · [下一課](<Day7-GitHub-Actions-GitOps-自動部署-ArgoCD.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「CI 建置映像」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

docker build 產生 image，push 才上 registry，部署再引用 tag 或 digest。Git SHA tag 提供追溯性但不等於已經上線，且 image 內實際 source 仍需核對。

## 在現在的專案中

只跑本機測試／離線讀 CI；不觸發 push、映像發佈或 Argo 同步。

本課對照：[.github/workflows/ci.yml](<../../.github/workflows/ci.yml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
      - name: Build Docker Image

        run: |

          docker build \
            -f docker/Dockerfile \
            -t asia-east1-docker.pkg.dev/project-4b82f780-0a12-4087-b94/hpc-images/hpc-api:${{ github.sha }} \
            .

      - name: Push Docker Image
        run: |
          docker push \
            asia-east1-docker.pkg.dev/project-4b82f780-0a12-4087-b94/hpc-images/hpc-api:${{ github.sha }}



      - name: Update Image Tag
        run: |
          sed -i "s/^  tag:.*/  tag: ${{ github.sha }}/" helm/api/values-dev.yaml
          cat helm/api/values-dev.yaml



      - name: Commit GitOps Changes
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 build 的 -f 與 context，找 tag 使用 github.sha 的位置；將 build 成功、push 成功、rollout 成功列為不同驗收點。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '86,109p' '.github/workflows/ci.yml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../tests/test_worker.py>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week10/Day6-Docker-Build-inCI.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
