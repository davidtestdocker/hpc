# 教材修正紀錄：完整 Markdown 與直接可讀結果

日期：2026-09-22。前一版把原教材縮短、要求讀者自行練習，並將原文存成文字檔，不符合直接閱讀完整教學與結果的需求；本次已修正。

- 原始 138 篇完整正文、命令與輸出，恢復到 docs/week*/ 對應 `.md` 的下半部；不是只留外部連結。
- 頁首提供現行補充與已保存結果。worker、CPU bootstrap、Redis persistence、NetworkPolicy、單 L4 訓練等直接列數據與解讀。
- 原版副本全部恢復 `.md`，僅重定位相對連結，讓 Markdown 可渲染。manifest 保存原文與副本各自的 SHA-256。
- [學習導讀](learning-guide.md)與[結果總覽](current-environment.md)改為閱讀模式，不要求使用者重新操作 VM 或做本機測試。
- 基礎概念與歷史案例沿用原文，不將示例／預期值假裝實測。未完成、失敗和不同環境仍分開標示。

本次僅做文件與既有證據核對：`python3 scripts/check_curriculum.py` 檢查原文保留、Markdown 副本、結果入口及 44 份原始證據 hashes。沒有重新執行 benchmark、部署、故障注入或雲端查詢；沒有刪除 VM，也沒有 commit／push。

原文完整保留的區段可能包含舊格式或 trailing whitespace，為保存原文不做機械清洗。新版補充的連結另行檢查，不把歷史教材本來的命令當作今日必須執行的步驟。
