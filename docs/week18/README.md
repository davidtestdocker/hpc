# Week18 — 網路排障：由近到遠建立證據

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

本週每日教材已完成逐篇文件核對。先讀各課頁首的修正與結果邊界，再讀完整原文；沒有 raw log 的課程不冒充實測。全套見[稽核清單](../audits/curriculum-content-audit.md)與[問題總表](../audits/curriculum-findings.md)。

## 先備與學習方式

先完成 [Week17](../week17/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

## 基礎解說

先確認來源、目的、協定、port 和時間，再依主機介面／route／DNS／listener／防火牆／服務路由逐層檢查。ping 不通或通都不足以替代應用連線測試。

Bandwidth 描述單位時間資料量，latency 描述延遲，MTU 決定某層封包大小上限。tcpdump 是觀察實際封包的工具，但需要範圍與權限，可能涉及敏感資料。

Kubernetes 又增加 Service／Endpoint／CNI／NetworkPolicy；NCCL 增加 transport 選擇與裝置拓撲。主環境沒有啟用 NetworkPolicy enforcement，allow／deny 證據來自隔離 Calico 叢集。

## 目前環境與實測邊界

本週可用 CPU 學主機網路；不把 CPU 測試或 Socket fallback 當 RDMA 硬體實測。

## 本週材料怎麼讀

- **Day1～Day3：主機連線與封包** — 課文保存介面、路由、MTU、吞吐及封包觀察；[run_iperf3.sh](../../benchmark/network/run_iperf3.sh) 只對應 Day2 的 TCP 吞吐命令，未實作課文全部 UDP／MTU 測試。
- **Day4：Kubernetes 服務路徑** — [API Service](../../k8s/api-service.yaml) 看 selector／port，[default-deny.yaml](../../k8s/security/network-policy/default-deny.yaml) 看網路規則。[隔離叢集的 allow／deny 結果](../evidence/network-policy-validation-20260921.json) 僅對應政策實驗，沒有涵蓋整週網路排障。
- **Day5：NCCL transport** — [保存的 NCCL log](../../benchmark/results/week16-day4-nccl-single-gpu.txt) 來自 Week16，同一份資料在本課用於讀取 transport 訊息。
- **Day6～Day7：拓撲與排查順序** — GPU／NIC／NUMA 指令、觀察與 playbook 都在課文；這部分沒有完成的雙節點訓練故障實驗。

## 每日閱讀順序

- [Day1：Linux 網路 baseline](<day1-linux-network-troubleshooting-baseline.md>)
- [Day2：Bandwidth、latency、MTU](<day2-network-quality-bandwidth-latency-mtu.md>)
- [Day3：封包級排障](<day3-packet-level-network-failure-troubleshooting.md>)
- [Day4：Kubernetes 網路](<day4-kubernetes-network-troubleshooting.md>)
- [Day5：NCCL transport 排障](<day5-nccl-transport-debugging.md>)
- [Day6：GPU／NIC／NUMA 拓撲](<day6-gpu-nic-numa-topology.md>)
- [Day7：通訊排障 playbook](<day7-distributed-communication-troubleshooting-playbook.md>)

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
