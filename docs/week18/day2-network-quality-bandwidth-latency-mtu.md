<!-- readable-curriculum: 2026-09-22 -->
# Week18 Day2 — Bandwidth、latency、MTU

[上一課](<day1-linux-network-troubleshooting-baseline.md>) · [本週目錄](README.md) · [下一課](<day3-packet-level-network-failure-troubleshooting.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史TCP/UDP/ICMP比較。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

單流30秒與4流10秒不是完整等條件比較；971/973Mbps相近只是候選上限，未排除client/server CPU或限速。現存runner只做TCP，不能冒充本課UDP/PMTU自動化。

## 程式／設定與來源

本次核對：[benchmark/network/run_iperf3.sh](<../../benchmark/network/run_iperf3.sh>)

## 已有結果與解讀

來源：[記錄／示例原文](<day2-network-quality-bandwidth-latency-mtu.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
0.007 ms
```

0/88771 UDP datagrams loss、.007ms jitter僅限100Mbps10秒，不推論所有負載零丟包。

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

# Week18 Day2 — Bandwidth / Latency / Packet Loss / MTU

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/k8s/iperf3-server.yaml](../../benchmark/k8s/iperf3-server.yaml)
- [benchmark/k8s/iperf3-service.yaml](../../benchmark/k8s/iperf3-service.yaml)
- [benchmark/network/run_iperf3.sh](../../benchmark/network/run_iperf3.sh)：網路吞吐測試

---

## 今日完成內容

建立 `hpc-demo ↔ net-test-01` 的 cluster network quality baseline，實際量測：

- ICMP latency
- packet loss
- UDP jitter
- TCP bandwidth
- single stream vs parallel streams
- TCP retransmission
- Path MTU
- PMTU / MTU / MSS 關係

測試節點：

    hpc-demo      10.140.0.2
    net-test-01   10.140.0.9

---

## 1. Latency Baseline

使用：

    ping -c 20 10.140.0.9

結果：

    20 packets transmitted
    20 received
    0% packet loss

    rtt min/avg/max/mdev =
    0.218 / 0.312 / 1.178 / 0.202 ms

重點：

    RTT = Round Trip Time

代表：

    hpc-demo
    → net-test-01
    → hpc-demo

完整往返時間。

本次平均 RTT：

    0.312 ms

可作為目前兩台 VM 之間的 latency baseline。

`mdev`：

    表示 RTT 樣本的波動程度。

它可以幫助觀察 latency variation，但不等同於 UDP 工具計算的 jitter。

---

## 2. UDP Packet Loss / Jitter

hpc-demo：

    iperf3 -s

net-test-01：

    iperf3 -c 10.140.0.2 -u -b 100M -t 10

參數：

    -u
    = UDP mode

    -b 100M
    = 目標傳輸速率 100 Mbit/s

    -t 10
    = 測試 10 秒

結果：

    Transfer:
    119 MBytes

    Sender Bitrate:
    100 Mbits/sec

    Receiver Bitrate:
    99.6 Mbits/sec

    Receiver Jitter:
    0.007 ms

    Lost/Total Datagrams:
    0 / 88771

    Packet Loss:
    0%

重點：

    UDP 不會像 TCP 一樣自動 retransmit，
    因此適合直接觀察 datagram loss 與 jitter。

本次：

    100 Mbps UDP 壓力下
    0% packet loss
    0.007 ms jitter

---

## 3. TCP Single Stream Baseline

先前單流測試：

    iperf3 -c 10.140.0.2 -t 30

結果：

    Transfer:
    3.39 GBytes

    Bitrate:
    ~971 Mbits/sec

    Retr:
    0

這代表目前單一 TCP flow 已能接近此環境可觀察到的整體 throughput ceiling。

---

## 4. Parallel TCP Streams

使用：

    iperf3 -c 10.140.0.2 -P 4 -t 10

`-P 4`：

    同時建立 4 條 parallel TCP streams。

結果：

    [SUM] sender:
    1.13 GBytes
    973 Mbits/sec
    Retr 0

    [SUM] receiver:
    1.12 GBytes
    960 Mbits/sec

比較：

    1 stream:
    ~971 Mbits/sec

    4 streams:
    ~973 Mbits/sec

結論：

    增加 parallel streams 沒有明顯提升總 throughput。

代表目前 bottleneck 較可能在：

    VM / virtual NIC / cloud network capacity

而不是單一 TCP flow 本身。

注意：

    -P 4 不代表 bandwidth 會乘 4。

4 條 TCP streams 仍然共同競爭相同的 network capacity。

---

## 5. TCP Retransmission

本次 single stream 與 parallel stream 測試：

    Retr = 0

表示測試期間沒有觀察到 TCP retransmission。

因此目前：

    throughput 穩定
    無明顯 TCP loss symptom
    parallel flow 也沒有造成 retransmission

---

## 6. Path MTU

PMTU：

    Path MTU

代表：

    一條 end-to-end network path 上，
    能不經 fragmentation 安全通過的最大 IP packet size。

使用：

    tracepath -n 10.140.0.2

結果：

    pmtu 1460

    Resume:
    pmtu 1460
    hops 1
    back 1

所以：

    Path MTU = 1460

---

## 7. Interface MTU / Path MTU / MSS

目前驗證結果：

    Interface MTU = 1460
    Path MTU      = 1460
    TCP MSS       = 1420

IPv4 TCP：

    MTU 1460
    - IPv4 header 20
    - TCP header 20
    = MSS 1420

關係：

    Interface MTU
    = 單一 network interface 能送出的最大 IP packet

    Path MTU
    = end-to-end 路徑中可安全通過的最大 IP packet

    MSS
    = TCP segment 可承載的最大 TCP payload

本次三者一致，沒有觀察到 MTU mismatch。

---

## 8. MTU Mismatch 風險

若出現：

    Node MTU = 9000
    Path MTU = 1500

可能造成：

    large packet
        ↓
    fragmentation / drop
        ↓
    retransmission
        ↓
    latency increase
        ↓
    throughput degradation

更嚴重時可能形成：

    PMTU black hole

表現可能是：

    small packet 正常
    ping 正常
    TCP connection 可建立
    但 large transfer / distributed workload 異常

這對：

    MPI
    NCCL
    distributed training

都可能造成明顯 performance impact。

---

## 9. Network Quality Baseline

本次測試結果：

    ICMP RTT min:
    0.218 ms

    ICMP RTT avg:
    0.312 ms

    ICMP RTT max:
    1.178 ms

    ICMP packet loss:
    0%

    UDP jitter:
    0.007 ms

    UDP packet loss:
    0%

    TCP single stream:
    ~971 Mbits/sec

    TCP 4 streams:
    ~973 Mbits/sec

    TCP retransmission:
    0

    Interface MTU:
    1460

    Path MTU:
    1460

    TCP MSS:
    1420

---

## 10. Troubleshooting Interpretation

如果：

    RTT 高

優先查：

    network path
    queueing
    host contention
    routing
    cross-zone / cross-region path

如果：

    jitter 高

優先查：

    queueing
    congestion
    VM scheduling
    network contention

如果：

    packet loss 高

優先查：

    NIC drops
    firewall / network device
    congestion
    MTU mismatch
    physical / virtual network errors

如果：

    single stream 慢
    parallel streams 明顯變快

可能是：

    TCP window
    per-flow limitation
    latency-sensitive throughput limit

如果：

    single stream
    與 parallel streams
    都停在相近 throughput

可能是：

    VM / NIC / network total capacity ceiling

如果：

    small packet 正常
    large transfer 異常

應檢查：

    Interface MTU
    Path MTU
    MSS
    PMTU Discovery

---

## 今日結論

目前 `hpc-demo ↔ net-test-01` 路徑呈現：

    low latency
    zero observed packet loss
    very low UDP jitter
    ~1 Gbit/s throughput ceiling
    zero TCP retransmission
    consistent MTU / PMTU / MSS

可作為後續 HPC / AI distributed communication troubleshooting 的 network quality baseline。

---

## Interview Review

**Q1：single TCP stream 和 4 個 parallel streams throughput 幾乎一樣，代表什麼？**  
A：代表單流已接近目前環境的總 network capacity ceiling，瓶頸較可能在 VM、virtual NIC 或 cloud network，而不是單一 TCP flow。

**Q2：MTU、PMTU、MSS 分別代表什麼？**  
A：MTU 是介面可送出的最大 IP packet；PMTU 是整條 end-to-end path 可安全通過的最大 IP packet；MSS 是 TCP 可承載的最大 payload，IPv4 TCP 常見為 MSS = MTU - 20-byte IP header - 20-byte TCP header。
