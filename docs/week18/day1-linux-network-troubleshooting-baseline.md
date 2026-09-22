<!-- readable-curriculum: 2026-09-22 -->
# Week18 Day1 — Linux 網路 baseline

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-network-quality-bandwidth-latency-mtu.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史兩VM網路摘要。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

NIC零counter只限觀測位置與期間；TCP累積counter需delta，不等於應用完全無loss。MTU/MSS算式是假設IPv4無options，1433拒絕是本機MTU限制，不是遠端drop證據。

## 程式／設定與來源

本次核對：本課沒有對應獨立程式；依文內命令及觀察核對，不硬接其他元件。

## 已有結果與解讀

來源：[記錄／示例原文](<day1-linux-network-troubleshooting-baseline.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
971 Mbits/sec
```

hpc-demo10.140.0.2與net-test-01.9，30秒約971Mbps、Retr0；未保存pcap，不能回看完整封包。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：網路基礎依本週循序讀；Calico 封包隔離已在隔離叢集驗收，主環境 enforcement 仍關閉。
> **閱讀順序**：先學本文基礎，再讀[Week18 現行對照與檢核](../learning-guide.md#week18)及[對應現行入口](../runbooks/ai-hpc-job-troubleshooting.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week18 Day1 — Linux / Cluster Network Troubleshooting Baseline

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[day2-network-quality-bandwidth-latency-mtu](day2-network-quality-bandwidth-latency-mtu.md)。

---

## 今日完成內容

建立 HPC / AI Cluster Linux 網路排障基線，實際驗證：

- NIC / IP / route
- TCP LISTEN port
- TCP retransmission counters
- iperf3 bandwidth
- MTU boundary
- tcpdump 封包觀察
- TCP three-way handshake
- MTU 與 MSS 關係

測試節點：

    hpc-demo      10.140.0.2
    net-test-01   10.140.0.9

---

## 1. NIC / IP / Route

確認介面與 IP：

    ip -br addr

主要介面：

    ens4
    hpc-demo: 10.140.0.2
    net-test-01: 10.140.0.9

確認 routing：

    ip route
    ip route get 10.140.0.9

用途：

    確認 Linux 實際會從哪個 interface / gateway 將 packet 送往目標節點。

---

## 2. NIC 狀態與 counters

查看 NIC：

    ethtool ens4

虛擬 NIC 環境中可能看到：

    Speed: Unknown
    Duplex: Unknown
    Link detected: yes

查看統計：

    ethtool -S ens4

篩選異常：

    ethtool -S ens4 | grep -Ei 'drop|error|miss|timeout|fail|discard|overrun|crc'

以及：

    ip -s link show ens4

本次結果：

    RX errors: 0
    RX dropped: 0
    TX errors: 0
    TX dropped: 0
    tx_timeouts: 0

代表目前 NIC baseline 沒有明顯 drop / error。

---

## 3. TCP LISTEN Port

確認服務是否真的 listen：

    ss -lntp | grep 5201

iperf3 預設 TCP port：

    5201

啟動 server：

    iperf3 -s

概念：

    LISTEN 只代表本機 process 正在等待 TCP connection，
    不代表遠端一定能成功連入，仍可能受 route / firewall / VPC rule 影響。

---

## 4. TCP Retransmission Baseline

查看 TCP counters：

    netstat -s | grep -Ei 'retrans|lost'

重點：

    netstat counters 是開機後累積值，
    troubleshooting 時應比較 workload 前後 delta。

本次 iperf3 測試：

    before retransmitted segments: 1
    after retransmitted segments: 1

所以：

    retransmission delta = 0

---

## 5. Bandwidth Baseline

hpc-demo：

    iperf3 -s

net-test-01：

    iperf3 -c 10.140.0.2 -t 30

結果：

    Transfer: 3.39 GBytes
    Bitrate: 971 Mbits/sec
    Retr: 0

概念：

    Transfer
    = 測試期間傳送的總資料量

    Bitrate
    = 平均傳輸速率

本次 30 秒測試沒有觀察到 TCP retransmission。

注意：

    約 971 Mbps 是此 VM / virtual network path 的測試 baseline，
    不能直接推論為實體 NIC 的最高速度。

---

## 6. MTU

MTU：

    Maximum Transmission Unit

代表：

    network interface 能送出的最大 Layer 3 IP packet size。

本次：

    ens4 MTU = 1460

IPv4 ICMP 測試：

    ping -c 3 -M do -s 1432 10.140.0.9

計算：

    1432 ICMP payload
    + 8 ICMP header
    + 20 IPv4 header
    = 1460 bytes

結果成功：

    3 transmitted
    3 received
    0% packet loss

超過 1 byte：

    ping -c 3 -M do -s 1433 10.140.0.9

結果：

    local error: message too long, mtu=1460

代表：

    1461-byte IP packet 超過 local interface MTU，
    且 -M do 禁止 fragmentation，因此 Linux 在本機直接拒絕送出。

---

## 7. MSS

MSS：

    Maximum Segment Size

代表：

    TCP segment 中可承載的最大 TCP payload。

tcpdump SYN 中觀察到：

    mss 1420

IPv4 TCP：

    MTU 1460
    - IPv4 header 20
    - TCP header 20
    = MSS 1420

關係：

    MTU
    = 整個 IP packet 大小上限

    MSS
    = TCP payload 大小上限

---

## 8. tcpdump

安裝：

    apt-get update
    apt-get install -y tcpdump

抓 iperf3 TCP 5201：

    tcpdump -i ens4 -nn tcp port 5201

參數：

    -i ens4
    = 指定 NIC

    -nn
    = 不做 hostname / service name 解析

    tcp port 5201
    = 只抓 TCP 5201 traffic

---

## 9. TCP Data / ACK

實際抓到：

    10.140.0.9.41910 > 10.140.0.2.5201: Flags [P.], ... length 8448

代表：

    client 傳送 application data。

Server 回：

    10.140.0.2.5201 > 10.140.0.9.41910: Flags [.], ack ..., length 0

代表：

    server 透過 ACK 告知 sender 已收到資料，
    ack number 表示下一個期待收到的 sequence number。

常見 flags：

    [S]
    = SYN

    [S.]
    = SYN + ACK

    [.]
    = ACK

    [P.]
    = PSH + ACK

    [F.]
    = FIN

    [R]
    = RST

---

## 10. TCP Three-Way Handshake

使用：

    tcpdump -i ens4 -nn -c 10 'tcp port 5201'

Client：

    nc -vz 10.140.0.2 5201

抓到：

    Client -> Server  SYN
    Server -> Client  SYN + ACK
    Client -> Server  ACK

流程：

    Client                      Server

    SYN        ---------------->
               <---------------- SYN + ACK
    ACK        ---------------->

    TCP connection established

SYN：

    Synchronize

用途：

    發起 TCP connection，
    並同步雙方初始 sequence number。

---

## 11. TCP Connection Close

nc 測試完成後抓到：

    FIN
    FIN
    ACK

代表 TCP connection 正常關閉。

FIN：

    表示 sender 已沒有更多資料要傳，
    請求正常終止 TCP connection。

---

## 12. tcpdump 大封包觀察注意事項

tcpdump 中曾看到：

    length 56320

這不代表 wire 上真的存在 56 KB 且突破 MTU 的單一 IP packet。

Linux 可能使用：

    TSO
    GSO
    GRO

等 offload 機制。

因此 host 上 tcpdump 看到的大 chunk，
可能會在真正送往 network 前再被切成符合 MTU 的 packets。

---

## 13. Network Troubleshooting Playbook

遇到：

    Node A 無法連到 Node B

排查順序：

    NIC / Link
        ↓
    IP
        ↓
    Route
        ↓
    LISTEN Port
        ↓
    TCP Handshake
        ↓
    Firewall / Network Path

常用：

    ip -br addr
    ip route
    ip route get <destination>
    ss -lntp
    tcpdump

如果：

    可以連，但 performance 很差

再查：

    NIC drop / error
        ↓
    TCP retransmission
        ↓
    latency
        ↓
    bandwidth
        ↓
    MTU / MSS

常用：

    ip -s link
    ethtool -S
    netstat -s
    ping
    iperf3
    tcpdump

---

## 今日驗證結果

    ens4 link: UP
    NIC errors/drops: 0
    MTU: 1460
    TCP MSS: 1420
    iperf3 bandwidth: ~971 Mbits/sec
    Transfer: 3.39 GBytes / 30 sec
    iperf3 Retr: 0
    TCP retransmission delta: 0
    MTU 1432-byte ICMP payload: success
    MTU 1433-byte ICMP payload: rejected
    TCP SYN / SYN-ACK / ACK: verified
    tcpdump kernel capture drops: 0

---

## Interview Review

**Q1：MTU 與 MSS 有什麼差別？**  
A：MTU 是單一 IP packet 的最大大小；MSS 是 TCP segment 可承載的最大 TCP payload。IPv4 TCP 常見關係為 MSS = MTU - 20-byte IP header - 20-byte TCP header。

**Q2：TCP 連線異常時，tcpdump 怎麼判斷問題在哪？**  
A：先看 SYN 是否到達 server，再看 server 是否回 SYN-ACK。沒有 SYN 偏向 route / firewall / network path；有 SYN 但沒有 SYN-ACK 則優先檢查 server service、local firewall 或 TCP stack。
