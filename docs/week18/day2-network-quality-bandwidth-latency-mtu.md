# Week18 Day2 — Bandwidth / Latency / Packet Loss / MTU

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
