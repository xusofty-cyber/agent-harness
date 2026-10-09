# Project AGENTS.md

## 继承与定位

- 本文件是当前项目的根指令文件，补充 [Global AGENTS.md] 的通用底线，提供本项目专有的工程上下文。
- 采用**渐进式披露（Progressive Disclosure）**架构，本项目的高频红线与命令在此维护，细粒度规则存放于 `.agents/rules/`，Agent 仅在需要时按需查阅。

## 项目概览

- **项目名称**：`<PROJECT_NAME>`
- **业务定位**：`<PROJECT_PURPOSE>`（一句话说明核心业务场景与目标受众）
- **核心维护者**：`<OWNERS>`
- **代码仓库与默认分支**：`<REPOSITORY_URL>`；默认分支 `<DEFAULT_BRANCH>`（以远端 `origin/HEAD` 为准）

## 常用开发命令（CLI 上下文）

> 运行命令前先确认工作目录。必须采用过滤参数防日志刷屏，严禁将全量日志直接倒进上下文。

```bash
# 1. 依赖管理 / 构建配置
<INSTALL_COMMAND>                  # 例：npm ci / poetry install / cmake -B build / go mod download / cargo check

# 2. 本地开发与编译构建
<DEV_COMMAND>                      # 例：npm run dev / python main.py / cargo run
<BUILD_COMMAND>                    # 例：npm run build / cmake --build build / go build ./... / cargo build --release

# 3. 精准单测与验证（改动后必须运行，输出须精简）
<UNIT_TEST_COMMAND>                # 例：npm test -- --reporter=dot / pytest -q / ctest --output-on-failure
<TARGETED_TEST_COMMAND>            # 针对单文件的测试：npm test -- <path> / pytest <path> -q / ctest -R <test_name>
<INTEGRATION_TEST_COMMAND>         # 集成测试：npm run test:e2e

# 4. 代码质量、Lint 与静态检查
<LINT_COMMAND>                     # 例：npm run lint / ruff check . / clang-tidy / golangci-lint run / cargo clippy
<FORMAT_COMMAND>                   # 例：npm run format / black . / clang-format -i / gofmt -w . / cargo fmt
<TYPE_CHECK_COMMAND>               # 例：npm run typecheck / mypy .

# 5. 数据迁移与发布（高危操作需确认）
<MIGRATION_COMMAND>                # 例：npm run db:migrate / alembic upgrade head
```

## 技术栈与运行环境

| 类别 | 技术选型与版本 | 补充说明 |
|---|---|---|
| **语言 & 标准/运行时** | `<LANGUAGE_AND_VERSION>` | 例：C++20 / Python 3.11 / TypeScript 5.4 (Node 20) / Go 1.22 / Rust 1.78 |
| **包管理器 / 构建工具** | `<PACKAGE_MANAGER>` | 例：CMake+Ninja / Conan / Poetry / pnpm / Cargo / Go Modules |
| **核心框架 / 第三方库** | `<FRAMEWORK>` | 例：Qt 6 / Boost / FastAPI / Next.js / Gin / Tokio |
| **持久层 & 存储** | `<DATABASE_AND_CACHE>` | 例：PostgreSQL 16 / SQLite 3 / Redis 7 |
| **CI/CD 配置** | `<CI_PATH>` | 例：`.github/workflows/ci.yml` / `.gitlab-ci.yml` |

## 架构核心红线

1. **单向分层依赖**：上层调用下层，底层严禁反向引用上层业务，严禁模块间循环依赖。
2. **统一异常流**：业务错误必须抛出统一封装的业务异常，严禁静默吞掉异常；异步必须包含错误捕获。
3. **配置隔离**：所有配置通过统一环境变量/配置模块读取，严禁深层硬编码或直接读取原生 env。
4. **日志脱敏**：任何打印到控制台或日志的敏感字段（PII、Token、密码）必须掩码脱敏。
5. **风险分级**：按 `.agents/rules/security-boundary.md` 区分提醒、告知与必须授权的操作；文件数量本身不构成确认门槛。
6. **Git 受保护分支隔离**：禁止在受保护分支（develop/master/main）直接改代码，改动一律切临时分支，严禁 `git add .` 防误提交。

## 子级规则与工程技能调度矩阵（按需查阅与唤醒）

为避免上下文单次加载膨胀，以下细粒度规约与专业技能存放在 `.agents/rules/` 与 `.agents/skills/`，相关场景按需查阅或调用；需要外部 CLI / MCP 的技能仅在其已安装并配置后可运行：

| 研发场景 | 绑定规则 / 技能 | 唤醒语法与触发动作 | 预期行为规范 |
|---|---|---|---|
| **分支流转 / 提交 / 推送** | `git-workflow.md` | 涉及任何 `git commit` / `git push` / 分支切换 | 严格在临时分支提交；禁止 `git add .`；触碰共享远端必须明确授权；禁 force push |
| **高危操作 / 核心结构变更** | `security-boundary.md` | 触发规则定义的授权门槛 | 按风险等级说明影响；仅明确要求授权的操作暂停等待 |
| **复杂需求 / 架构改造** | `engineering-spec.md` + 可选 `comet` / `openspec` 工作流 | 用户指定工作流或项目已配置该工作流 | 遵守所选工具当前版本的流程与状态文件；未配置时按任务需要规划，不假定自动守卫 |
| **代码依赖 / 找符号引用** | `token-discipline.md` + 可选 `codegraph` | CodeGraph MCP 可用时进行语义探索；否则用限定范围的 `rg` | CodeGraph CLI/MCP 未安装配置时，不假设可调用；搜索范围应与问题相关 |
| **功能实现 / 编码阶段** | `engineering-spec.md` + `ponytail` + `test-driven-development` | 按需查阅已部署的 Skill；测试按任务风险和项目要求执行 | 先理解现有实现，再选最小正确方案；遵循适用的 Ponytail 阶梯验证 |
| **复杂 Bug / 偶现排障** | `engineering-spec.md` + `systematic-debugging` | 粘贴完整报错 Trace | 严禁创可贴盲修；必须先收集证据、建立假设、定位根因再写修复 |
| **超长输出 / 测试跑批** | `token-discipline.md` + 可选 `rtk` | RTK Hook 已配置时由其改写支持的命令；否则使用 CLI 原生精简参数 | 不假定命令会被自动改写；必要时将长日志保存在本地并只汇报相关摘要 |
| **Token 告急 / 精简输出** | `Global AGENTS.md` + 可选 `caveman` | 宿主工具支持并加载该 Skill 时按需启用 | 精简表达但保留安全说明、必要上下文和技术准确性 |

---

## 动态记忆与任务追踪

- **会话启动**：在文件存在且与任务相关时，查阅 `PROJECT_CONTEXT.md` 与 `SESSION_STATE.md`；核实会影响当前工作的分支、状态、配置和实现事实。
- **项目长期记忆**：`PROJECT_CONTEXT.md` 记录经验证且跨任务有用的架构事实、硬约束、技术决策及其理由。它是项目摘要与导航入口，不取代代码、配置或正式设计文档；尽量附上来源路径或决策记录。
- **会话断点**：在有意义的任务/会话边界更新 `SESSION_STATE.md`，记录已完成工作、实际验证证据、未完成步骤和仍有效的环境风险。新会话开始时核实其内容，并删除已过期的断点；没有实质变化时不制造空更新。
- **更新范围**：只有项目长期事实发生变化时才改 `PROJECT_CONTEXT.md`；只改当前断点时只更新 `SESSION_STATE.md`。任务较小且没有新的持久事实时，不要求同步改写两者。
- **复用经验**：项目使用 `tasks/lessons.md` 时，仅记录尚未进入规则或项目文档的可复用经验；使用 `tasks/todo.md` 或工具计划记录进行中事项，避免重复维护进度。
- **来源与时效**：把推断标记为推断；易变化的事实记录日期或来源。记忆与当前用户指令、代码、配置或可复现证据冲突时，以当前指令和证据为准，并在适当时修正记忆。
- **隐私与安全**：不保存凭证、私钥、原始个人数据、完整对话/工具日志或不必要的个人信息；共享仓库不保存用户私人偏好。
- **可选长期记忆**：跨工具记忆仅使用本地 ai-memory 方案；默认不部署、不启动，也不要求 API Key。需要自动采集时，先按《多工具部署配置指南》显式安装原生 hooks/MCP，并创建本机忽略的 `.ai-memory.toml`；未启用或服务不可用时继续依靠本仓库 Markdown，不得阻塞任务。记忆只辅助导航，必须用当前代码、规范和证据复核。
- **共享记忆技能**：涉及跨会话延续、长期项目决策、研究或文档/设计方案时，按需使用 `.agents/skills/cross-tool-memory/SKILL.md`；不保存完整对话、凭证或未经核实的结论。
- **活体文档与代码追溯**：项目长期技术文档统一维护于 `docs/` 下（需求 `docs/specs/`、架构 `docs/architecture/`、接口与配置参考 `docs/reference/`、用户操作指南 `docs/guides/`）。各文档头部 Frontmatter 声明 `modules`（关联代码路径）与 `depends_on`。在开发或使用 `/comet` 流程时，按启发式阈值（新增模块、改动 2+ 接口或关键配置）同步更新对应文档，保证代码与文档双向追溯；详见 `.agents/skills/living-documentation/SKILL.md`。
## 目录级规则索引

当项目为 Monorepo 或存在高隔离独立子模块时，仅在必要子目录下按需创建 `AGENTS.md`：
- 在确有独立边界的子模块中新增其 `AGENTS.md`，定义专属 In/Out Scope 与快速验证命令；普通目录直接继承本文件，避免重复根规则。
