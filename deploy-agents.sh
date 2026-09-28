#!/usr/bin/env bash
# ==============================================================================
# deploy-agents.sh
# Platforms: Linux / macOS (Bash)
# Purpose: One-click deploy & online update AI Agents Harness spec, rules & skills
#          (Supports Codex / Claude Code / Antigravity IDE)
# ==============================================================================

set -euo pipefail

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print usage
usage() {
    echo -e "${CYAN}用法 (Usage):${NC}"
    echo "  $0 <项目根目录路径> [--global|-g] [--update|-u] [--comet-init]"
    echo "  $0 --global|-g [--update|-u]   # 仅部署/更新全局配置"
    echo ""
    echo -e "${CYAN}参数说明 (Parameters):${NC}"
    echo "  <项目根目录路径>   目标项目所在的相对路径或绝对路径。"
    echo "  --global, -g       同时部署/更新当前用户的全局规则 (~/.claude/ 与 ~/.gemini/)。"
    echo "  --update, -u       执行在线检测与更新（拉取最新规则、更新技能库与配套脚手架）。"
    echo "  --comet-init       若系统中已安装 comet CLI，自动在目标项目中运行 comet init。"
    echo ""
    echo -e "${CYAN}示例 (Examples):${NC}"
    echo "  $0 /path/to/my-project"
    echo "  $0 /path/to/my-project --global --update"
    echo "  $0 /path/to/my-project --comet-init"
    echo "  $0 --global --update"
    exit 1
}

# Parse arguments
TARGET_PROJECT_ARG=""
DEPLOY_GLOBAL=false
DO_UPDATE=false
DO_COMET_INIT=false

for arg in "$@"; do
    case "$arg" in
        --global|-g)
            DEPLOY_GLOBAL=true
            ;;
        --update|-u)
            DO_UPDATE=true
            ;;
        --comet-init)
            DO_COMET_INIT=true
            ;;
        --help|-h)
            usage
            ;;
        *)
            if [ -z "$TARGET_PROJECT_ARG" ]; then
                TARGET_PROJECT_ARG="$arg"
            fi
            ;;
    esac
done

if [ -z "$TARGET_PROJECT_ARG" ] && [ "$DEPLOY_GLOBAL" = false ]; then
    echo -e "${RED}[错误] 请指定目标项目路径，或者使用 --global 仅更新全局配置。${NC}\n"
    usage
fi

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GLOBAL_TEMPLATE="${SCRIPT_DIR}/全局 AGENTS.md"
PROJECT_TEMPLATE="${SCRIPT_DIR}/项目级 AGENTS.md"
SOURCE_RULES_DIR="${SCRIPT_DIR}/.agents/rules"
SOURCE_SKILLS_DIR="${SCRIPT_DIR}/.agents/skills"
SOURCE_SKILLS_LOCK="${SCRIPT_DIR}/skills-lock.json"
SOURCE_CLAUDE_SETTINGS="${SCRIPT_DIR}/.claude/settings.json"

# ==============================================================================
# 1. Online Update Phase (--update)
# ==============================================================================
if [ "$DO_UPDATE" = true ]; then
    echo -e "${CYAN}==================================================${NC}"
    echo -e "${CYAN} 正在执行在线检测与更新...${NC}"
    echo -e "${CYAN}==================================================${NC}"

    # A. Check Git upstream
    if git -C "${SCRIPT_DIR}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        echo -e "${YELLOW}>>> 从 Git 远程上游拉取最新规则与技能模板...${NC}"
        if git -C "${SCRIPT_DIR}" pull --rebase; then
            echo -e "  ${GREEN}[√] 本地模板已与远程上游同步。${NC}"
        else
            echo -e "  ${YELLOW}[!] Git pull 出现告警，将继续使用当前模板。${NC}"
        fi
    else
        echo -e "  ${NC}[i] 当前模板目录非 Git 仓库，跳过 git pull。${NC}"
    fi

    # B. Check Harness CLI updates
    echo -e "\n${YELLOW}>>> 检查 Harness 生态工具更新...${NC}"
    if command -v comet >/dev/null 2>&1; then
        echo -e "  ${NC}[i] 发现 Comet CLI，执行 comet update...${NC}"
        comet update || true
    elif command -v npm >/dev/null 2>&1; then
        echo -e "  ${NC}[i] Comet CLI 未安装。如需安装: npm install -g @rpamis/comet${NC}"
    fi

    # C. Update Skills via npx skills
    if command -v npx >/dev/null 2>&1; then
        echo -e "\n${YELLOW}>>> 从网络上游通过 'npx skills@latest update' 更新全套技能库...${NC}"
        npx -y skills@latest update -y || echo -e "  ${YELLOW}[!] npx skills update 出现告警，继续使用本地技能。${NC}"
    fi
fi

# ==============================================================================
# 2. Deploy / Update Global Rules (--global)
# ==============================================================================
if [ "$DEPLOY_GLOBAL" = true ]; then
    echo -e "\n${YELLOW}>>> [1/3] 正在部署/更新用户全局规则...${NC}"

    if [ ! -f "${GLOBAL_TEMPLATE}" ]; then
        echo -e "${YELLOW}[警告] 未找到全局模板 ${GLOBAL_TEMPLATE}，跳过全局部署。${NC}"
    else
        # A. Claude Code (~/.claude/CLAUDE.md)
        mkdir -p "${HOME}/.claude"
        cp -f "${GLOBAL_TEMPLATE}" "${HOME}/.claude/CLAUDE.md"
        echo -e "  ${GREEN}[√] Claude Code 全局规则已部署: ${HOME}/.claude/CLAUDE.md${NC}"

        # B. Antigravity IDE (~/.gemini/config/rules/global_agents.md)
        mkdir -p "${HOME}/.gemini/config/rules"
        cp -f "${GLOBAL_TEMPLATE}" "${HOME}/.gemini/config/rules/global_agents.md"
        echo -e "  ${GREEN}[√] Antigravity IDE 全局规则已部署: ${HOME}/.gemini/config/rules/global_agents.md${NC}"
    fi
fi

# If no target project specified, finish
if [ -z "$TARGET_PROJECT_ARG" ]; then
    echo -e "\n${GREEN}[√] 全局规则配置完成！${NC}"
    exit 0
fi

# Validate target project directory
if [ ! -d "${TARGET_PROJECT_ARG}" ]; then
    echo -e "${RED}[错误] 目标项目路径不存在或不是目录: ${TARGET_PROJECT_ARG}${NC}"
    exit 1
fi

TARGET_PROJECT_DIR="$(cd "${TARGET_PROJECT_ARG}" && pwd)"

echo -e "\n${CYAN}==================================================${NC}"
echo -e "${CYAN} 目标项目路径: ${TARGET_PROJECT_DIR}${NC}"
echo -e "${CYAN}==================================================${NC}"

# ==============================================================================
# 3. Deploy Project AGENTS.md & Bridges
# ==============================================================================
echo -e "\n${YELLOW}>>> [2/3] 正在部署项目级规则与跨工具桥接...${NC}"

TARGET_AGENTS="${TARGET_PROJECT_DIR}/AGENTS.md"
if [ ! -f "${TARGET_AGENTS}" ]; then
    cp "${PROJECT_TEMPLATE}" "${TARGET_AGENTS}"
    echo -e "  ${GREEN}[√] 已生成项目级 AGENTS.md（从模板初始化）${NC}"
else
    echo "  [i] 目标项目已存在 AGENTS.md，保持现状不破坏用户自定义配置。"
    if [ "$DO_UPDATE" = true ]; then
        cp -f "${PROJECT_TEMPLATE}" "${TARGET_PROJECT_DIR}/AGENTS.template.md"
        echo "  [i] 已生成最新的 AGENTS.template.md 供参照。"
    fi
fi

# Claude Code bridge (CLAUDE.md -> AGENTS.md)
TARGET_CLAUDE="${TARGET_PROJECT_DIR}/CLAUDE.md"
if [ ! -e "${TARGET_CLAUDE}" ]; then
    ln -sf "AGENTS.md" "${TARGET_CLAUDE}"
    echo -e "  ${GREEN}[√] 已建立软链接: CLAUDE.md -> AGENTS.md${NC}"
else
    echo "  [i] 目标项目已存在 CLAUDE.md，跳过。"
fi

# GitHub Copilot bridge (.github/copilot-instructions.md -> AGENTS.md)
TARGET_GITHUB_DIR="${TARGET_PROJECT_DIR}/.github"
TARGET_COPILOT="${TARGET_GITHUB_DIR}/copilot-instructions.md"
mkdir -p "${TARGET_GITHUB_DIR}"

if [ ! -e "${TARGET_COPILOT}" ]; then
    ln -sf "../AGENTS.md" "${TARGET_COPILOT}"
    echo -e "  ${GREEN}[√] 已建立软链接: .github/copilot-instructions.md -> AGENTS.md${NC}"
else
    echo "  [i] 目标项目已存在 copilot-instructions.md，跳过。"
fi

# Zed IDE bridge (ZED.md -> AGENTS.md)
TARGET_ZED="${TARGET_PROJECT_DIR}/ZED.md"
if [ ! -e "${TARGET_ZED}" ]; then
    ln -sf "AGENTS.md" "${TARGET_ZED}"
    echo -e "  ${GREEN}[√] 已建立软链接: ZED.md -> AGENTS.md${NC}"
else
    echo "  [i] 目标项目已存在 ZED.md，跳过。"
fi

# Claude Code PreToolUse Security Hooks (.claude/settings.json)
if [ -f "${SOURCE_CLAUDE_SETTINGS}" ]; then
    mkdir -p "${TARGET_PROJECT_DIR}/.claude"
    TARGET_CLAUDE_SETTINGS="${TARGET_PROJECT_DIR}/.claude/settings.json"
    if [ "$DO_UPDATE" = true ] || [ ! -f "${TARGET_CLAUDE_SETTINGS}" ]; then
        cp -f "${SOURCE_CLAUDE_SETTINGS}" "${TARGET_CLAUDE_SETTINGS}"
        echo -e "  ${GREEN}[√] 已部署 Claude Code 安全拦截钩子: .claude/settings.json${NC}"
    else
        echo "  [i] 目标项目已存在 .claude/settings.json，跳过。"
    fi
fi

# Sub-rules (.agents/rules/)
TARGET_RULES_DIR="${TARGET_PROJECT_DIR}/.agents/rules"
if [ -d "${SOURCE_RULES_DIR}" ]; then
    mkdir -p "${TARGET_RULES_DIR}"
    for rule in "${SOURCE_RULES_DIR}"/*.md; do
        if [ -f "$rule" ]; then
            rule_name=$(basename "$rule")
            if [ "$DO_UPDATE" = true ] || [ ! -f "${TARGET_RULES_DIR}/${rule_name}" ]; then
                cp -f "$rule" "${TARGET_RULES_DIR}/${rule_name}"
                echo -e "  ${GREEN}[√] 已同步子规则: .agents/rules/${rule_name}${NC}"
            fi
        fi
    done
fi

# ==============================================================================
# 4. Deploy Skills (.agents/skills/ & .claude/skills/)
# ==============================================================================
echo -e "\n${YELLOW}>>> [3/3] 正在部署技能库与工具链集成...${NC}"

TARGET_SKILLS_DIR="${TARGET_PROJECT_DIR}/.agents/skills"
TARGET_CLAUDE_SKILLS_DIR="${TARGET_PROJECT_DIR}/.claude/skills"

mkdir -p "${TARGET_SKILLS_DIR}"
mkdir -p "${TARGET_CLAUDE_SKILLS_DIR}"

if [ -d "${SOURCE_SKILLS_DIR}" ]; then
    for skill_path in "${SOURCE_SKILLS_DIR}"/*; do
        if [ -d "$skill_path" ]; then
            skill_name=$(basename "$skill_path")
            dest_skill="${TARGET_SKILLS_DIR}/${skill_name}"

            if [ "$DO_UPDATE" = true ] || [ ! -d "${dest_skill}" ]; then
                rm -rf "${dest_skill}"
                cp -r "${skill_path}" "${dest_skill}"
                echo -e "  ${GREEN}[√] 已部署技能: .agents/skills/${skill_name}${NC}"
            else
                echo "  [i] 技能 .agents/skills/${skill_name} 已存在。"
            fi

            # Claude Code symlink bridge
            dest_claude_link="${TARGET_CLAUDE_SKILLS_DIR}/${skill_name}"
            if [ ! -e "${dest_claude_link}" ]; then
                ln -sf "../../.agents/skills/${skill_name}" "${dest_claude_link}"
                echo -e "  ${GREEN}[√] 已建立 Claude 技能链接: .claude/skills/${skill_name}${NC}"
            fi
        fi
    done
fi

# Sync skills-lock.json
if [ -f "${SOURCE_SKILLS_LOCK}" ]; then
    if [ "$DO_UPDATE" = true ] || [ ! -f "${TARGET_PROJECT_DIR}/skills-lock.json" ]; then
        cp -f "${SOURCE_SKILLS_LOCK}" "${TARGET_PROJECT_DIR}/skills-lock.json"
        echo -e "  ${GREEN}[√] 已同步 skills-lock.json${NC}"
    fi
fi

# ==============================================================================
# 5. Initialize Tasks Tracking (lessons.md & todo.md)
# ==============================================================================
TARGET_TASKS_DIR="${TARGET_PROJECT_DIR}/tasks"
mkdir -p "${TARGET_TASKS_DIR}"

if [ ! -f "${TARGET_TASKS_DIR}/lessons.md" ]; then
    cat << 'EOF' > "${TARGET_TASKS_DIR}/lessons.md"
# Lessons Learned (项目错题本)

> 本文件记录人类纠偏与架构踩坑经验。Agent 在开始新会话或类似改动前优先阅读，**同一错误绝不犯第二次**。

## 历史经验记录
- [INIT] 项目初始化完成，已接入 Harness 渐进式披露规约与技能库。
EOF
    echo -e "  ${GREEN}[√] 已初始化 tasks/lessons.md${NC}"
fi

if [ ! -f "${TARGET_TASKS_DIR}/todo.md" ]; then
    cat << 'EOF' > "${TARGET_TASKS_DIR}/todo.md"
# Task Checklist

> 复杂任务（>= 3 步）在此维护打勾清单，实时更新进度。

- [x] 项目基础规则与 Harness 技能库部署就绪
EOF
    echo -e "  ${GREEN}[√] 已初始化 tasks/todo.md${NC}"
fi

# ==============================================================================
# 7. Initialize OpenSpec Scaffold (docs/openspec/changes)
# ==============================================================================
TARGET_OPENSPEC_DIR="${TARGET_PROJECT_DIR}/docs/openspec/changes"
if [ ! -d "${TARGET_OPENSPEC_DIR}" ]; then
    mkdir -p "${TARGET_OPENSPEC_DIR}"
    echo -e "  ${GREEN}[√] 已初始化 OpenSpec 骨架目录: docs/openspec/changes${NC}"
fi

# ==============================================================================
# 8. Optional Comet CLI Init (--comet-init)
# ==============================================================================
if [ "$DO_COMET_INIT" = true ]; then
    if command -v comet >/dev/null 2>&1; then
        echo -e "\n${YELLOW}>>> 正在目标项目中运行 'comet init'...${NC}"
        (cd "${TARGET_PROJECT_DIR}" && comet init) || echo -e "  ${YELLOW}[!] comet init 执行存在告警。${NC}"
    else
        echo -e "  ${YELLOW}[!] 指定了 --comet-init，但在系统 PATH 中未找到 comet CLI。${NC}"
        echo -e "      可通过以下命令安装: npm install -g @rpamis/comet"
    fi
fi

echo -e "\n${GREEN}==================================================${NC}"
echo -e "${GREEN} 部署完成！${NC}"
echo -e "${CYAN} 目标项目: ${TARGET_PROJECT_DIR}${NC}"
echo -e "${CYAN} 规则目录: ${TARGET_RULES_DIR}${NC}"
echo -e "${CYAN} 技能目录: ${TARGET_SKILLS_DIR}${NC}"
if command -v comet >/dev/null 2>&1; then
    echo -e "\n${YELLOW}[TIP] 检测到当前系统已安装 Comet CLI。若需启用终端原生状态机与 Hooks，可运行:${NC}"
    echo -e "      cd \"${TARGET_PROJECT_DIR}\" && comet init"
else
    echo -e "\n${NC}[i] 会话级三级规则与 30+ 原生技能已全部就绪。${NC}"
    echo -e "    若需使用终端原生 comet doctor / comet status 等 CLI 工具，可安装: npm install -g @rpamis/comet"
fi
echo -e "${GREEN}==================================================${NC}"
