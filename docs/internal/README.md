# docs/internal — 仓库自身的开发运维记录

本目录存放 **agent-harness 仓库自身的**开发过程记录（双轨状态记忆的 dogfood 实例），
**不是**随模板分发的内容，`deploy-agents.*` 也不会拷贝它们。

- `PROJECT_CONTEXT.md` —— 本仓库的项目全景与演进编年史
- `SESSION_STATE.md` —— 本仓库的开发断点与下一步计划
- `SESSION_RESUME.md` —— 会话恢复备忘

模板中提到的 `PROJECT_CONTEXT.md` / `SESSION_STATE.md` 双轨记忆模式，
指的是**使用本模板的下游项目**应在自己项目根目录维护的两个文件，
与本目录这三个文件是"模式"与"实例"的关系，不要混淆。

- `superpowers/` —— 已合入功能的设计文档归档（`plans/` 实现计划、`specs/` 设计规格）。注意：各 skill 中提到的 `docs/superpowers/plans/` 是**未来新计划的存放约定**，不受此次归档影响。

## 现行制度 vs 历史轨迹（v0.4.1 索引）

新会话先读「现行」组；「历史」组是审计轨迹，只在追溯某条决策的
来历时才需要打开，不要把其中的阶段性结论当作现行规则。

**现行（living）**：

- `host-verification-matrix.md` —— 各宿主门禁的验证档位（唯一口径）
- `i18n-status.md` —— 繁中翻译状态台账
- `skill-tiers.md` —— 技能分档的理由记录
- `gate-operator-checklist.md` —— 无钩子宿主上手动跑门禁的清单
- `release-checklist.md` —— 发版清单
- `ai-memory-routing.md` —— 跨会话记忆路由
- `token-adapters.md` —— 为什么成本只能用代理指标
- `users-and-change-cost.md` —— 变更成本口径

**历史（historical，保留原文不改）**：

- `phase1-dogfood.md`、`phase2-verification.md`、`phase4-verification.md`、
  `phase5-graph.md`、`phase5-loops.md`、`phase5/`、`phase6-verification.md`
- `merge-verification.md`、`merge-rulings-and-fixes-2026-10-29.md`、
  `merge-review-optimization-2026-10-29.md`、`panel-fixes-2026-10-29.md`
- `dogfood-2026-10-29.md`、`release-v0.3.0.md`、`proposals/`、
  `SESSION_RESUME*.md`、`brainstorming-server-safety.md`
