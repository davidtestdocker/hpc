<!-- current-curriculum: 2026-09-22 -->
# Week20 Day2 — Pod、image 與 Secret 安全

[上一課](<day1-rbac-serviceaccount-least-privilege.md>) · [本週目錄](README.md) · [下一課](<day3-networkpolicy-tenant-isolation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Pod、image 與 Secret 安全」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

image digest 用於追溯內容，securityContext 限制執行權限，Secret mount 提供憑證。任何單一設定都不等於全面 hardening，init container 改權限也需看實際需要。

## 在現在的專案中

保留所有歷史成功與失敗；不宣稱 node failover、Redis 全失恢復或跨資料庫原子交易。

本課對照：[api/workloads/templates/jobset-mpi.yaml](<../../api/workloads/templates/jobset-mpi.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
              initContainers:
                - name: prepare-ssh
                  # 容器映像及標籤，決定執行的檔案系統與程式版本。
                  image: mpioperator/mpi-pi:openmpi
                  # 程序身分、權限與作業系統安全設定。
                  securityContext:
                    runAsUser: 0
                  # 覆寫容器入口指令；多行字串中的 Shell 語法由指定的 shell 解讀。
                  command:
                    - /bin/sh
                    - -lc
                    - |
                      set -e
                      cp /ssh-secret/id_ed25519 /ssh-work/id_ed25519
                      chown 1000:1000 /ssh-work/id_ed25519
                      chmod 600 /ssh-work/id_ed25519
                  # 把已宣告的 volume 掛載到容器中的指定路徑。
                  volumeMounts:
                    - name: ssh-secret
                      # 容器內可見的掛載路徑。
                      mountPath: /ssh-secret
                      # 是否以唯讀方式掛載，限制容器透過此掛載點寫入。
                      readOnly: true
                    - name: ssh-work
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 MPI template 的 key 複製、chmod 與 mount，說明 public/private key 用途和為何不能把內容放日誌；本課只讀設定，不讀實際 Secret。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '68,91p' 'api/workloads/templates/jobset-mpi.yaml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week20/day2-pod-image-secret-security.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
