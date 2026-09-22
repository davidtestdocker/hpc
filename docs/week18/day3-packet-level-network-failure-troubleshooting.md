<!-- readable-curriculum: 2026-09-22 -->
# Week18 Day3 — 封包級排障

[上一課](<day2-network-quality-bandwidth-latency-mtu.md>) · [本週目錄](README.md) · [下一課](<day4-kubernetes-network-troubleshooting.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史refused/timeout故障注入。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

RST可能由拒絕規則或中間設備產生；本例搭配server抓包、無listener与移除DROP的對照才支持原因。零NICcounter不能普遍排除全部driver問題。

## 程式／設定與來源

本次核對：本課沒有對應獨立程式；依文內命令及觀察核對，不硬接其他元件。

## 已有結果與解讀

來源：[記錄／示例原文](<day3-packet-level-network-failure-troubleshooting.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
timeout changed to refused
```

只有文內SYN/RST摘要，沒有pcap；移除DROP後仍refused，是防火牆恢復不是應用服務恢復。

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

# Week18 Day3 — Packet-level Network Failure Troubleshooting

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[day4-kubernetes-network-troubleshooting](day4-kubernetes-network-troubleshooting.md)。

---

## 今日完成內容

建立一套可從 client 連線失敗一路定位到 root cause 的 packet-level network troubleshooting 流程，實際驗證：

- `Connection refused`
- `Timeout`
- TCP SYN / RST 行為
- SYN retransmission
- firewall DROP
- `ss + tcpdump + iptables` 聯合判讀
- NIC / driver counters
- fault domain isolation

測試節點：

    hpc-demo      10.140.0.2
    net-test-01   10.140.0.9

---

## 1. Connection Refused Case

先確認 server TCP 6000 沒有 listener：

    ss -lntp | grep ':6000'

結果：

    no output

代表：

    TCP 6000 沒有 process LISTEN。

Server 抓包：

    tcpdump -i ens4 -nn 'tcp port 6000'

Client：

    nc -vz 10.140.0.2 6000

Client 結果：

    Connection refused

tcpdump：

    10.140.0.9.52818 > 10.140.0.2.6000: Flags [S]
    10.140.0.2.6000 > 10.140.0.9.52818: Flags [R.]

流程：

    Client
      |
      | SYN
      v
    hpc-demo
      |
      | TCP 6000 no listener
      v
    RST + ACK
      |
      v
    Connection refused

判斷：

    network path 正常
    packet 已抵達 server
    root cause 是 server port 沒有 service listen

---

## 2. RST

RST：

    Reset

是 TCP flag，用來：

    立即拒絕或強制終止 TCP connection。

本次：

    SYN
    ↓
    RST + ACK

代表：

    server 收到 client 的 connection request，
    但不接受此 TCP connection。

比較：

    FIN
    = 正常關閉 connection

    RST
    = 強制拒絕 / 立即終止

---

## 3. Silent DROP / Timeout Case

先確認 TCP 6001 沒有 listener：

    ss -lntp | grep ':6001'

加入暫時 firewall DROP rule：

    iptables -I INPUT 1 -p tcp --dport 6001 -j DROP

意義：

    進入 hpc-demo
    destination TCP port = 6001
    → silent DROP
    → 不回 RST
    → 不回 SYN-ACK

Server：

    tcpdump -i ens4 -nn 'tcp port 6001'

Client：

    nc -vz -w 5 10.140.0.2 6001

結果：

    timed out

tcpdump：

    Flags [S]
    Flags [S]
    Flags [S]
    Flags [S]
    Flags [S]

而且使用相同 sequence number。

代表：

    Client 第一次 SYN 沒收到任何 reply
    ↓
    TCP 自動 retransmit SYN
    ↓
    仍沒有 reply
    ↓
    最後 timeout

---

## 4. Connection Refused vs Timeout

Connection refused：

    SYN
    ↓
    RST
    ↓
    refused

代表：

    remote host 有回應，
    但 TCP connection 被拒絕。

Timeout：

    SYN
    ↓
    no reply
    ↓
    SYN retransmission
    ↓
    timeout

代表：

    client 沒收到有效回覆。

可能原因：

    firewall DROP
    route problem
    network path drop
    remote host unavailable

不能單靠 timeout 文字直接判定是哪一層，
需要 tcpdump / route / firewall 等證據進一步定位。

---

## 5. Root Cause Confirmation

移除 firewall DROP rule：

    iptables -D INPUT -p tcp --dport 6001 -j DROP

確認：

    iptables -L INPUT -n --line-numbers | grep 6001

預期：

    no output

再次測試：

    nc -vz -w 5 10.140.0.2 6001

tcpdump：

    Client -> Server: SYN
    Server -> Client: RST + ACK

代表：

    firewall DROP 移除後
    packet 可以正常進入 TCP stack

但因為 TCP 6001 仍沒有 listener：

    timeout
    ↓
    變成
    connection refused

這直接證明：

    原本 timeout 的 root cause
    是 host firewall DROP rule。

---

## 6. NIC Counters

查看 interface counters：

    ip -s link show ens4

結果：

    RX errors:   0
    RX dropped:  0
    RX missed:   0

    TX errors:   0
    TX dropped:  0
    carrier:     0

查看 driver / queue counters：

    ethtool -S ens4 | grep -Ei 'drop|error|miss|timeout|fail|discard|overrun|crc'

結果：

    rx_queue_0_drops: 0
    rx_queue_1_drops: 0
    rx_queue_2_drops: 0
    rx_queue_3_drops: 0

    tx_queue_*_xdp_tx_drops: 0
    tx_queue_*_tx_timeouts: 0

表示目前沒有觀察到：

    RX queue drops
    TX queue drops
    NIC errors
    driver timeouts
    carrier errors

---

## 7. Firewall DROP 不等於 NIC DROP

封包大致路徑：

    Network
       ↓
    Virtual NIC
       ↓
    ens4 / driver
       ↓
    Linux network stack
       ↓
    iptables INPUT
       ↓
    application

本次 firewall DROP 發生在：

    packet 已經正常通過 NIC / driver
    並進入 Linux network stack 之後。

所以即使：

    iptables DROP

仍可能看到：

    RX errors = 0
    RX dropped = 0

因此：

    firewall drop
    !=
    NIC drop

不同 layer 的 counter 不可混為一談。

---

## 8. Fault Domain Isolation

### Case A：Port 沒 listener

證據：

    ss
    → no LISTEN

    tcpdump
    → SYN + RST

    NIC counters
    → clean

Root cause：

    server service / TCP port layer

---

### Case B：Firewall DROP

證據：

    tcpdump
    → repeated SYN
    → no SYN-ACK
    → no RST

    NIC counters
    → clean

    iptables
    → DROP rule present

Root cause：

    host firewall layer

---

## 9. Packet-level Troubleshooting Flow

遇到：

    TCP connection failed

排查流程：

    1. Server 有 listener 嗎？
       ss -lntp

       ↓

    2. Client SYN 有沒有到 server？
       tcpdump

       ↓

    3. Server 回什麼？

       SYN-ACK
       → TCP handshake 正常

       RST
       → host reachable，但 connection 被拒絕

       no reply
       → drop / firewall / path issue

       ↓

    4. NIC counters 有異常嗎？
       ip -s link
       ethtool -S

       ↓

    5. 再定位 fault domain

       application
       service
       TCP stack
       firewall
       NIC / driver
       network path

---

## 10. 今日實際驗證

Connection refused case：

    SYN observed
    RST observed
    no listener on TCP 6000

Timeout case：

    repeated SYN observed
    no SYN-ACK
    no RST
    client timeout

Firewall recovery：

    DROP rule removed
    timeout changed to refused
    SYN + RST observed

NIC：

    RX errors = 0
    RX dropped = 0
    TX errors = 0
    TX dropped = 0
    tx_timeouts = 0

結論：

    本次兩個 failure case 都不是 NIC / driver fault。

---

## Interview Review

**Q1：Connection refused 和 timeout 在 tcpdump 上通常有什麼差別？**  
A：Connection refused 常見為 SYN 後收到 RST，表示 remote host 有回應但拒絕連線；timeout 則常見為 SYN 重送但沒有任何 reply，需再查 firewall、route 或 network path。

**Q2：為什麼 iptables DROP 時 NIC dropped counter 仍可能是 0？**  
A：因為封包可能已正常通過 NIC / driver，之後才在 Linux network stack 的 firewall layer 被 DROP，所以 firewall drop 不等於 NIC-level drop。
