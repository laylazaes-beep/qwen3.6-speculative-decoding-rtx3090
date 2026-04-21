# Benchmark environment snapshot

_Collected at 2026-04-21T08:00:30+08:00_

## Hardware
```
index, name, memory.total [MiB], driver_version, compute_cap
0, NVIDIA GeForce RTX 3090, 24576 MiB, 580.126.09, 8.6
1, NVIDIA GeForce RTX 3090, 24576 MiB, 580.126.09, 8.6

--- CPU ---
CPU(s):                                  16
On-line CPU(s) list:                     0-15
Model name:                              11th Gen Intel(R) Core(TM) i7-11700 @ 2.50GHz
Thread(s) per core:                      2
Socket(s):                               1
CPU(s) scaling MHz:                      74%
CPU max MHz:                             4900.0000
CPU min MHz:                             800.0000
NUMA node0 CPU(s):                       0-15

--- RAM ---
               total        used        free      shared  buff/cache   available
Mem:            62Gi       6.5Gi       5.9Gi       126Mi        50Gi        56Gi
Swap:          8.0Gi       904Ki       8.0Gi
```

## OS / kernel
```
Linux s1 6.17.0-20-generic #20~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Thu Mar 19 01:28:37 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
Distributor ID:	Ubuntu
Description:	Ubuntu 24.04.4 LTS
Release:	24.04
Codename:	noble
PRETTY_NAME="Ubuntu 24.04.4 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
VERSION="24.04.4 LTS (Noble Numbat)"
VERSION_CODENAME=noble
```

## CUDA / driver
```
collect_env.sh: line 35: nvcc: command not found

Tue Apr 21 08:00:30 2026       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.126.09             Driver Version: 580.126.09     CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
```

## llama.cpp
```
commit    : 97895129e5f2bde94d13dc01ca41ee79e9b629f2
short     : 9789512
describe  : N/A
authored  : 2026-04-20 23:30:38 +0200
subject   : ggml-cuda: flush legacy pool on OOM and retry (#22155)
```

## Models
```
21G /home/reachym/benchmarks/models/qwen3.6-ud-q4kxl/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf
508M /home/reachym/benchmarks/models/qwen3.5-0.8b/Qwen3.5-0.8B-Q4_K_M.gguf
379M /home/reachym/benchmarks/models/qwen3-0.6b/Qwen3-0.6B-Q4_K_M.gguf
ac2d97712095a558e31573f62f466a3f9d93990898b0ec79d7c974c1780d524a  Qwen3-0.6B-Q4_K_M.gguf
bd258782e35f7f458f8aced1adc053e6e92e89bc735ba3be89d38a06121dc517  Qwen3.5-0.8B-Q4_K_M.gguf
707a55a8a4397ecde44de0c499d3e68c1ad1d240d1da65826b4949d1043f4450  Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf
```

## Python packages (venv)
```
Python 3.12.3
huggingface_hub==1.3.0
matplotlib==3.10.8
numpy==2.4.4
requests==2.33.1
urllib3==2.6.3
```

## Build flags (for reference)
```
cmake flags used:
  -DGGML_CUDA=ON
  -DCMAKE_CUDA_ARCHITECTURES=86   # RTX 3090 SM 8.6
  -DLLAMA_CURL=OFF
  -DBUILD_SHARED_LIBS=OFF
  CUDACXX=/usr/local/cuda-12.6/bin/nvcc
```

## Server invocation template
```
llama-server \
  -m Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf \
  --host 127.0.0.1 --port 18123 \
  -ngl 999 -c 16384 --jinja \
  -fa on -ctk q8_0 -ctv q8_0 --no-webui
  # + per-config spec-decode flags (see run_p0_matrix.sh / run_matrix.sh)
```

## Environment variables at bench time
```
HOME=/home/reachym
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
```
