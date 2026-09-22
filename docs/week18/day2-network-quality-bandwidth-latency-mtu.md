<!-- readable-curriculum: 2026-09-22 -->
# Week18 Day2 — Bandwidth、latency、MTU

[上一課](<day1-linux-network-troubleshooting-baseline.md>) · [本週目錄](README.md) · [下一課](<day3-packet-level-network-failure-troubleshooting.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

吞吐不足可能是 TCP、CPU、路徑或封包遺失，不是單純看 NIC 規格。MTU 不一致可能影響大封包路徑，但不能未量測就把所有 timeout 歸因給 MTU。

## 在現在的專案中

本週可用 CPU 學主機網路；不把 CPU 測試或 Socket fallback 當 RDMA 硬體實測。

本課對照：[benchmark/network/run_iperf3.sh](<../../benchmark/network/run_iperf3.sh>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```bash
# 效能測試腳本（run_iperf3）：讀取參數、執行測試並輸出結果；須在具備對應工具的環境執行。
# Shell 語法：${變數} 取值，${1:-預設值} 讀取參數並提供預設；$(...) 取得指令輸出。
# 行尾反斜線延續同一指令；| 把標準輸出傳給下一指令；> 覆寫檔案，>> 附加內容。

# 設定 Shell 錯誤處理；-e 遇未被處理的指令失敗時退出，pipefail 使管線反映其中的失敗。
set -e

SERVER=${1:-iperf3-server}
TIME=${2:-30}

echo "================================"
echo " Network Benchmark"
echo "================================"

echo "Server : ${SERVER}"
echo "Runtime: ${TIME}s"

echo ""

# 網路吞吐測試：-c 指定伺服器，-t 指定測試秒數。
iperf3 \
    -c ${SERVER} \
    -t ${TIME}
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week18/day2-network-quality-bandwidth-latency-mtu.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
