# Week 教材現行化交付紀錄

日期：2026-09-22。範圍為教材與文件導航，不是平台功能升級或新一輪雲端驗收。

## 交付

- 138 篇每日教材正文改寫為概念、現行 source／設定片段、練習及判讀，不再只加新版入口。
- 新增 20 篇每週 README，先解釋基礎與先備，再依 Day 串接閱讀；[總導讀](learning-guide.md)從 Week1 開始。
- [本機練習與操作分級](current-environment.md)提供 Python、小範圍測試、離線 render 和原始結果重算；雲端變更依獨立 runbook。
- [歷史索引](history/20260922-before-current/README.md)保存改寫前 138 份完整文字快照；manifest 記錄原路徑、bytes 和 SHA-256。
- README、Evidence Index 與相關 demo／效能報告的歷史引用已連到快照；主展示和現行課程仍連到現行檔案。
- 部署 runbook 修正舊 image、14 個渲染資源、worker rollout 與 CPU bootstrap 的進度描述。

教材是現行實作導向的重新編排，不保證與舊教材逐段等長。舊版長篇教學與原始終端輸出沒有刪除，可由每課文末完整追回。Argo CD／Slurm／Ray 等獨立配置／案例不捏造成已接主線；單卡／CPU 證據不改稱多 GPU／RDMA 實績。

## 本機驗證

```bash
python3 scripts/check_curriculum.py
PYTHONPATH=. .venv/bin/pytest -q tests
.venv/bin/ruff check scripts/check_curriculum.py
terraform fmt -check terraform/environments/gpu-sg
helm lint helm/api helm/redis helm/postgres
git diff --check
```

本次結果：教材檢查通過、既有 53 項測試通過、驗證工具 Ruff 通過、Terraform 格式通過、三個 charts lint 通過。完整主 overlay 在本機離線渲染得到 14 個物件，未執行 apply。Helm 僅提示建議加入 chart icon，無失敗。

教材檢查覆蓋：現行頁面／連結／錨點、來源片段、138 份逐位元組快照及 44 份受保護原始證據。Evidence README 只更新導航，不列為不可變 raw artifact；manifest 保存其更新前 hash。新工具也用記憶體模擬損壞快照與斷鏈，確認會拒絕通過，未改動實際檔案。

本機 Python 基礎例子得到 `str dict`／`100.0`；離線重算確認每組三次、吞吐相對變化約 81.29%。這是讀取既有證據重新分析，不是新的 GPU 效能實驗。

## 沒有做的事

沒有重新部署、故障注入、壓測或修改雲端；沒有重寫歷史 log／JSON／trace／程式快照；沒有 commit／push。教材中需要硬體與維護時段的操作未因文件更新而重新驗證，也未把本機測試冒充遠端 CI 或服務即時健康。
