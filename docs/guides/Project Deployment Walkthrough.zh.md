# Agent Harness 部署实战指南（带完整示例）

> **Language / 语言**: [English](Project%20Deployment%20Walkthrough.md) | **简体中文**

> 适用版本：agent-harness **v0.7.0**（2026-11-06 发布）
> 定位：本文是「从零把 Harness 部署进一个真实项目」的分步实战，
> 与《多工具部署与配置指南》的规范视角互补。本文所有命令均按
> v0.7.0 脚本实查核对；贯穿示例使用一个虚构项目 **shopapi**
> （Python 3.12 + FastAPI + PostgreSQL，路径 `~/projects/shopapi`），
> 另在关键处给出 JS 与 C++ 的对照命令。

---

## 0. 先说清一件事：部署分两半

Agent Harness 的部署 = **脚本搭架子** + **人工填内容**，两半缺一不可：

| 部分 | 谁做 | 内容 |
|---|---|---|
| 搭架子 | `run-pipeline.sh` 自动 | 规则文件、宿主桥接与钩子、技能、门禁代码、CI/pre-push 模板 |
| 填内容 | 维护者（可由 agent 协助、您确认） | 三份根文档的项目事实、门禁初始化、第一批工作条目 |

只跑脚本不填内容，agent 拿到的是一套带占位符的空指令，门禁也没有条目可管——等于没部署。

---

## 1. 部署前准备

| 依赖 | 必需性 | 说明 |
|---|---|---|
| `git` | 必需 | 拉取模板仓；目标项目本身也应是 git 仓库 |
| `python3` | 必需 | 门禁 `pass-gate.py` 与流水线工具只依赖标准库 |
| `bash` | Linux/macOS 必需 | Windows 改用 PowerShell 版脚本（见 §3.3） |
| `node` | 可选 | Claude Code 等宿主的钩子脚本需要 |
| `cargo` | 可选 | 仅当要装 ai-memory 跨工具记忆时需要 |

目标项目侧的要求只有两条：

1. 项目根目录路径确定、且您有写权限；
2. 您能说出这个项目的三条命令——**怎么构建、怎么测试（能证明项目可用）、怎么启动**。第 6 节门禁初始化要用，提前想好。

---

## 2. 总览：流水线做什么

`run-pipeline.sh` 按序编排 4 个阶段：

```text
阶段 1  deploy   规则与桥接部署   → 项目 AGENTS.md / 两份记忆文档脚手架 /
                                   各宿主桥接与钩子 / .agents 规则与技能 /
                                   gate/ 门禁代码 / pre-push + CI 门禁模板
阶段 2  memory   AI 记忆接入      → 可选；未装 ai-memory CLI 时自动 SKIP（正常现象）
阶段 3  skills   技能库校验/同步  → 对照 skills-lock 校验；默认只检查不覆写
阶段 4  docs     活文档影响分析   → 检查文档与代码的溯源关系是否过期
收尾             汇总表           → 每阶段 PASS / SKIP / WARN / FAIL 如实记录
```

两个模式口径先记牢：

- **默认 advisory 模式**：阶段失败记 `WARN`、流水线退出码仍为 0（但绝不冒充 PASS）；
- **`--strict` 严格模式**：任一阶段失败即 `FAIL`、退出码 1。CI 或无人值守时建议加。

已有文件的安全语义：项目里已存在的 `AGENTS.md`、`PROJECT_CONTEXT.md`、
`SESSION_STATE.md` **一律不覆盖**（脚本会打印「保持现状」）；全局规则与技能
在 `--update` 时先备份（`*.bak-<时间戳>`）再替换。

---

## 3. 执行部署

### 3.1 方式一：一键流水线（推荐）

```bash
# 1) 把模板仓克隆到与目标项目平级的位置（不要克隆进目标项目里）
git clone https://github.com/xusofty-cyber/agent-harness.git
cd agent-harness

# 2) 无人值守全量执行：目标 = shopapi，模板语言 = 简体中文
./run-pipeline.sh --all -y -p ~/projects/shopapi -l zh
```

参数速记：

| 参数 | 作用 |
|---|---|
| `--all` | 四个阶段全跑 |
| `-y` | 非交互（无人值守），不弹确认 |
| `-p <路径>` | 目标项目根目录（默认当前目录，**务必显式写**） |
| `-l zh` | 模板语言：`zh` 简体 / `zh-tw` 繁体 / `en` 英文（默认 en，不写就是英文模板） |
| `-g` | 同时部署/更新本机全局规则（`~/.claude`、`~/.gemini`、`~/.codex`、`~/.dsh` 等） |
| `-u` | 覆盖更新全局规则与外部技能（替换前自动备份） |
| `--strict` | 严格模式，任一阶段失败即整体失败 |
| `-k` | 只读检查模式（技能只比差异、文档只分析，不落盘修改） |
| `--stages deploy,docs` | 只跑指定阶段（逗号分隔：deploy / memory / skills / docs） |

不想记参数也可以直接 `./run-pipeline.sh`（无参数）进入交互向导：
6 步依次选语言、是否更新全局规则、技能同步方式、项目路径、阶段组合、执行细度，
用方向键与空格操作。

### 3.2 方式二：只部署规则与门禁（轻量）

如果暂时不要记忆与文档阶段，直接用部署脚本本体：

```bash
cd agent-harness
./deploy-agents.sh ~/projects/shopapi --lang zh
```

它完成阶段 1 的全部内容（规则、桥接、钩子、技能、门禁代码、pre-push/CI 模板）。

### 3.3 Windows

```powershell
git clone https://github.com/xusofty-cyber/agent-harness.git
cd agent-harness
.\run-pipeline.ps1 -All -Yes -ProjectPath "D:\Projects\shopapi" -Language zh
# 或仅部署：.\deploy-agents.ps1 -ProjectPath "D:\Projects\shopapi" -Language zh
```

后文所有 Linux 命令在 Windows 下把 `.sh` 换成对应 `.ps1`、参数风格换成
`-PascalCase` 即可，功能一一对应。

### 3.4 跑完后目标项目的变化（以 shopapi 为例）

```text
shopapi/
├── AGENTS.md                  ← 新增：项目级规则（模板，待填，见 §4）
├── PROJECT_CONTEXT.md         ← 新增：项目长期事实（模板，待填，见 §4）
├── SESSION_STATE.md           ← 新增：会话断点（模板，待填，见 §4）
├── .gitignore                 ← 追加了 Harness 运行时忽略段（已有文件不重写）
├── .agents/
│   ├── rules/                 ← 按需加载的子规则（工程、Git、安全、token 纪律等）
│   └── skills/                ← 技能目录（默认 minimal 档 15 个，见 §8.1）
├── .claude/                   ← Claude Code 桥接与 PreToolUse/Stop 等钩子
├── .agents/hooks.json 等      ← Antigravity 系桥接（各宿主一份，视部署选择）
├── gate/
│   ├── pass-gate.py           ← 门禁本体（注意：只有代码，还没有条目数据，见 §5）
│   ├── feature_list.schema.json
│   ├── comet_adapter.py
│   └── init.template.sh       ← 门禁初始化脚本
├── （pre-push 门禁）           ← 部署默认安装：推送前重跑全部 passing 条目验收
│                                 （可被 --no-verify 绕过，所以还要配 CI + 分支保护）
└── （CI 门禁模板）             ← 与 pre-push 同逻辑、跑在服务端的一份检查模板
```

**这一步结束只算部署完成一半。** 下面三节是另一半。

### 3.5 部署前先分级：规模决定档位（不要一律满配）

全套 harness 的仪式（多宿主桥接、门禁条目、文档分析）对小项目是净负担：
一个只有十来个源文件、单人维护的工具型项目，管理文件能堆得比源码还多，
每个小任务先交一遍流程税。部署前先按「规模 × 出错代价」定档，档位写进
项目 `AGENTS.md` 的「规模分级与任务分级」一节（模板已内置该节）：

| 档位 | 判据（粗） | 部署形态 |
|---|---|---|
| Lite | 源文件约 < 50、单人维护、不跨周开发 | 只部署精简版项目 AGENTS（`--profile minimal` 的 slim 模板取向）＋保留项目自有测试；不启用门禁条目流程、check-clean、doc-impact；桥接只留实际在用的宿主一个 |
| 标准 | 中型及以上、多人或跨周、或错一次代价大 | 本指南的完整流程 |

定错档的代价不对称：小项目上标准档是天天的慢，大项目上 Lite 是出事时的贵。
拿不准先 Lite，遇到第一次「改错了没被拦住」的事故再升档——升档只是补部署，不丢数据。

### 3.6 升档操作单：项目长大后从 Lite 切到标准档

升档不是「把欠的流程补交一遍」，而是从某一天起换一套活法。先看信号，
再走四步，全程不回溯历史。

**触发信号（任意两条即升档）**：

- 代码多到「通读一遍」不再现实，明显越过 Lite 的体量判据；
- 第二位协作者或第二个宿主加入；
- 开发开始跨周，「上次做到哪」要靠猜；
- 出现第一次「改 A 处坏 B 处、现有测试没拦住」；
- 长出对外接口、数据格式这类错一次很贵的面。

**四步操作**：

1. **改标注**：项目 `AGENTS.md` 分级节里把档位从 Lite 改为标准，依据一句话更新。
2. **补部署**：重跑第 3 节的流水线即可——部署只补缺失、从不覆盖已有文件；
   slim 版 AGENTS 里已填好的项目事实，手工搬进全版模板的对应节；
   桥接仍只补实际在用的宿主，不要一升档就全宿主撒网。
3. **门禁冷启动**：按 §6 跑 `gate/init` 建功能清单；第一条先立**基线条目**
   （验收命令＝项目现有的全量测试），verify 跑绿，证明升档这一刻起点是绿的。
   存量功能**不回溯补条目**——谁动到哪个模块，顺手给它补条目（增量认领），
   台账随增量自然长满。
4. **纪律三步开**：先状态层（SESSION_STATE 转正、收工跑 check-clean）→
   再门禁条目流（新功能一律立项、老功能随触随补）→ 最后 doc-impact 与 CI
   收紧；每步隔一两个迭代再开下一步，别在同一天全开。

**切线原则**：升档日之前的提交不补条目、不补文档，git 历史本身就是那段
时期的记录；从升档日起按标准档记账。降档完全对称：项目冻结或缩小时，
反向删掉管理文件即可，没有任何锁定——这正是可以放心先 Lite 的原因。

---

## 4. 基本配置一：填实三份根文档

三份文档分工不同，不要混写：

| 文档 | 写什么 | 什么时候改 |
|---|---|---|
| `AGENTS.md` | 给 agent 的项目级指令：命令、技术栈、架构红线、完成定义 | 命令或红线变化时 |
| `PROJECT_CONTEXT.md` | 项目长期事实（SSOT）：领域、架构、模块职责、关键约束 | 架构/选型发生实质变化时 |
| `SESSION_STATE.md` | 当前会话断点：一页以内，只有目标/进行中/下一步/阻塞/最近验证 | 每次会话收尾时刷新 |

### 4.1 先让脚本扫一遍，再人工确认

```bash
cd agent-harness
# 自动扫描 git 元数据、依赖清单、CI 文件，生成带项目事实的 AGENTS.md 草稿，
# 无法推断的字段会列成待确认清单
./deploy-agents.sh ~/projects/shopapi --initialize --lang zh
# 检查还有哪些占位符没填完（有未填项会逐个列出）
./deploy-agents.sh ~/projects/shopapi --check
```

注意：`--initialize` 扫到的框架/脚本信息只是**建议**，不是已核实事实；
项目定位、模块职责、边界这类推断不出来的，必须由您或当班 agent 确认后填。

### 4.2 AGENTS.md 必填项与示例

必填占位符：项目名、业务定位、维护者、仓库与默认分支、五组命令
（安装 / 开发 / 构建 / 测试 / lint 与格式化）、技术栈表、架构红线。

shopapi 填好后的节选（命令段）：

```bash
# 1. 依赖管理
pip install -r requirements.txt        # Python 3.12 venv 内执行

# 2. 本地开发与构建
uvicorn app.main:app --reload          # 开发服务器
python -m compileall app               # 无独立构建步骤，以编译检查代之

# 3. 测试（改动后必须运行，输出须精简）
python -m pytest -q                    # 全量单测
python -m pytest tests/test_orders.py -q   # 针对单文件

# 4. 代码质量
ruff check . && ruff format --check .
```

技术栈表节选：

| 类别 | 选型 | 说明 |
|---|---|---|
| 语言 & 运行时 | Python 3.12 | 类型注解必填 |
| 核心框架 | FastAPI 0.11x | 路由层只做参数校验与编排 |
| 持久层 | PostgreSQL 16 + Redis 7 | 订单状态机只存 PG，Redis 仅作缓存 |

架构红线按本项目实际写，不要照抄模板的通用五条就完事——
红线应该是「这个项目特有的、违反了会出事的」约束，例如 shopapi 的：
*订单金额一律整数分存储，禁止浮点；库存扣减必须走订单服务的 CAS 更新*。

其他语言的命令段对照（填表时替换即可）：

| 用途 | JS / Node 示例 | C++ / CMake 示例 |
|---|---|---|
| 安装 | `pnpm install --frozen-lockfile` | `cmake -B build -DCMAKE_BUILD_TYPE=Release` |
| 构建 | `pnpm build` | `cmake --build build -j4` |
| 全量测试 | `pnpm test -- --reporter=dot` | `ctest --test-dir build --output-on-failure` |
| 单文件测试 | `pnpm test -- src/orders.test.ts` | `ctest --test-dir build -R order_test` |
| lint | `pnpm lint && pnpm typecheck` | `clang-tidy -p build src/*.cpp` |

### 4.3 PROJECT_CONTEXT.md 必填项

领域一句话、核心模块矩阵（每个模块：职责 + 工作流）、仓库与分支、
运行时与部署形态、技术栈表、目录职责、关键约束。
原则：只写**长期事实**，不写「本周在做什么」——那是 SESSION_STATE 的事。

### 4.4 SESSION_STATE.md 的规矩

固定六节：目标 / 进行中 / 下一步 / 阻塞 / 最近一次验证（外加页眉的日期与项目名）。
硬规矩：**最多一页**；状态以 `gate/feature_list.json` 为准，本文件与之冲突时以清单为准；
已完成的历史移去 CHANGELOG，不要在这里堆流水账。首次部署时按当前真实状态填一遍即可。

### 4.5 目录级 AGENTS.md：从不自动部署，只能逐个点名（可选）

三级规则里的第三级——某个子目录自己的 `AGENTS.md`——**不会被
任何一条自动路径生成**，这是有意的设计，不是遗漏：

- `run-pipeline.sh` 没有目录参数，走流水线永远不会生成它；
- `deploy-agents.sh` 常规部署（不带 `--initialize`）也不会；
- 唯一生成路径是显式点名，一次一个目录：

```bash
cd agent-harness
./deploy-agents.sh ~/projects/shopapi --initialize --lang zh --directory app/orders
# Windows：.\deploy-agents.ps1 -ProjectPath "D:\Projects\shopapi" -Initialize -DirectoryPath "app/orders"
```

规则与边界：

| 事项 | 口径 |
|---|---|
| 路径 | 必须是相对路径、目录**已经存在**、且位于项目内（绝对路径或跳出项目的路径会被拒绝） |
| 搭配 | `--directory` 必须与 `--initialize` 或 `--check` 同用，单写会直接报错；配 `--check` 时只查该目录的占位符、不生成 |
| 已有文件 | 该目录已有 `AGENTS.md` 时，新稿写成同目录的 `AGENTS.generated.md` 供对照合并，不覆盖 |
| 内容来源 | 与项目级同一套 `init_guidance` 扫描（该目录的清单/脚本会被读作本地命令建议），边界部分仍须人工确认 |

为什么不自动：目录级文件写的是单个模块的**微边界**——管辖范围
（In Scope / Out of Scope）、对其他模块的依赖边界、该目录的本地
快速测试命令、大文件注意事项。脚本既不知道哪些子目录值得单独立
规矩，也扫不出这些边界；对每个子目录自动撒一份带占位符的文件，
只会让 agent 被空指令误导。所以它被做成维护者逐个点名、逐个填
实的 opt-in。

什么时候值得立一份：monorepo 的独立包、技术栈或红线与项目主体
明显不同的模块、高风险目录（如支付、迁移脚本）。填写要点：只写
**相对项目级的增量**（本目录特有的范围、边界与命令），通用规则
引用项目级 `AGENTS.md` 即可，不要整段复制——复制出来的副本会在
项目级修订时悄悄过期。

---

## 5. 基本配置二：初始化门禁（最容易漏的一步）

部署脚本只把门禁**代码**拷进 `gate/`，条目数据文件 `feature_list.json`
不会自动生成——必须显式初始化。在**目标项目根目录**执行：

```bash
cd ~/projects/shopapi
sh gate/init.template.sh \
  --name shopapi \
  --verify "python -m pytest -q" \
  --start "uvicorn app.main:app --reload" \
  --build "python -m compileall app"
```

三个参数的含义与填法：

| 参数 | 含义 | 填法要点 |
|---|---|---|
| `--name` | 项目名 | 与 AGENTS.md 一致 |
| `--verify` | **能证明项目可用的命令**（必填） | 退出码 0 = 项目是好的；通常是全量测试 |
| `--start` | 标准启动命令（必填） | 日常开发怎么把项目跑起来 |
| `--build` | 构建命令（可选） | 没有构建步骤的项目可省略，该维度在 check-clean 里记 SKIP |

注意：任一参数留空或还带着 `<...>` 占位符，初始化会**直接失败**而不是
生成一个坏脚手架——这是有意的防呆。初始化会顺带把 `--verify` 跑一遍冒烟，
项目此刻若是红的，先修项目再初始化。

产物：

```text
gate/feature_list.json    ← 条目清单（此刻只有项目骨架，条目待 §6 录入）
gate/clean-state.json     ← 内容即上面三条命令，例如：
                            {"build": "python -m compileall app",
                             "test":  "python -m pytest -q",
                             "start": "uvicorn app.main:app --reload"}
SESSION_STATE.md          ← 若部署阶段没生成，这里会补一份断点格式
DECISIONS.md              ← 若不存在，补一份决策记录骨架
```

JS / C++ 项目的初始化对照：

```bash
# JS / Node
sh gate/init.template.sh --name webapp \
  --verify "pnpm test" --start "pnpm dev" --build "pnpm build"

# C++ / CMake
sh gate/init.template.sh --name engine \
  --verify "ctest --test-dir build --output-on-failure" \
  --start "./build/engine --demo" \
  --build "cmake --build build -j4"
```

---

## 6. 基本配置三：录入条目并走完一轮门禁

门禁的日常语言只有四个动作：**add（录入）→ start（开始）→ verify（验收）→ check-clean（交接检查）**。
铁规矩：同时只能有 1 个条目在进行中（WIP=1）；条目变 `passing` 的唯一合法
路径是 verify 真跑其验收命令并退出 0、证据自动落盘——**任何人（包括 agent）
不得直接编辑 `feature_list.json`**，钩子会当场拦截直写。

### 6.1 录入示例（shopapi 的第一批三个条目）

```bash
cd ~/projects/shopapi

python3 gate/pass-gate.py add \
  --id order-create-api \
  --title "订单创建接口" \
  --behavior "POST /orders 能创建订单并返回订单号；金额按整数分入库" \
  --command "python -m pytest tests/test_orders.py -q" \
  --level integration --priority p0

python3 gate/pass-gate.py add \
  --id order-stock-cas \
  --title "库存扣减 CAS" \
  --behavior "并发下单不超卖：扣减走带版本校验的原子更新" \
  --command "python -m pytest tests/test_stock_cas.py -q" \
  --level integration --priority p0 \
  --depends-on order-create-api \
  --out-of-scope "不做预留库存与超时释放（下一期）"

python3 gate/pass-gate.py add \
  --id readme-quickstart \
  --title "README 快速开始" \
  --behavior "新克隆按 README 三步能把服务跑起来" \
  --command "python -m pytest tests/test_smoke.py -q" \
  --level assert --priority p2
```

字段说明：

| 字段 | 说明 |
|---|---|
| `--id` | 条目唯一短名（kebab-case），后续所有命令都用它 |
| `--behavior` | 完成时用户可见的行为——写「做完是什么样」，不写实现细节 |
| `--command` | **该条目自己的验收命令**，退出 0 才算过；要具体到文件，不要写「跑全部测试」糊弄 |
| `--level` | 验证层级：`assert` < `unit` < `integration` < `e2e`；跨组件的 p0 条目至少 integration |
| `--depends-on` | 依赖的条目 id（可重复）；未满足时 start 默认硬拦，确需越过用 `start --override-deps "理由"`，理由会写入哈希链事件留痕 |
| `--out-of-scope` | 明确本条目不做什么，防止范围蔓延 |

### 6.2 走完一轮

```bash
python3 gate/pass-gate.py start --id order-create-api   # 进入进行中（WIP=1）
# ……正常开发、写代码、跑测试……
python3 gate/pass-gate.py verify --id order-create-api  # 门禁重跑验收命令
# 退出 0 → 条目变 passing，证据（含命令输出摘要的哈希）自动记录
python3 gate/pass-gate.py status                        # 看全部条目与状态
python3 gate/pass-gate.py check-clean                   # 五维交接检查（构建/测试/启动等）
```

verify 失败时条目留在进行中，连败 5 次触发熔断要求先复盘——不要用
`override` 绕过成常态：`override` 是给人类的留痕通道（必须写理由、计入
事件日志、且 CI 不认它是真 passing），日常滥用等于拆掉门禁。

### 6.3 每次会话的固定动作

- **开工**：先读 `SESSION_STATE.md`，再 `python3 gate/pass-gate.py status` 对齐状态；
- **收工**：刷新 `SESSION_STATE.md`（一页内）、未完成事项留在条目或计划里、
  最后跑一遍 `check-clean` 全绿再结束。

### 6.4 轻通道：小任务的快速路径（任务分级）

项目定档之后，每个任务开工前还要判一次级（模板「规模分级与任务分级」节有
出厂文本，项目可按自己的风险口径改）：

- **S 级 · 轻通道**：单文件、样式/文案/参数类小改——不立条目、不跑全量验证，
  只读相关文件（先定位后精读，禁止无目标通读全仓），改后跑该文件的定向测试，
  会话内直接汇报。布局微调、改个默认参数、修个错别字都属此类。
- **M 级 · 常规通道**：多文件、边界清晰——立一个条目（同类小改合并），
  验收命令写定向测试集，check-clean 只在收工时跑。
- **L 级 · 全通道**：状态机、对外接口、数据迁移、安全边界，或错一次代价大——
  全流程一个不省。

没有轻通道的 harness 会在小任务上系统性地慢：开工通读十几个文件、为改一行
参数立项验收，时间全花在仪式上。判级口诀：影响面一眼可见、错了立刻能发现
→ S；其余先 M；碰高代价面 → L。有疑问就高不就低，S 级中途发现影响面超
预期，立即升 M 补立条目。

---

## 7. 宿主面配置（按您实际用的工具看）

部署后各宿主的强制力不同，先认清再决定要不要额外动作：

| 宿主 | 部署后状态 | 还要做什么 |
|---|---|---|
| Claude Code | 桥接 + 钩子就位，客户端内强制（拦直写 feature_list、Stop 时拦未完成条目） | 无，开新会话即生效 |
| Antigravity CLI / IDE / 桌面版 | 项目钩子已部署，四类事件已实测可用 | 无；注意桌面版走全局注册，钩子改动后要重启桌面版 |
| Codex | 全局/项目 AGENTS.md 配置型接入 | 无强制钩子，靠门禁命令 + CI |
| DeepSeek Harness（dsh） | 门禁插件已随部署落入 `.dsh/` | **需手动激活**（挂载 Cordis 插件行），激活后 Stop 转向才生效 |
| WorkBuddy | 规则桥接已部署（协议级） | 暂未完成活验，先当配置型接入用，不依赖其钩子强制 |
| 其他宿主 | 只有文件 | 手动跑 `verify` / `check-clean`，靠 pre-push + CI 兜底 |

全局规则（可选）： `./run-pipeline.sh --all -y -g -p <项目>` 或在向导里选，
会把 Global AGENTS 写入各工具的全局位置；加 `-u` 时先备份再覆盖。
只对单项目部署时不要加 `-g`，免得动到其他项目的环境。

---

## 8. 可选配置

### 8.1 技能档位（profile）

部署默认 `minimal`。档位决定拷多少技能与是否带编排层：

| 档位 | 技能数 | 编排层（graph/loop） | 适合 |
|---|---|---|---|
| `minimal`（默认） | 15（门禁核心 10 + openspec 核心 5） | 不带 | 只想要门禁 + 基础规则的新项目 |
| `standard` | 20 | 带 | 要用目标循环/图编排 |
| `full` | 37（加 `--include-heavy-skills` 为全部 39） | 带 | 技能全家桶 |

切换方式：重新部署时在 `deploy-agents.sh` 上加 `--profile standard` 等参数。
从大档降回 minimal 时，被移除的编排文件会先备份，不会直接删除。

### 8.2 ai-memory 跨工具记忆（可选）

流水线阶段 2 显示 SKIP 是因为它需要显式开启，三步：

```bash
cargo install ai-memory                      # 或到其 GitHub Releases 下二进制
cp .ai-memory.toml.example .ai-memory.toml   # 在 agent-harness 仓内取模板
# 编辑 .ai-memory.toml：把 replace-with-* 占位符换成您的 workspace / 项目名，
# 并把该文件放进目标项目根目录（它已被 .gitignore 忽略，不会误提交）
./setup-ai-memory.sh claude-code codex antigravity-ide   # 在目标项目内运行
```

不开启完全不影响门禁与规则工作，只是没有跨工具的长期记忆召回。

### 8.3 CodeGraph / RTK 提示

部署尾声脚本会检测这两个可选 CLI 并**逐个询问**是否安装与接入（默认否）；
无人值守（`-y`）时自动跳过并打印后续命令，需要时按提示手动跑即可，不必重部署。

---

## 9. 部署验收清单

在目标项目根目录逐条跑，全过才算部署落地：

```bash
cd agent-harness && ./deploy-agents.sh ~/projects/shopapi --check
# → 无未填占位符报告

cd ~/projects/shopapi
python3 gate/pass-gate.py status        # 无校验错误，条目列表符合预期
python3 gate/pass-gate.py check-clean   # 五维全过（未配 build 时该维 SKIP 可接受）
python3 gate/pass-gate.py events --verify-chain   # 事件哈希链完整
git status                              # 新增文件集合与 §3.4 对照，无意外改动
```

再做一次真机式自检：开一个新 agent 会话，让它只读项目文件回答
「这个项目是做什么的、怎么测、当前进行中条目是什么」——答得对，
说明三文档填得够实；答错或答不出，先补文档，不要先怪模型。

---

## 10. 更新与回滚

```bash
cd agent-harness
./deploy-agents.sh ~/projects/shopapi --update   # 快进模板仓并同步托管文件
```

- `--update` 替换被托管的规则/技能前会先备份；您在目标项目里手改过的
  三份根文档不在托管替换范围内，但更新后仍建议跑一遍 `--check` 与 `check-clean`。
- 想回滚某个全局规则文件：找同目录下的 `*.bak-<时间戳>` 覆盖回去即可。
- 项目侧想整体退出 Harness：删除 `.agents/`、`.claude/`、`gate/` 与根目录
  三文档即可，无服务端状态、无锁定。

---

## 11. 常见问题

| 现象 | 原因与处置 |
|---|---|
| 阶段 2 显示 SKIP | 未装 ai-memory CLI 或 `.ai-memory.toml` 还有占位符。不用记忆功能可无视；要开见 §8.2 |
| 阶段 3/4 显示 WARN | 默认 advisory 模式下「发现问题但不拦停」：技能有差异或有文档过期。看汇总表详情逐项处理，或加 `--strict` 让它硬失败以便定位 |
| `init.template.sh` 报占位符错误 | `--verify` / `--start` 里还带着 `<...>` 或没填。填真实命令后重跑 |
| 初始化时 verify 冒烟失败 | 项目当前本身是红的。先把项目修绿，再初始化——门禁不接受「带病上岗」 |
| 已有 AGENTS.md 没被更新 | 设计如此：已存在文件不覆盖。新版模板会写成 `AGENTS.generated.md` 供对照，手动合并 |
| agent 说改不了 feature_list.json | 正确行为：该文件只能由 pass-gate 写。让它用 `add / start / verify` 命令，不要教它绕过钩子 |
| start 被依赖拦住 | 依赖条目还没 passing。要么先做依赖，要么 `start --override-deps "理由"` 留痕越过 |
| verify 一直失败想先收工 | 用 `block` 标记阻塞并在 SESSION_STATE 写清原因，不要 override 成 passing |
| 桌面版钩子不生效 | 桌面版读全局注册，与 CLI 的项目级配置不同面；确认全局 hooks 已注册且桌面版已重启 |
| Windows 下脚本行为不一致 | 用 `.ps1` 版且 PowerShell ≥ 5.1；两版功能对齐，若发现差异以仓内 `tests/repo_checks.py` 的 PARITY 表为准 |

---

## 附录：命令速查

```bash
# 部署
./run-pipeline.sh --all -y -p <项目> -l zh        # 一键全量（模板仓内执行）
./run-pipeline.sh                                  # 交互向导
./deploy-agents.sh <项目> --initialize --lang zh   # 扫描项目事实生成草稿
./deploy-agents.sh <项目> --check                  # 查未填占位符
./deploy-agents.sh <项目> --initialize --directory <子目录>   # 为一个子目录生成目录级 AGENTS.md（逐个点名）
./deploy-agents.sh <项目> --update                 # 更新托管文件（自动备份）

# 门禁（目标项目内执行）
sh gate/init.template.sh --name <名> --verify "<命令>" --start "<命令>" [--build "<命令>"]
python3 gate/pass-gate.py add --id <id> --title "" --behavior "" --command ""
python3 gate/pass-gate.py start --id <id>
python3 gate/pass-gate.py verify --id <id>
python3 gate/pass-gate.py status
python3 gate/pass-gate.py check-clean
python3 gate/pass-gate.py events --verify-chain
```

*本文档随 agent-harness v0.7.0 编制；脚本参数如后续版本有变，以
`./run-pipeline.sh --help` 与《多工具部署与配置指南》为准。*
