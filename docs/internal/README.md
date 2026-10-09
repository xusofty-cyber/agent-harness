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
