---
id: GUIDE-XXX
title: "[特性/系统] 用户使用与运维操作指南"
type: guide
status: draft
modules:
  - "apps/your_module/**"
depends_on:
  - "docs/architecture/ARCH-XXX.md"
version: 0.1.0
last_verified_commit: HEAD
---

# 用户使用与运维操作指南：[特性/系统]

## 1. 目标与适用范围
- 本指南面向人群：运维工程师、实施人员、终端操作人员。
- 适用场景：新环境部署、证书签发与更新、日常服务启停、系统故障恢复。

## 2. 前置环境与依赖准备
- **硬件架构**：[如：ARM am335x / x86_64]
- **系统环境**：[如：Linux, glibc 2.27+, 交叉编译工具链]
- **必要工具**：[如：gmssl CLI, systemd, openssl]

## 3. 操作步骤指南 (Step-by-Step)

### 步骤 1：[环境配置 / 证书准备]
```bash
# 示例命令
gmssl req -inform der -in request.csr -outform pem -out request-fixed.csr
```
> **注意**：[关键提示，例如格式转换时的注意事项]

### 步骤 2：[编译构建 / 安装部署]
```bash
# 执行交叉编译构建
./make_arm.sh
```

### 步骤 3：[服务启动与状态检查]
```bash
# 启动服务
./nrsecServer -c apps/config/system.ini

# 查看运行状态
ps aux | grep nrsecServer
```

## 4. 常见问题排查与 FAQ
| 常见现象 / 错误日志 | 产生原因 | 解决处置方案 |
| :--- | :--- | :--- |
| `bind failed: Address already in use` | 端口被已有进程占用 | 查找并终止旧进程：`fuser -k <端口>/tcp` |
| `Certificate verify failed` | 证书链不完整或格式错误 | 检查证书格式，按步骤 1 执行 PEM 格式转换 |
