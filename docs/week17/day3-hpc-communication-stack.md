<!-- current-curriculum: 2026-09-22 -->
# Week17 Day3 — HPC communication stack

[上一課](<day2-mpi-performance-benchmark.md>) · [本週目錄](README.md) · [下一課](<day4-slurm-multinode-hpc-cluster.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「HPC communication stack」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

SSH 可用來啟動遠端程序，MPI transport 承擔運算通訊，網路再提供底層路徑。SSH 能連上不代表所有 MPI ports／transport 都正確。

## 在現在的專案中

Slurm／Ray 是獨立實驗教材與已保存歷史案例，不當作目前可用服務。

本課對照：[api/workloads/templates/jobset-mpi.yaml](<../../api/workloads/templates/jobset-mpi.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
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
                      mountPath: /ssh-work

              # Pod 內的容器清單；同一 Pod 的容器共用網路。
              containers:
                - name: launcher
                  image: mpioperator/mpi-pi:openmpi
                  securityContext:
                    runAsUser: 1000
                    runAsGroup: 1000
                  # 資源設定；Pod 中是 requests／limits，Kustomize 中是待組合的檔案清單。
                  resources:
                    # 排程器計算需求時採用的資源量；500m CPU 等於 0.5 顆核心。
                    requests:
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 從 template 找 SSH key 掛載、worker DNS 與 mpirun 命令，分別解釋身分、名稱解析、程序啟動；不把 private key 印進筆記。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '81,104p' 'api/workloads/templates/jobset-mpi.yaml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week17/day3-hpc-communication-stack.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
