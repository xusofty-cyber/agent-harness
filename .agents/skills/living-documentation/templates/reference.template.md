---
id: REF-XXX
title: "[模块名称] 接口协议与配置详细说明"
type: reference
status: draft
modules:
  - "apps/your_module/**"
  - "apps/config/system.ini"
depends_on:
  - "docs/architecture/ARCH-XXX.md"
version: 0.1.0
last_verified_commit: HEAD
---

# 接口协议与配置详细说明：[模块名称]

## 1. 配置项速查字典 (`system.ini` / 配置参数)
| 配置小节 `[Section]` | 键名 `Key` | 数据类型 | 默认值 | 作用说明与取值范围 |
| :--- | :--- | :--- | :--- | :--- |
| `[Server]` | `Port` | 整数 | `8080` | 服务监听端口，范围 1024-65535 |
| `[Security]` | `CertPath` | 路径字符串 | `/etc/cert.pem` | 国密/SSL 证书文件路径 |

## 2. API / 协议报文规格
### 2.1 [接口/命令名称 1]
- **请求方式 / 协议**：[如：TCP 报文 / HTTP POST / 信号槽]
- **报文格式 / 路径**：[报文头结构或 URL 路径]
- **请求字段说明**：
  | 字段名 | 类型 | 必填 | 说明 |
  | :--- | :--- | :--- | :--- |
  | `cmd_id` | uint16 | 是 | 命令标识码 (如 `0x0102`) |
  | `payload` | bytes | 否 | 业务负载数据 |

- **响应字段说明**：
  | 字段名 | 类型 | 说明 |
  | :--- | :--- | :--- |
  | `status` | int32 | 返回状态码（0 代表成功，非 0 见错误码表） |
  | `data` | json/bytes | 响应内容 |

## 3. 状态码与异常代码字典
| 错误码 (Dec/Hex) | 符号常量 | 含义与排查指引 |
| :--- | :--- | :--- |
| `0` / `0x0000` | `SUCCESS` | 操作成功完成 |
| `-1` / `0xFFFF` | `ERR_NETWORK_TIMEOUT` | 网络超时，检查对端连接或防火墙设置 |
| `-2` / `0xFFFE` | `ERR_CERT_INVALID` | 证书无效或已过期，需重新签发证书 |
