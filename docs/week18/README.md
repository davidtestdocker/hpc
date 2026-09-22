# Week18 — 網路排障：由近到遠建立證據

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week17](../week17/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

## 基礎解說

先確認來源、目的、協定、port 和時間，再依主機介面／route／DNS／listener／防火牆／服務路由逐層檢查。ping 不通或通都不足以替代應用連線測試。

Bandwidth 描述單位時間資料量，latency 描述延遲，MTU 決定某層封包大小上限。tcpdump 是觀察實際封包的工具，但需要範圍與權限，可能涉及敏感資料。

Kubernetes 又增加 Service／Endpoint／CNI／NetworkPolicy；NCCL 增加 transport 選擇與裝置拓撲。主環境沒有啟用 NetworkPolicy enforcement，allow／deny 證據來自隔離 Calico 叢集。

## 目前環境與實測邊界

本週可用 CPU 學主機網路；不把 CPU 測試或 Socket fallback 當 RDMA 硬體實測。

[本週實作／證據入口](<../evidence/network-policy-validation-20260921.json>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：Linux 網路 baseline](<day1-linux-network-troubleshooting-baseline.md>)
- [Day2：Bandwidth、latency、MTU](<day2-network-quality-bandwidth-latency-mtu.md>)
- [Day3：封包級排障](<day3-packet-level-network-failure-troubleshooting.md>)
- [Day4：Kubernetes 網路](<day4-kubernetes-network-troubleshooting.md>)
- [Day5：NCCL transport 排障](<day5-nccl-transport-debugging.md>)
- [Day6：GPU／NIC／NUMA 拓撲](<day6-gpu-nic-numa-topology.md>)
- [Day7：通訊排障 playbook](<day7-distributed-communication-troubleshooting-playbook.md>)

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
