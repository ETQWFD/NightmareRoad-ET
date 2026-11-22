# Nightmare Road-ET Server 1.8.0

本地 AI 绘图服务端（Windows / Linux x86_64），由 C 外壳 + stable-diffusion.cpp `sd-server` CPU 引擎 + Python 管理端组成。

## 1.8.0 修复重点
- **模型完整性**：`.part` 断点续传；下载前实测总字节；完成必须与实测/清单完全一致；safetensors 读文件头；已知模型按清单字节数复核。半截文件不再被当成“已就绪”。
- **模型路径自愈**：`data/models` 为唯一仓库；相对 `model_path` 自动按仓库解析；失效路径启动前自动改成仓库中最大的有效模型。
- **下载可见**：Python 管理端显示绝对保存路径、已下载/总字节、速度、ETA、`.part` 位置；C 外壳向导打印完整保存路径。
- **引擎自检**：按 `engine/`、`bin/`、程序根、`runtime/` 多位置探测；管理端真实执行 `sd-server --help`；缺 DLL/so、无权限、架构不符输出原始原因。
- **配置对称**：`engine_args` 现在既保存也加载；Linux 启动时按空格拆分传给 `sd-server`（旧版完全忽略）。
- **部署**：Windows 包内置精简 Python 3.11 + tkinter；首次启动自动建 `data/config`、`data/logs`、`data/models`。

## 目录
```
data/
├─ models/      # 唯一模型仓库（界面显示绝对路径）
├─ config/etserver.conf
├─ logs/server.log
└─ run/
```

## 构建
Linux: `./build.sh`
Windows: `./build.sh win`（需要 `x86_64-w64-mingw32-gcc`）

## 验证
- `etserver --selftest`：全部 PASS
- `etserver --diag`：显示程序目录、数据目录、模型仓库、配置文件、引擎、模型可用性与网络
- 实测：DreamShaper 8 / 4 steps / 256×256 通过 `/sdapi/v1/txt2img` 出图（约 60s CPU）
