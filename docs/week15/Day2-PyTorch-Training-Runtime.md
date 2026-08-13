# Week15 Day2 — PyTorch Training Runtime

## 今日目標

在既有的 **HPC AI Performance Engineering Platform** 上新增正式的 PyTorch Training Capability。

Day1 已經完成：

```text
Kubernetes
 ↓
PyTorch Runtime
 ↓
CUDA
 ↓
Tesla P100
```

Day2 進一步完成：

```text
Dataset
 ↓
DataLoader
 ↓
Training Loop
 ↓
Forward
 ↓
Loss
 ↓
Backward
 ↓
Gradient
 ↓
Optimizer
 ↓
Epoch
 ↓
Kubernetes Job
 ↓
GPU Monitoring
```

今天不是建立第二套平台，而是把 Training Workload 接進既有：

```text
Git
 ↓
ArgoCD
 ↓
Kustomize
 ↓
Helm
 ↓
Kubernetes
 ↓
GPU Node
 ↓
Prometheus / Grafana
```

---

# 1. Day2 最終架構

```text
runtime/pytorch/train.py
          │
          ▼
       Git Push
          │
          ▼
        ArgoCD
          │
          ▼
      Kustomize
          │
          ├── configMapGenerator
          │          │
          │          ▼
          │   pytorch-runtime-code
          │          │
          │          ▼
          │      /runtime/train.py
          │
          └── Helm
               │
               ▼
       pytorch-training Job
               │
               ▼
      Official PyTorch Image
               │
               ▼
       PyTorch Training Loop
               │
               ▼
          Tesla P100
               │
               ▼
        DCGM Exporter
               │
               ▼
         Prometheus
               │
               ▼
           Grafana
```

---

# 2. Training 基本資料流

Training 最核心的流程：

```text
Feature
  ↓
Model
  ↓
Prediction
  ↓
Loss ← Label
  ↓
Backward
  ↓
Gradient
  ↓
Optimizer
  ↓
Update Weight / Bias
```

這個流程會對每一個 Batch 重複。

---

# 3. Feature / Label / Prediction

## Feature

Feature 是：

> 給 Model 的輸入資料。

例如房價預測：

```text
Feature
├── 坪數
├── 屋齡
├── 捷運距離
└── ...
```

---

## Label

Label 是：

> 正確答案。

例如：

```text
Feature
30 坪、屋齡 5 年、捷運距離 300m

Label
1200 萬
```

---

## Prediction

Prediction 是：

> Model 根據 Feature 算出的答案。

例如：

```text
Prediction = 1100 萬
Label      = 1200 萬
```

Model 預測錯了多少，之後會透過 Loss 計算。

可以記成：

```text
Feature = 題目
Label = 正確答案
Prediction = Model 算出的答案
```

---

# 4. Dataset

PyTorch 中：

```python
TensorDataset(features, labels)
```

將 Feature 和 Label 配成 Dataset。

例如：

```text
features[0] + labels[0]
→ Sample 1

features[1] + labels[1]
→ Sample 2
```

所以：

```text
Dataset
├── Sample 1
├── Sample 2
├── Sample 3
└── ...
```

Dataset 的責任：

> 管理整份 Training Data，以及每筆 Sample 的 Feature / Label。

---

# 5. Sample

Sample 是：

> Dataset 裡的一筆資料。

例如：

```text
Sample 1

Feature:
[x1, x2, x3, ...]

Label:
[y]
```

所以：

```text
Sample = 一筆資料
Dataset = 全部資料
```

---

# 6. Batch

真實 Dataset 可能非常大，例如：

```text
Dataset = 500 GB
GPU VRAM = 16 GB
```

不可能整份 Dataset 一次塞進 GPU。

所以會把 Dataset 切成小批：

```text
Batch
```

例如：

```text
Dataset = 1000 Samples
Batch Size = 64
```

Training：

```text
Batch 1 → 64 Samples
Batch 2 → 64 Samples
Batch 3 → 64 Samples
...
```

最後一批可以少於 64。

---

# 7. DataLoader

DataLoader 負責：

> 從 Dataset 一批一批產生 Batch。

例如：

```python
dataloader = DataLoader(
    dataset,
    batch_size=64,
    shuffle=True,
)
```

資料流：

```text
Dataset
   ↓
DataLoader
   ↓
Batch 1
Batch 2
Batch 3
...
```

---

# 8. shuffle=True

`shuffle=True` 表示：

> 每個 Epoch 開始前重新打亂 Dataset 順序。

例如：

```text
原本：

1 2 3 4 5 6 7 8

Shuffle：

5 2 8 1 7 3 6 4
```

目的：

避免 Model 過度受到原始資料排列順序影響。

---

# 9. 從 DataLoader 取得 Batch

最開始測試時使用：

```python
features_batch, labels_batch = next(iter(dataloader))
```

可以拆成三步理解。

## iter(dataloader)

建立 DataLoader 的 iterator。

概念：

```text
DataLoader
 ↓
指向第一個 Batch
```

---

## next(...)

取下一個 Batch。

```python
next(iter(dataloader))
```

等於：

> 取得第一個 Batch。

---

## Python Unpack

DataLoader 回傳：

```text
(features, labels)
```

所以：

```python
features_batch, labels_batch = ...
```

就是：

```text
第一個值 → features_batch
第二個值 → labels_batch
```

---

# 10. CPU RAM → GPU VRAM

DataLoader 產生的 Batch 預設還是在 CPU。

例如：

```text
features_batch.device = cpu
```

要讓 GPU Training，需要：

```python
features_batch = features_batch.to(device)
labels_batch = labels_batch.to(device)
```

如果：

```python
device = torch.device("cuda:0")
```

資料流就是：

```text
CPU RAM
   ↓
PCIe
   ↓
GPU VRAM
```

---

# 11. 為什麼不是整份 Dataset 搬到 GPU？

因為真實 Dataset 通常遠大於 GPU VRAM。

所以標準流程：

```text
Disk / CPU RAM
      ↓
DataLoader
      ↓
Batch
      ↓
GPU VRAM
      ↓
Training
      ↓
Next Batch
```

這也是後續 GPU Performance Analysis 很重要的一條資料路徑。

如果 DataLoader 太慢：

```text
CPU 準備資料太慢
      ↓
GPU 等資料
      ↓
GPU Utilization 下降
```

---

# 12. Model

Day2 使用 PyTorch Model：

```python
class SimpleModel(torch.nn.Module):
```

`torch.nn.Module` 是 PyTorch 建立 Neural Network Model 的標準基礎類別。

最開始使用：

```python
torch.nn.Linear(10, 1)
```

意思：

```text
10 個 Feature
     ↓
Linear Layer
     ↓
1 個 Prediction
```

---

# 13. Weight / Bias

Linear Layer 會學：

```text
Weight
Bias
```

例如：

```text
Feature 1 × Weight 1
Feature 2 × Weight 2
Feature 3 × Weight 3
...
        +
      Bias
        ↓
Prediction
```

Training 的主要目的：

> 找到更好的 Weight / Bias，讓 Prediction 更接近 Label。

---

# 14. Weight Shape

例如：

```python
torch.nn.Linear(10, 1)
```

表示：

```text
Input = 10
Output = 1
```

因此 Weight Shape：

```text
[1, 10]
```

概念：

```text
[
  [w1, w2, w3, ... w10]
]
```

因為 1 個輸出需要一組 10 個 Weight。

---

# 15. Forward

Model：

```python
def forward(self, x):
    return self.linear(x)
```

代表資料進 Model 後的流向：

```text
Input
 ↓
Linear Layer
 ↓
Prediction
```

實際呼叫：

```python
predictions = model(features_batch)
```

PyTorch 會自動執行 `forward()`。

---

# 16. Loss

Loss 表示：

> Prediction 跟 Label 差多少。

Day2 使用：

```python
torch.nn.MSELoss()
```

MSE：

```text
Mean Squared Error
平均平方誤差
```

概念：

```text
Prediction
     │
     ▼
   Loss
     ▲
     │
   Label
```

例如：

```text
Prediction = 10
Label = 12

Difference = -2

Squared Error = 4
```

Loss 越小，通常代表 Prediction 越接近 Label。

---

# 17. Backward

計算：

```python
loss.backward()
```

作用：

> 根據 Loss 計算 Model 每個可訓練參數的 Gradient。

流程：

```text
Loss
 ↓
Backward
 ↓
Gradient
```

---

# 18. Gradient

Gradient 可以理解成：

> 如果這個 Weight 改一點點，Loss 會怎麼變。

它告訴 Optimizer：

```text
Weight 應該往哪個方向調整
```

每個 Weight 都會有對應的 Gradient。

所以：

```text
Weight Shape   = [1, 10]
Gradient Shape = [1, 10]
```

---

# 19. Optimizer

Backward 只負責：

```text
算 Gradient
```

真正修改 Weight / Bias 的是：

```text
Optimizer
```

Day2 使用：

```python
torch.optim.SGD(
    model.parameters(),
    lr=0.01,
)
```

SGD：

```text
Stochastic Gradient Descent
```

作用：

```text
Gradient
 ↓
Optimizer
 ↓
修改 Weight / Bias
```

---

# 20. model.parameters()

```python
model.parameters()
```

表示：

> 把 Model 裡所有需要學習的參數交給 Optimizer。

例如：

```text
SimpleModel
└── Linear
    ├── Weight
    └── Bias
```

Optimizer 就會管理這些參數。

---

# 21. Learning Rate

```python
lr=0.01
```

`lr`：

```text
Learning Rate
學習率
```

Gradient 決定：

```text
往哪裡走
```

Learning Rate 決定：

```text
一次走多遠
```

概念：

```text
Gradient = 方向
Learning Rate = 步伐大小
```

---

# 22. optimizer.step()

```python
optimizer.step()
```

作用：

> 根據 Gradient 真正更新 Model Weight / Bias。

所以：

```text
Backward
= 算怎麼改

Optimizer.step()
= 真的修改
```

---

# 23. optimizer.zero_grad()

PyTorch Gradient 預設會累加。

例如：

```text
Batch 1 Gradient = 0.5

Batch 2 Gradient = 0.3

如果不清：
0.5 + 0.3 = 0.8
```

所以每個 Batch 開始時：

```python
optimizer.zero_grad()
```

清除上一個 Batch 的 Gradient。

Training 順序：

```text
zero_grad
 ↓
forward
 ↓
loss
 ↓
backward
 ↓
step
```

---

# 24. Training Loop

真正 Training 不會只跑第一個 Batch。

使用：

```python
for features_batch, labels_batch in dataloader:
```

表示：

```text
Batch 1
 ↓
Training

Batch 2
 ↓
Training

Batch 3
 ↓
Training
```

每個 Batch 執行：

```text
CPU → GPU
 ↓
Forward
 ↓
Prediction
 ↓
Loss
 ↓
Backward
 ↓
Gradient
 ↓
Optimizer
 ↓
Update Model
```

---

# 25. Epoch

當整份 Dataset 全部訓練過一次：

```text
= 1 Epoch
```

例如：

```text
Dataset = 1000 Samples
Batch Size = 64
```

大約：

```text
16 Batches
= 1 Epoch
```

---

# 26. Epoch Loop

使用：

```python
for epoch in range(epochs):
```

例如：

```python
epochs = 5
```

代表：

```text
Epoch 1
→ 整份 Dataset 跑一次

Epoch 2
→ 再跑一次

...

Epoch 5
```

目的：

讓 Model 經過更多次 Weight 更新。

---

# 27. Epoch Average Loss

一開始只印：

```text
最後一個 Batch 的 Loss
```

這不能代表整個 Epoch。

所以改成：

```python
epoch_loss = 0.0
```

每個 Batch：

```python
epoch_loss += loss.item()
```

最後：

```python
average_loss = epoch_loss / len(dataloader)
```

所以：

```text
Batch Loss
= 某一批資料的 Loss

Epoch Average Loss
= 整份 Dataset 這輪的平均 Loss
```

---

# 28. 建立有規律的 Synthetic Dataset

一開始：

```python
features = torch.randn(1000, 10)
labels = torch.randn(1000, 1)
```

Feature 和 Label 都是各自亂數。

兩者沒有關係：

```text
Feature
   X
Label
```

Model 根本沒有規律可以學。

因此改成：

```python
features = torch.randn(1000, 10)

labels = features.sum(
    dim=1,
    keepdim=True,
)
```

表示：

```text
Feature 1
+
Feature 2
+
...
+
Feature 10
=
Label
```

所以 Model 有一個明確規律可以學。

---

# 29. Loss 收斂驗證

第一次成功 Training：

```text
Epoch [1/5] Average Loss: 7.249890
Epoch [2/5] Average Loss: 3.903716
Epoch [3/5] Average Loss: 2.113517
Epoch [4/5] Average Loss: 1.150443
Epoch [5/5] Average Loss: 0.619023
```

可以看到：

```text
7.24
 ↓
3.90
 ↓
2.11
 ↓
1.15
 ↓
0.61
```

Loss 持續下降。

代表：

> Model 確實正在學習 Feature → Label 的規律。

---

# 30. Kubernetes Job

Training 的生命週期：

```text
Start
 ↓
Train
 ↓
Finish
 ↓
Exit
```

所以使用：

```yaml
kind: Job
```

而不是 Deployment。

---

# 31. Training Job

建立：

```text
helm/pytorch-runtime/templates/training-job.yaml
```

核心：

```yaml
apiVersion: batch/v1
kind: Job

metadata:
  name: pytorch-training
```

Container：

```yaml
command:
  - python

args:
  - -u
  - /runtime/train.py
```

實際執行：

```bash
python -u /runtime/train.py
```

---

# 32. restartPolicy

Job：

```yaml
restartPolicy: Never
```

Training 完成後：

```text
Process Exit
 ↓
Pod Completed
```

不需要像 Deployment 一樣一直保持 Running。

---

# 33. backoffLimit

設定：

```yaml
backoffLimit: 1
```

代表：

> Training 失敗後最多再重試一次。

避免程式錯誤時一直重複建立 GPU Pod。

---

# 34. Job 與 Pod 的關係

Job 不是 Pod。

關係：

```text
Job
 ↓
建立 Pod
 ↓
Pod 執行 Container
 ↓
Container 跑 train.py
```

可以記：

```text
Deployment → 管理長時間 Running Pod

Job → 管理跑完就結束的 Pod

Pod → 真正執行 Container
```

---

# 35. Runtime Code ConfigMap

Day1 已有：

```yaml
configMapGenerator:
  - name: pytorch-runtime-code
    files:
      - runtime.py=../../../runtime/pytorch/runtime.py
```

Day2 加入：

```yaml
      - train.py=../../../runtime/pytorch/train.py
```

所以 ConfigMap：

```text
pytorch-runtime-code
├── runtime.py
└── train.py
```

Training Pod Mount：

```text
/runtime/train.py
```

---

# 36. 單 GPU Resource Conflict

Day1 的：

```text
pytorch-runtime Deployment
```

會使用：

```text
P100 × 1
```

Day2 Training Job 也需要：

```text
P100 × 1
```

但目前只有一張 GPU。

所以將：

```yaml
replicaCount: 1
```

改為：

```yaml
replicaCount: 0
```

流程：

```text
pytorch-runtime
 ↓
Scale to 0
 ↓
Release P100
 ↓
Training Job
 ↓
Allocate P100
```

---

# 37. Helm Render 驗證

執行：

```bash
helm template pytorch-runtime \
  ./helm/pytorch-runtime \
  > /tmp/pytorch.yaml
```

確認：

```text
pytorch-runtime
replicas: 0
```

以及：

```text
kind: Job
name: pytorch-training
```

---

# 38. Kustomize Render 驗證

執行：

```bash
kubectl kustomize \
  --enable-helm \
  --load-restrictor LoadRestrictionsNone \
  kustomize/overlays/dev \
  > /tmp/dev.yaml
```

確認 ConfigMap：

```bash
grep -n "train.py:" /tmp/dev.yaml
```

實際：

```text
327:  train.py: |
```

代表：

```text
runtime/pytorch/train.py
 ↓
Kustomize
 ↓
ConfigMap
```

成功。

---

# 39. GitOps Deployment

提交：

```bash
git add runtime/pytorch/train.py \
        helm/pytorch-runtime \
        kustomize/overlays/dev/kustomization.yaml
```

Commit：

```bash
git commit -m "feat: add PyTorch training workload"
```

Push：

```bash
git push origin master
```

流程：

```text
Git
 ↓
ArgoCD
 ↓
Kustomize + Helm
 ↓
Training Job
```

---

# 40. Training 第一次失敗

Job Pod：

```text
pytorch-training-xxxxx
Error
```

Logs：

```text
UnboundLocalError:
cannot access local variable 'epoch_loss'
where it is not associated with a value
```

原因：

```python
epoch_loss += loss.item()
```

但 Epoch 開始時沒有：

```python
epoch_loss = 0.0
```

---

# 41. epoch_loss 修正

正確結構：

```python
for epoch in range(epochs):
    epoch_loss = 0.0

    for features_batch, labels_batch in dataloader:
        ...
        epoch_loss += loss.item()

    average_loss = epoch_loss / len(dataloader)
```

代表：

```text
每個 Epoch 開始
 ↓
Loss 歸零
 ↓
每個 Batch 累加
 ↓
最後算平均
```

---

# 42. 為什麼 Git Push 後 Job 沒重跑？

修正 `train.py` 後：

```text
Git Push
 ↓
ArgoCD Sync
 ↓
ConfigMap 更新
```

但是 Job 已經 Failed。

而：

```text
Job Spec 沒有改
```

所以 ArgoCD 不會重新執行已存在的 Job。

---

# 43. disableNameSuffixHash

目前：

```yaml
generatorOptions:
  disableNameSuffixHash: true
```

所以 ConfigMap 名稱固定：

```text
pytorch-runtime-code
```

即使 `train.py` 內容改變：

```text
ConfigMap 名稱仍然相同
```

Job Template：

```yaml
configMap:
  name: pytorch-runtime-code
```

也沒有改。

所以：

```text
ConfigMap Change
≠
Job Restart
```

---

# 44. 重新觸發 Job

使用：

```bash
kubectl delete job pytorch-training \
  -n hpc-platform-dev
```

因為 Git 裡仍然存在：

```text
pytorch-training Job
```

Cluster 裡被手動刪掉：

```text
Actual State
≠
Desired State
```

ArgoCD `selfHeal` 會：

```text
重新建立 Job
 ↓
建立新的 Pod
 ↓
讀取最新 ConfigMap
 ↓
重新執行 train.py
```

---

# 45. ArgoCD Desired State

可以理解：

```text
Git
= Desired State

Cluster
= Actual State
```

如果：

```text
Git：Job 應該存在
Cluster：Job 不存在
```

ArgoCD Self Heal：

```text
重新 Create Job
```

但如果：

```text
Git：Job 存在
Cluster：Job Failed 但仍然存在
```

Manifest 仍然一致。

所以 ArgoCD 不一定重新執行它。

---

# 46. Training Job 成功

最後：

```bash
kubectl get job pytorch-training \
  -n hpc-platform-dev
```

實際：

```text
NAME               STATUS     COMPLETIONS   DURATION
pytorch-training   Complete   1/1           12s
```

代表：

```text
Training Pod
 ↓
train.py
 ↓
Training 完成
 ↓
Process Exit 0
 ↓
Pod Completed
 ↓
Job Complete
```

---

# 47. 為什麼第一次 Grafana 幾乎看不到 GPU？

第一次 Training：

```text
Dataset = 1000
Features = 10
Batch = 64
Model = Linear(10 → 1)
```

對 P100 來說運算量非常小。

而 Prometheus：

```text
scrape_interval = 15s
```

代表每 15 秒抓一次 GPU Metric。

如果 GPU Workload 很短：

```text
Prometheus Scrape
      ↓

|---------------15s---------------|

     GPU Burst
        |--|
```

可能剛好完全沒採樣到。

---

# 48. Grafana Refresh 與 Prometheus Scrape 不同

Grafana：

```text
Refresh = 10s
```

意思：

> 每 10 秒重新 Query Prometheus。

Prometheus：

```text
scrape_interval = 15s
```

意思：

> 每 15 秒去 Exporter 抓一次 Metric。

資料流：

```text
DCGM Exporter
      ↑
      │ scrape 15s
      │
Prometheus
      ↑
      │ query 10s
      │
Grafana
```

---

# 49. 放大 Training Workload

為了讓 GPU 指標更容易觀察，將 Dataset 放大：

```python
features = torch.randn(20000, 1024)
```

意思：

```text
20000 Samples
每筆 1024 Features
```

Shape：

```text
[20000, 1024]
```

---

# 50. 放大 Model

Model 改成：

```python
class SimpleModel(torch.nn.Module):
    def __init__(self):
        super().__init__()

        self.layer1 = torch.nn.Linear(1024, 4096)
        self.layer2 = torch.nn.Linear(4096, 1)

    def forward(self, x):
        x = self.layer1(x)
        x = torch.relu(x)
        return self.layer2(x)
```

架構：

```text
1024 Features
      ↓
Linear
      ↓
4096 Hidden Features
      ↓
ReLU
      ↓
Linear
      ↓
1 Prediction
```

---

# 51. Linear(1024, 4096)

```python
torch.nn.Linear(1024, 4096)
```

表示：

```text
Input = 1024
Output = 4096
```

一筆 Sample：

```text
[x1 ... x1024]
      ↓
Linear
      ↓
[h1 ... h4096]
```

4096 個數值不是 Label。

它們是：

```text
Hidden Features
```

也就是 Model 中間的 Representation。

---

# 52. Model Parameter 數量

第一層：

```text
1024 × 4096
=
4,194,304 Weights
```

另外還有：

```text
4096 Bias
```

跟原本：

```text
Linear(10 → 1)
```

只有大約 10 個 Weight 相比，GPU 計算量大幅增加。

---

# 53. ReLU

使用：

```python
torch.relu(x)
```

作用：

> 對中間結果做 Non-linear Activation。

目前先理解：

```text
Linear
 ↓
ReLU
 ↓
Linear
```

讓 Model 不只是單純多層線性變換。

---

# 54. 放大 Batch

原本：

```text
batch_size = 64
```

改成：

```text
batch_size = 512
```

所以每次 GPU 處理：

```text
512 Samples
×
1024 Features
```

再進入：

```text
1024 → 4096 → 1
```

每個 Batch 的 GPU Compute 增加很多。

---

# 55. 放大 Epoch

為了讓 Prometheus 有足夠時間採樣：

```python
epochs = 100
```

目的：

```text
Training Duration ↑
 ↓
Prometheus Samples ↑
 ↓
Grafana 更容易看到 GPU 行為
```

不是因為 Day2 一定需要訓練 100 Epoch。

---

# 56. 放大後 GPU Monitoring 結果

Grafana 實際看到 Training 時：

```text
GPU Utilization
0% → 約 19%

GPU Power
約 27W → 約 42W

VRAM Used
0 → 約 400 MiB

VRAM Free
約 16260 MiB → 約 15870 MiB

GPU Temperature
約 41°C → 約 43°C
```

這些 Metric 在同一時間變化。

證明：

```text
Training Job
 ↓
PyTorch
 ↓
CUDA
 ↓
P100
 ↓
Real GPU Compute
```

---

# 57. GPU Utilization 約 19% 代表什麼？

代表：

```text
GPU 有在工作
```

但：

```text
GPU 沒有被完全吃滿
```

可以理解：

```text
GPU Capacity
████████████████████ 100%

Current Workload
████                 ~19%
```

這不是 Day2 失敗。

Day2 的目標不是：

```text
GPU = 100%
```

而是驗證：

```text
Training Workload
確實使用 GPU
+
GPU 行為可以被觀測
```

---

# 58. Training Success 不等於 GPU Efficiency

Day2 很重要的 Performance Engineering 觀念：

```text
Training Successfully Completed
≠
GPU Efficiently Utilized
```

即使 Job：

```text
Complete
```

GPU Utilization 還是可能：

```text
10%
20%
30%
```

原因可能是：

```text
Model 太小
Batch 太小
DataLoader 太慢
CPU Bottleneck
PCIe Transfer
GPU Kernel 太短
```

這些是後續 Performance Engineering 要分析的問題。

---

# 59. VRAM 為什麼只有幾百 MiB？

第一層有：

```text
4,194,304 Weights
```

如果是 FP32：

```text
每個 Weight = 4 Bytes
```

所以：

```text
4.2M × 4 Bytes
≈ 16 MB
```

再加：

```text
Gradient
Activation
Batch Tensor
CUDA Context
PyTorch Allocator
```

最後才會到 Grafana 看到的幾百 MiB。

所以：

> 參數數量很大，不代表一定會使用很多 GB VRAM。

---

# 60. Day2 最終 Training Pipeline

```text
Synthetic Dataset
       ↓
DataLoader
       ↓
Batch
       ↓
CPU RAM
       ↓
.to(cuda)
       ↓
GPU VRAM
       ↓
Model
       ↓
Forward
       ↓
Prediction
       ↓
MSE Loss
       ↓
Backward
       ↓
Gradient
       ↓
SGD Optimizer
       ↓
Update Weight / Bias
       ↓
Next Batch
       ↓
Next Epoch
```

---

# 61. Kubernetes Training Pipeline

```text
Git
 ↓
ArgoCD
 ↓
Kustomize
 ↓
ConfigMap
 ↓
Helm
 ↓
Kubernetes Job
 ↓
Training Pod
 ↓
PyTorch
 ↓
CUDA
 ↓
Tesla P100
```

---

# 62. Observability Pipeline

```text
Tesla P100
 ↓
NVIDIA DCGM
 ↓
DCGM Exporter
 ↓
Prometheus
 ↓
Grafana
```

主要觀測：

```text
GPU Utilization
GPU Power
GPU Temperature
VRAM Used
VRAM Free
VRAM Total
```

---

# 63. Day2 最重要的 10 個觀念

```text
Feature
= Model 輸入

Label
= 正確答案

Prediction
= Model 預測結果

Loss
= Prediction 與 Label 的誤差

Backward
= 計算 Gradient

Gradient
= 告訴參數應該怎麼調

Optimizer
= 真正修改參數

Batch
= 一次送進 Training 的一批資料

Epoch
= 整份 Dataset 訓練一次

Job
= 執行跑完即結束的 Training Workload
```

---

# 64. Day1 vs Day2

Day1：

```text
Can PyTorch Use GPU?
        ↓
Runtime Validation
```

Day2：

```text
Can Platform Run Training?
        ↓
Dataset
DataLoader
Forward
Loss
Backward
Optimizer
Epoch
        ↓
Kubernetes Job
        ↓
GPU Monitoring
```

---

# 65. Day2 最終成果

完成：

```text
Existing HPC AI Platform
          │
          ▼
PyTorch Training Capability
          │
          ├── Dataset
          ├── DataLoader
          ├── Batch Training
          ├── GPU Data Transfer
          ├── Model
          ├── Forward
          ├── Prediction
          ├── Loss
          ├── Backward
          ├── Gradient
          ├── Optimizer
          ├── Epoch
          ├── Kubernetes Job
          ├── GitOps Deployment
          ├── Loss Convergence
          └── GPU Monitoring
```

實際驗證：

```text
Job Status = Complete

Loss:
7.249890
→ 3.903716
→ 2.113517
→ 1.150443
→ 0.619023
```

GPU Monitoring：

```text
GPU Utilization → 約 19%
GPU Power → 約 42W
VRAM Used → 約 400 MiB
GPU Temperature → 約 43°C
```

---

# Day2 一句話複習

```text
Week15 Day2 將 PyTorch Training 正式接進既有 HPC AI Platform，
使用 Kubernetes Job 執行完整 Training Loop，
完成 Dataset → DataLoader → Forward → Loss → Backward → Optimizer，
並透過 DCGM / Prometheus / Grafana 驗證 GPU Training 行為與資源使用。
```

---

# Interview

## Q1：為什麼 Training Workload 適合 Kubernetes Job，而不是 Deployment？

Training 的生命週期是：

```text
Start
 ↓
Train
 ↓
Finish
 ↓
Exit
```

它不是需要永久保持 Running 的 Service。

Kubernetes Job 的目標是：

```text
Pod 成功完成指定工作
```

所以 Training、Batch Processing、Benchmark 等 workload 通常更適合 Job。

Deployment 則更適合：

```text
API
Inference Service
Web Service
```

這些需要持續 Running 的服務。

---

## Q2：PyTorch Training 一個 Batch 的核心流程是什麼？

核心：

```text
Batch
 ↓
Move Data to GPU
 ↓
optimizer.zero_grad()
 ↓
Forward
 ↓
Prediction
 ↓
Loss
 ↓
Backward
 ↓
Gradient
 ↓
optimizer.step()
 ↓
Update Model Parameters
```

其中：

```text
zero_grad()
= 清上一個 Batch 的 Gradient

backward()
= 計算新的 Gradient

optimizer.step()
= 根據 Gradient 更新 Weight / Bias
```

這套流程會對每個 Batch 重複，整份 Dataset 跑完一次就是 1 Epoch。
