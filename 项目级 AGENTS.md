# Project AGENTS.md

## 继承与定位

- 本文件是当前项目的根指令文件，补充 [全局 AGENTS.md]的通用底线，提供本项目专有的工程上下文。
- 采用**渐进式披露（Progressive Disclosure）**架构，本项目的高频红线与命令在此维护，细粒度规则存放于 `.agents/rules/`，Agent 仅在需要时按需查阅。

## 项目概览

- **项目名称**：`<PROJECT_NAME>`
- **业务定位**：`<PROJECT_PURPOSE>`（一句话说明核心业务场景与目标受众）
- **核心维护者**：`<OWNERS>`
- **代码仓库与默认分支**：`<DEFAULT_BRANCH>`（如 `main` / `master`）

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
5. **八大高危操作防呆**：改构建配置、新增依赖、改核心公共数据结构、改协议报文、改授权代码、改 `.gitignore`/CI、跨 3+ 文件大改前，必须先确认影响面。
6. **Git 受保护分支隔离**：禁止在受保护分支（develop/master/main）直接改代码，改动一律切临时分支，严禁 `git add .` 防误提交。

## 子级规则与工程技能调度矩阵（按需查阅与唤醒）

为避免上下文单次加载膨胀，以下细粒度规约与专业技能存放在 `.agents/rules/` 与 `.agents/skills/`，相关场景触发时必须联动调用：

| 研发场景 | 绑定规则 / 技能 | 唤醒语法与触发动作 | 预期行为规范 |
|---|---|---|---|
| **分支流转 / 提交 / 推送** | `git-workflow.md` | 涉及任何 `git commit` / `git push` / 分支切换 | 严格在临时分支提交；禁止 `git add .`；触碰共享远端必须明确授权；禁 force push |
| **高危操作 / 核心结构变更** | `security-boundary.md` | 触碰 8 大高风险操作（改构建/协议/公共头/依赖） | 暂停执行，列出变动清单与影响面，待人类明确确认后再操作 |
| **复杂需求 / 架构改造** | `engineering-spec.md` + `comet` / `openspec` | `/comet` 或 `用 openspec 规范出方案` | 自动立项生成 `docs/openspec/` 变更，出具 Proposal 契约并待人工确认，严禁盲干跳步 |
| **代码依赖 / 找符号引用** | `token-discipline.md` + `codegraph` | `codegraph explore "query"` | 严禁全库 grep，优先利用 AST 语法树图谱精确定位依赖与调用链路 |
| **功能实现 / 编码阶段** | `engineering-spec.md` + `ponytail` + `test-driven-development` | `用 ponytail 策略实现` / 先写测试 | 遵循 7 步懒人阶梯（改 1 行绝不重写 10 行，stdlib 优先）；红绿单测先行验证 |
| **复杂 Bug / 偶现排障** | `engineering-spec.md` + `systematic-debugging` | 粘贴完整报错 Trace | 严禁创可贴盲修；必须先收集证据、建立假设、定位根因再写修复 |
| **超长输出 / 测试跑批** | `token-discipline.md` + `rtk` | 默认追加精简过滤参数 | 严禁裸命令刷屏；带精简参数运行并将超长输出重定向至本地临时日志 |
| **Token 告急 / 精简输出** | `全局 AGENTS.md` + `caveman` | `/caveman` 或 `进入 caveman 模式` | 切换电报体沟通，仅出结论、Diff 与待办项，去除一切寒暄客套与免责铺垫 |

---

## 动态记忆与任务追踪

- **错题本（经验沉淀）**：`tasks/lessons.md`
  - 记录当前项目人类纠偏的技术坑点与规约；新会话或类似改动前优先阅读，**同一错误不犯第二次**。
- **进行中任务清单**：`tasks/todo.md`
  - $\ge$ 3 步的复杂任务必须在此维护打勾清单，每完成一项打勾一项，过程透明。

## 目录级规则索引

当项目为 Monorepo 或存在高隔离独立子模块时，仅在必要子目录下按需创建 `AGENTS.md`：
- `<PATH_TO_SUBMODULE>/AGENTS.md`：定义该子模块的 In/Out Scope 与专属快速测试命令；普通目录直接继承本文件，严禁冗余泛滥。