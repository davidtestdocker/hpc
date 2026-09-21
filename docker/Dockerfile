# API 容器映像建置步驟：安裝相依套件，以非 root 帳號啟動 Uvicorn。
# 選擇基底映像，後續建置步驟以它為起點。
FROM python:3.12-slim

# 設定容器環境變數：停用 .pyc 輸出，並讓 Python 日誌即時輸出。
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 設定後续 RUN／COPY 與啟動程式使用的工作目錄。
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

# 容器預設啟動指令；JSON 陣列形式直接傳入參數，不經 Shell 展開。
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
