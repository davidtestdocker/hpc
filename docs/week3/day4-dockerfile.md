<!-- current-curriculum: 2026-09-22 -->
# Week3 Day4 — Dockerfile 與 build context

[上一課](<day3-image-container.md>) · [本週目錄](README.md) · [下一課](<day5-docker-compose.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Dockerfile 與 build context」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

FROM 選基底、WORKDIR 設工作目錄、COPY 放檔案、RUN 在建置時執行、CMD 設預設命令。COPY 的來源相對 build context，不一定相對 Dockerfile 目錄。

## 在現在的專案中

本週以檢查與離線讀設定為主；不要求安裝另一個 Docker daemon 或啟動正式服務。

本課對照：[docker/Dockerfile](<../../docker/Dockerfile>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
WORKDIR /app

# 建置映像時執行 Shell 指令；&& 只在前一指令成功後繼續。
RUN groupadd --system app \
    && useradd --system --gid app app

# 從建置 context 複製檔案；--chown 設定檔案擁有者。
COPY requirements.txt .

# 建置映像時執行 Shell 指令；&& 只在前一指令成功後繼續。
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

# 從建置 context 複製檔案；--chown 設定檔案擁有者。
COPY --chown=app:app api ./api
# 從建置 context 複製檔案；--chown 設定檔案擁有者。
COPY --chown=app:app monitoring ./monitoring

# 後續步驟與容器啟動使用此帳號。
USER app

# 宣告程式使用的埠號；仍需 Service 或 port mapping 才能對外連線。
EXPOSE 8000

```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 從 repo 根目錄讀 docker/Dockerfile，逐項標註建置時或啟動時發生。只閱讀 CI 的 build 命令，這輪不 push 映像。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '10,33p' 'docker/Dockerfile'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../docker/Dockerfile>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week3/day4-dockerfile.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
