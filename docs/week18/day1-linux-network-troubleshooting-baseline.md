<!-- current-curriculum: 2026-09-22 -->
# Week18 Day1 — Linux 網路 baseline

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-network-quality-bandwidth-latency-mtu.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Linux 網路 baseline」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

ip addr 看介面與位址，ip route 看路由，ss 看 listener／連線；DNS 則把名字轉位址。沒有先定義 source namespace 就說某 port 不通，可能混淆 host 和容器視角。

## 在現在的專案中

本週可用 CPU 學主機網路；不把 CPU 測試或 Socket fallback 當 RDMA 硬體實測。

本課對照：[helm/api/templates/service.yaml](<../../helm/api/templates/service.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
  ports:
    - port: {{ .Values.service.port }}
      # Service 將流量轉送至 Pod 的目標埠號或命名埠。
      targetPort: {{ .Values.service.targetPort }}
      {{- if eq .Values.service.type "NodePort" }}
      # 經節點 IP 開放的 Service 埠號，適用 NodePort／部分 LoadBalancer 配置。
      nodePort: {{ .Values.service.nodePort }}
      {{- end }}
```

## 閱讀與練習

遇到「API 連不通」時，先寫下你從 host、哪個 Pod 或哪台 VM 出發，再依序問：

| 問題 | 本機可用的觀察 | 判讀限制 |
|---|---|---|
| 本機有哪些位址與路由？ | `ip addr`、`ip route` | 容器的視圖不一定等於 host |
| 服務有沒有監聽？ | `ss -lnt` | 只能看到所在網路視圖的 listener |
| 名稱能否解析？ | 在正確環境查 DNS，例如 `getent hosts localhost` | localhost 可解析不代表叢集 Service DNS 正常 |
| 應用是否回應？ | 對你自己掌控的測試服務發起單次請求 | ping 成功不能代替 TCP／HTTP 檢查 |

若目標是 Kubernetes Service，下一層再查 selector／ready endpoints；不要在還沒確認 listener 或 DNS 前就改防火牆。tcpdump 抓包另需權限、明確介面與篩選，且不得公開敏感 payload。

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 在自己的 Linux 執行 ip addr、ip route、ss -lnt，選一個 listener 說明 bind 位址；再對照 API Service，不需要向外掃描網段。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '24,31p' 'helm/api/templates/service.yaml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/network-policy-validation-20260921.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week18/day1-linux-network-troubleshooting-baseline.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
