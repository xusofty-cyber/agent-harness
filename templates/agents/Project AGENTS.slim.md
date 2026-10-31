# Project AGENTS.md

<!-- Slim variant: installed by the minimal/standard deploy tiers (D-009,
     ablation #2). The full template ships with the full tier. -->

- 本文件是当前项目的根指令文件，补充 Global AGENTS.md 的通用底线，提供本项目专有的工程上下文。细粒度规则存放于 `.agents/rules/`，按需查阅。

## 项目概览

- **项目名称**：`<PROJECT_NAME>`
- **业务定位**：`<PROJECT_PURPOSE>`
- **核心维护者**：`<OWNERS>`
- **代码仓库与默认分支**：`<REPOSITORY_URL>`；默认分支 `<DEFAULT_BRANCH>`

## 常用开发命令（CLI 上下文）

> 运行命令前先确认工作目录。必须采用过滤参数防日志刷屏，严禁将全量日志直接倒进上下文。

```bash
<INSTALL_COMMAND>       # 依赖管理 / 构建配置
<DEV_COMMAND>           # 本地开发
<BUILD_COMMAND>         # 编译构建
<UNIT_TEST_COMMAND>     # 精准单测与验证（改动后必须运行，输出须精简）
<LINT_COMMAND>          # 代码质量 / Lint
<FORMAT_COMMAND>        # 格式化
<TYPE_CHECK_COMMAND>    # 类型检查
<MIGRATION_COMMAND>     # 数据迁移与发布（高危操作需确认）
```

## 技术栈与运行环境

| 类别 | 技术选型与版本 |
|---|---|
| **语言 & 运行时** | `<LANGUAGE_AND_VERSION>` |
| **包管理器 / 构建工具** | `<PACKAGE_MANAGER>` |
| **核心框架 / 第三方库** | `<FRAMEWORK>` |
| **持久层 & 存储** | `<DATABASE_AND_CACHE>` |
| **CI/CD 配置** | `<CI_PATH>` |

## 架构核心红线

1. **单向分层依赖**：上层调用下层，底层严禁反向引用上层业务，严禁模块间循环依赖。
2. **统一异常流**：业务错误必须抛出统一封装的业务异常，严禁静默吞掉异常；异步必须包含错误捕获。
3. **配置隔离**：所有配置通过统一环境变量/配置模块读取，严禁深层硬编码。
4. **日志脱敏**：敏感字段（PII、Token、密码）必须掩码脱敏。
5. **Git 安全**：见 Global AGENTS.md「授权边界与 Git 安全铁律」；禁止 `git add .` 与 force push。

## 工作方式

- 先理解现有实现，再选最小正确方案；功能实现按需查阅 `test-driven-development`，复杂 Bug 用 `systematic-debugging`（先证据、后假设、再修复，严禁创可贴盲修）。
- 分支流转与高危操作分别遵守 `.agents/rules/git-workflow.md` 与 `.agents/rules/security-boundary.md`。
- 长输出先落盘再摘要，不把全量日志倒进上下文。

## 动态记忆与任务追踪

- **会话启动**：在文件存在且与任务相关时，查阅 `PROJECT_CONTEXT.md` 与 `SESSION_STATE.md` 并核实其时效。
- **会话断点**：在有意义的任务边界更新 `SESSION_STATE.md`（已完成事项、实际验证证据、未完成步骤、仍有效的风险）；只有长期事实变化时才改 `PROJECT_CONTEXT.md`。
- **来源与安全**：推断标记为推断；不保存凭证、私钥或原始个人数据。

## 功能完成检查清单（Definition of Done）

若存在 `gate/feature_list.json`，全程用 `python3 gate/pass-gate.py` 驱动（`pass-gate.py status` ➔ `pass-gate.py start` [WIP=1] ➔ `pass-gate.py verify` ➔ `pass-gate.py check-clean`），严禁直接手改 `feature_list.json`：

1. [ ] **测试与门禁验证**：运行相关测试及 `python3 gate/pass-gate.py verify --id <id>`，确认 exit 0 并留存真实运行证据
2. [ ] **更新 SESSION_STATE.md 并交接检查**：记录已完成事项与验证证据，运行 `python3 gate/pass-gate.py check-clean` 确认五维干净
3. [ ] **代码审查**：完成功能或合并前执行代码审查，Critical / High 缺陷清零
