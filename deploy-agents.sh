#!/usr/bin/env bash
# ==============================================================================
# deploy-agents.sh
# Platforms: Linux / macOS (Bash)
# Purpose: One-click deploy & online update AI Agents Harness spec, rules & skills
#          (Supports Codex / Claude Code / Antigravity 2.0 / CLI / IDE)
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
    echo "  $0 --global|-g [--update|-u]   # 初始化全局配置；--update 先备份再覆盖已有规则"
    echo ""
    echo -e "${CYAN}参数说明 (Parameters):${NC}"
    echo "  <项目根目录路径>   目标项目所在的相对路径或绝对路径。"
    echo "  --global, -g       初始化 Claude、Antigravity 2.0/CLI/IDE、Codex 用户全局规则。"
    echo "  --update, -u       更新模板仓库；与 --global 一起使用时，先备份再覆盖全局规则。"
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
GLOBAL_TEMPLATE="${SCRIPT_DIR}/Global AGENTS.md"
if [ ! -f "${GLOBAL_TEMPLATE}" ]; then
    GLOBAL_TEMPLATE="${SCRIPT_DIR}/全局 AGENTS.md"
fi

PROJECT_TEMPLATE="${SCRIPT_DIR}/Project AGENTS.md"
if [ ! -f "${PROJECT_TEMPLATE}" ]; then
    PROJECT_TEMPLATE="${SCRIPT_DIR}/项目级 AGENTS.md"
fi
SOURCE_RULES_DIR="${SCRIPT_DIR}/.agents/rules"
SOURCE_SKILLS_DIR="${SCRIPT_DIR}/.agents/skills"
SOURCE_SKILLS_LOCK="${SCRIPT_DIR}/skills-lock.json"
SOURCE_CLAUDE_SETTINGS="${SCRIPT_DIR}/.claude/settings.json"

# Back up managed target paths before an explicit update replaces them.
backup_path() {
    local path="$1"
    if [ -e "$path" ] || [ -L "$path" ]; then
        cp -a "$path" "${path}.bak.$(date +%Y%m%d%H%M%S)"
    fi
}

backup_global_rule() {
    local path="$1"
    local backup_path="${path}.bak.$(date +%Y%m%d%H%M%S)"
    local suffix=1
    while [ -e "$backup_path" ] || [ -L "$backup_path" ]; do
        backup_path="${path}.bak.$(date +%Y%m%d%H%M%S).${suffix}"
        suffix=$((suffix + 1))
    done
    cp -a "$path" "$backup_path"
    printf '%s' "$backup_path"
}

deploy_global_rule() {
    local tool_name="$1"
    local target_path="$2"
    local source_template="${3:-$GLOBAL_TEMPLATE}"
    local target_dir
    target_dir="$(dirname "$target_path")"
    mkdir -p "$target_dir"

    if [ -e "$target_path" ] || [ -L "$target_path" ]; then
        if [ -d "$target_path" ] && [ ! -L "$target_path" ]; then
            echo "  [!] ${tool_name} global rule target is a directory: ${target_path}" >&2
            return 1
        fi
        if [ "$DO_UPDATE" != true ]; then
            echo "  [i] 保留现有 ${tool_name} 全局规则: ${target_path}（使用 -u 备份并覆盖）"
            return
        fi

        local backup_file
        backup_file="$(backup_global_rule "$target_path")"
        if [ -L "$target_path" ]; then
            rm "$target_path"
        fi
        cp -f "$source_template" "$target_path"
        echo "  [√] 已更新 ${tool_name} 全局规则: ${target_path}（备份: ${backup_file}）"
        return
    fi

    cp "$source_template" "$target_path"
    echo "  [√] 已初始化 ${tool_name} 全局规则: ${target_path}"
}

prompt_yes_no() {
    local prompt="$1"
    local answer
    if [ ! -t 0 ]; then
        echo "  [i] 非交互终端，跳过：${prompt}"
        return 1
    fi
    read -r -p "${prompt} [y/N] " answer
    [[ "$answer" =~ ^[Yy]$ ]]
}

guide_optional_cli_tools() {
    local target="$1"
    local install_codegraph='curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh'
    local install_rtk='curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh'

    echo -e "\n${CYAN}>>> 可选 CLI 工具（Ponytail / Caveman 已作为 Skill 随项目部署）${NC}"

    if command -v codegraph >/dev/null 2>&1; then
        echo -e "  ${GREEN}[√] 已检测到 CodeGraph CLI: $(command -v codegraph)${NC}"
    else
        echo "  CodeGraph CLI 未安装。它会连接 Agent，并在项目中生成本地索引。"
        if prompt_yes_no "现在安装 CodeGraph CLI？安装后还会单独询问是否配置 Agent 与项目索引。"; then
            if ! command -v curl >/dev/null 2>&1; then
                echo "  [!] 缺少 curl。请按官方说明安装：${install_codegraph}"
                echo "  安装后：codegraph install；进入目标项目运行 codegraph init。"
            elif sh -c "$install_codegraph"; then
                echo -e "  ${GREEN}[√] CodeGraph CLI 安装器已执行。请重开终端，确认 codegraph 在 PATH 中。${NC}"
            else
                echo "  [!] CodeGraph 安装失败。官方命令：${install_codegraph}"
            fi
        else
            echo "  安装命令：${install_codegraph}"
            echo "  安装后：codegraph install；进入目标项目运行 codegraph init。"
        fi
    fi

    if command -v codegraph >/dev/null 2>&1; then
        if prompt_yes_no "现在运行 codegraph install 配置 Agent，并在目标项目运行 codegraph init 建索引？"; then
            codegraph install || echo "  [!] Agent 配置未完成，请按提示检查后重试。"
            (cd "$target" && codegraph init) || echo "  [!] 项目索引初始化未完成，可稍后在项目目录运行 codegraph init。"
        else
            echo "  后续配置命令：codegraph install；然后在项目目录运行：codegraph init"
        fi
    fi

    if command -v rtk >/dev/null 2>&1 && rtk gain >/dev/null 2>&1; then
        echo -e "  ${GREEN}[√] 已检测到 Rust Token Killer (RTK) CLI。${NC}"
    else
        echo "  RTK CLI 未安装或检测到的 rtk 不是 Rust Token Killer。"
        if prompt_yes_no "现在安装 Rust Token Killer (RTK) CLI？"; then
            if ! command -v curl >/dev/null 2>&1; then
                echo "  [!] 缺少 curl。请按官方说明安装：${install_rtk}"
                echo "  安装后：运行 rtk gain 验证，再进入目标项目运行 rtk init。"
            elif sh -c "$install_rtk"; then
                echo -e "  ${GREEN}[√] RTK 安装器已执行。请重开终端并运行 rtk gain 验证。${NC}"
            else
                echo "  [!] RTK 安装失败。官方命令：${install_rtk}"
            fi
        else
            echo "  安装命令：${install_rtk}（安装后用 rtk gain 验证，避免同名工具混淆）"
            echo "  验证后：进入目标项目运行 rtk init 配置支持的 Agent Hook。"
        fi
    fi

    if command -v rtk >/dev/null 2>&1 && rtk gain >/dev/null 2>&1; then
        if prompt_yes_no "现在在目标项目运行 rtk init 配置 RTK Hook？"; then
            (cd "$target" && rtk init) || echo "  [!] RTK 项目初始化未完成，请按当前版本提示处理。"
        else
            echo "  后续项目配置命令：cd \"${target}\" && rtk init"
        fi
    fi
}

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
        if git -C "${SCRIPT_DIR}" pull --ff-only; then
            echo -e "  ${GREEN}[√] 本地模板已与远程上游同步。${NC}"
        else
            echo -e "  ${YELLOW}[!] Git pull 出现告警，将继续使用当前模板。${NC}"
        fi
    else
        echo -e "  ${NC}[i] 当前模板目录非 Git 仓库，跳过 git pull。${NC}"
    fi

    echo -e "  ${NC}[i] 仅更新本模板仓库；不会升级全局 CLI，也不会在当前目录运行第三方技能更新器。${NC}"
fi

# ==============================================================================
# 2. Deploy / Update Global Rules (--global)
# ==============================================================================
if [ "$DEPLOY_GLOBAL" = true ]; then
    echo -e "\n${YELLOW}>>> [1/3] 正在部署/更新用户全局规则...${NC}"
    ANTIGRAVITY_GEMINI_TEMPLATE="${SCRIPT_DIR}/templates/antigravity-GEMINI.md"

    if [ ! -f "${GLOBAL_TEMPLATE}" ]; then
        echo -e "${YELLOW}[警告] 未找到全局模板 ${GLOBAL_TEMPLATE}，跳过全局部署。${NC}"
    else
        # A. Claude Code (~/.claude/CLAUDE.md)
        deploy_global_rule "Claude Code" "${HOME}/.claude/CLAUDE.md"

        # B. Current Antigravity releases load AGENTS.md; GEMINI.md supports older surfaces.
        deploy_global_rule "Antigravity 2.0 / CLI / IDE" "${HOME}/.gemini/AGENTS.md"
        if [ -f "$ANTIGRAVITY_GEMINI_TEMPLATE" ]; then
            deploy_global_rule "Antigravity legacy GEMINI.md compatibility" "${HOME}/.gemini/GEMINI.md" "$ANTIGRAVITY_GEMINI_TEMPLATE"
        else
            echo "  [!] Antigravity GEMINI.md compatibility template not found: ${ANTIGRAVITY_GEMINI_TEMPLATE}" >&2
        fi

        # C. Codex CLI / app (CODEX_HOME or ~/.codex); an active override wins.
        CODEX_HOME_DIR="${CODEX_HOME:-${HOME}/.codex}"
        if [ -s "${CODEX_HOME_DIR}/AGENTS.override.md" ]; then
            CODEX_GLOBAL_FILE="${CODEX_HOME_DIR}/AGENTS.override.md"
            echo "  [i] 检测到 Codex 全局覆盖文件，将更新当前生效的 AGENTS.override.md。"
        else
            CODEX_GLOBAL_FILE="${CODEX_HOME_DIR}/AGENTS.md"
        fi
        deploy_global_rule "Codex" "$CODEX_GLOBAL_FILE"
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

# Note: no Zed-specific configuration is created.

# Claude Code PreToolUse Security Hooks (.claude/settings.json + .claude/hooks/)
if [ -f "${SOURCE_CLAUDE_SETTINGS}" ]; then
    mkdir -p "${TARGET_PROJECT_DIR}/.claude"
    TARGET_CLAUDE_SETTINGS="${TARGET_PROJECT_DIR}/.claude/settings.json"
    if [ "$DO_UPDATE" = true ] || [ ! -f "${TARGET_CLAUDE_SETTINGS}" ]; then
        if [ "$DO_UPDATE" = true ]; then backup_path "${TARGET_CLAUDE_SETTINGS}"; fi
        cp -f "${SOURCE_CLAUDE_SETTINGS}" "${TARGET_CLAUDE_SETTINGS}"
        echo -e "  ${GREEN}[√] 已部署 Claude Code 安全拦截钩子: .claude/settings.json${NC}"
    else
        echo "  [i] 目标项目已存在 .claude/settings.json，跳过。"
    fi
    # Deploy hook scripts (.claude/hooks/)
    SOURCE_HOOKS_DIR="${SCRIPT_DIR}/.claude/hooks"
    if [ -d "${SOURCE_HOOKS_DIR}" ]; then
        TARGET_HOOKS_DIR="${TARGET_PROJECT_DIR}/.claude/hooks"
        mkdir -p "${TARGET_HOOKS_DIR}"
        for hook in "${SOURCE_HOOKS_DIR}"/*.mjs; do
            [ -f "$hook" ] || continue
            hook_name=$(basename "$hook")
            target_hook="${TARGET_HOOKS_DIR}/${hook_name}"
            if [ "$DO_UPDATE" = true ] || [ ! -f "$target_hook" ]; then
                if [ "$DO_UPDATE" = true ]; then backup_path "$target_hook"; fi
                cp -f "$hook" "$target_hook"
            fi
        done
        echo -e "  ${GREEN}[√] 已部署钩子脚本: .claude/hooks/${NC}"
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
                if [ "$DO_UPDATE" = true ]; then backup_path "${TARGET_RULES_DIR}/${rule_name}"; fi
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
                if [ "$DO_UPDATE" = true ]; then backup_path "${dest_skill}"; fi
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
        if [ "$DO_UPDATE" = true ]; then backup_path "${TARGET_PROJECT_DIR}/skills-lock.json"; fi
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

guide_optional_cli_tools "$TARGET_PROJECT_DIR"

echo -e "\n${GREEN}==================================================${NC}"
echo -e "${GREEN} 部署完成！${NC}"
echo -e "${CYAN} 目标项目: ${TARGET_PROJECT_DIR}${NC}"
echo -e "${CYAN} 规则目录: ${TARGET_RULES_DIR}${NC}"
echo -e "${CYAN} 技能目录: ${TARGET_SKILLS_DIR}${NC}"
if command -v comet >/dev/null 2>&1; then
    echo -e "\n${YELLOW}[TIP] 检测到 Comet CLI。请按当前版本文档为该项目选择并配置工作流。${NC}"
else
    echo -e "\n${NC}[i] 规则与技能文件已部署；是否自动加载取决于宿主工具。${NC}"
fi
echo -e "${GREEN}==================================================${NC}"
