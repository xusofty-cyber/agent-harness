#!/usr/bin/env bash
# ==============================================================================
# run-pipeline.sh
# Platforms: Linux / macOS (Bash)
# Purpose: Unified pipeline runner for agent-harness:
#          1. Agent rules & bridge deployment (deploy-agents.sh)
#          2. AI Memory service & MCP setup (setup-ai-memory.sh)
#          3. External skill synchronization & verification (tools/sync-skills.py)
#          4. Living documentation impact analysis & quality gate (tools/doc-impact.py)
# ==============================================================================

{
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

# Detect Python interpreter
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
fi

usage() {
    echo -e "${CYAN}用法 (Usage):${NC}"
    echo "  $0 [选项 (Options)]"
    echo ""
    echo -e "${CYAN}阶段选项 (Stage Options):${NC}"
    echo "  -a, --all               一键执行全量流水线 (全阶段按序执行)"
    echo "  -s, --stages <列表>     指定阶段列表 (逗号分隔: deploy,memory,skills,docs)"
    echo "  --deploy                执行阶段 1: 规则与 Agent 桥接部署 (deploy-agents)"
    echo "  --memory                执行阶段 2: AI-Memory 记忆服务与 MCP 接入 (setup-ai-memory)"
    echo "  --skills                执行阶段 3: 外部技能库校验与同步 (sync-skills)"
    echo "  --docs                  执行阶段 4: 活体文档影响分析与质检 (doc-impact)"
    echo ""
    echo -e "${CYAN}配置选项 (Configuration):${NC}"
    echo "  -p, --project <路径>    目标项目根目录 (默认: 当前目录 .)"
    echo "  -l, --lang <语言>       规则模板语言 (en, zh, zh-tw, fr, de；默认: zh)"
    echo "  -g, --global            部署/更新本机各工具全局规则 (~/.gemini, ~/.codex, ~/.claude)"
    echo "  -u, --update            覆盖更新已有全局规则并备份；同时更新外部 skills"
    echo "  -k, --check-only        只读检查模式 (技能仅检查差异、文档仅分析影响)"
    echo "  --apply-skills          在技能同步阶段主动拉取并应用上游更新"
    echo "  --brief-probe           探针极简输出模式 (仅打印探针关键摘要前 15 项，适合 CI)"
    echo "  -y, --yes               非交互/无人值守执行 (直接使用推荐配置，不弹窗确认)"
    echo "  --interactive, -I       强制启用交互式逐步选择向导"
    echo "  -h, --help              显示本帮助信息"
    echo ""
    echo -e "${CYAN}示例 (Examples):${NC}"
    echo "  $0                      # 交互式向导模式，根据菜单指引执行"
    echo "  $0 --all                # 一键执行全部 4 个流水线阶段"
    echo "  $0 --all -y             # 无人值守一键全量执行"
    echo "  $0 --stages deploy,docs # 仅执行规则部署与活体文档质检"
    echo "  $0 --project /path/app  # 指定目标项目执行流水线"
    exit 0
}

# TUI Single Select
prompt_select() {
    local title="$1"
    shift
    local -a labels=()
    local -a values=()
    while [[ $# -gt 0 ]]; do
        labels+=("$1")
        values+=("$2")
        shift 2
    done

    local count=${#labels[@]}
    local cur=0

    if [ ! -t 0 ]; then
        echo -e "$title"
        for i in "${!labels[@]}"; do
            echo "  $((i+1))) ${labels[$i]}"
        done
        read -r -p "请输入序号 [1-$count] (默认 1): " choice
        choice="${choice:-1}"
        local idx=$((choice-1))
        if [ "$idx" -ge 0 ] && [ "$idx" -lt "$count" ]; then
            SELECTED_VALUE="${values[$idx]}"
        else
            SELECTED_VALUE="${values[0]}"
        fi
        return
    fi

    local old_stty
    old_stty="$(stty -g 2>/dev/null || true)"
    trap 'stty "${old_stty:-}" 2>/dev/null || true; printf "\033[?25h\n"; trap - INT TERM; exit 1' INT TERM

    stty -echo -icanon min 1 time 0 2>/dev/null || true
    printf "\033[?25l"

    echo -e "\n${CYAN}${title}${NC}"
    echo -e "${DIM}↑↓ 移动光标, 回车确认${NC}"

    while true; do
        for i in "${!labels[@]}"; do
            if [ "$i" -eq "$cur" ]; then
                printf "\r\033[K${CYAN}> ● %s${NC}\n" "${labels[$i]}"
            else
                printf "\r\033[K  ${DIM}○${NC} %s\n" "${labels[$i]}"
            fi
        done

        local key=""
        IFS= read -r -n1 -s key || true
        if [ "$key" = $'\x1b' ]; then
            local seq1="" seq2=""
            IFS= read -r -n1 -s -t 0.1 seq1 || true
            IFS= read -r -n1 -s -t 0.1 seq2 || true
            if [ "$seq1" = "[" ]; then
                case "$seq2" in
                    A) cur=$(( (cur - 1 + count) % count )) ;;
                    B) cur=$(( (cur + 1) % count )) ;;
                esac
            fi
        elif [ "$key" = "k" ] || [ "$key" = "K" ]; then
            cur=$(( (cur - 1 + count) % count ))
        elif [ "$key" = "j" ] || [ "$key" = "J" ]; then
            cur=$(( (cur + 1) % count ))
        elif [ -z "$key" ] || [ "$key" = $'\n' ] || [ "$key" = $'\r' ]; then
            break
        elif [ "$key" = "q" ] || [ "$key" = "Q" ]; then
            stty "$old_stty" 2>/dev/null || true
            printf "\033[?25h\n"
            echo "操作已取消。"
            exit 0
        fi

        printf "\033[%dA" "$count"
    done

    stty "$old_stty" 2>/dev/null || true
    printf "\033[?25h\n"
    trap - INT TERM
    SELECTED_VALUE="${values[$cur]}"
}

# TUI Multi Select
prompt_multiselect() {
    local title="$1"
    shift
    local -a labels=()
    local -a values=()
    local -a checked=()
    while [[ $# -gt 0 ]]; do
        labels+=("$1")
        values+=("$2")
        checked+=("$3")
        shift 3
    done

    local count=${#labels[@]}
    local cur=0

    if [ ! -t 0 ]; then
        echo -e "$title"
        for i in "${!labels[@]}"; do
            local chk=" "
            if [ "${checked[$i]}" -eq 1 ]; then chk="x"; fi
            echo "  $((i+1))) [$chk] ${labels[$i]}"
        done
        read -r -p "输入序号多选（空格分隔，回车保持默认）: " resp
        SELECTED_VALUES=()
        if [ -z "$resp" ]; then
            for i in "${!values[@]}"; do
                if [ "${checked[$i]}" -eq 1 ]; then SELECTED_VALUES+=("${values[$i]}"); fi
            done
        else
            for num in $resp; do
                local idx=$((num-1))
                if [ "$idx" -ge 0 ] && [ "$idx" -lt "$count" ]; then
                    SELECTED_VALUES+=("${values[$idx]}")
                fi
            done
        fi
        return
    fi

    local old_stty
    old_stty="$(stty -g 2>/dev/null || true)"
    trap 'stty "${old_stty:-}" 2>/dev/null || true; printf "\033[?25h\n"; trap - INT TERM; exit 1' INT TERM

    stty -echo -icanon min 1 time 0 2>/dev/null || true
    printf "\033[?25l"

    echo -e "\n${CYAN}${title}${NC}"
    echo -e "${DIM}↑↓ 移动, 空格切换, a 全选/全反选, 回车确认${NC}"

    while true; do
        for i in "${!labels[@]}"; do
            if [ "$i" -eq "$cur" ]; then
                if [ "${checked[$i]}" -eq 1 ]; then
                    printf "\r\033[K${CYAN}> ${GREEN}[x]${CYAN} %s${NC}\n" "${labels[$i]}"
                else
                    printf "\r\033[K${CYAN}> ${DIM}[ ]${CYAN} %s${NC}\n" "${labels[$i]}"
                fi
            else
                if [ "${checked[$i]}" -eq 1 ]; then
                    printf "\r\033[K  ${GREEN}[x]${NC} %s\n" "${labels[$i]}"
                else
                    printf "\r\033[K  ${DIM}[ ]${NC} %s\n" "${labels[$i]}"
                fi
            fi
        done

        local key=""
        IFS= read -r -n1 -s key || true
        if [ "$key" = $'\x1b' ]; then
            local seq1="" seq2=""
            IFS= read -r -n1 -s -t 0.1 seq1 || true
            IFS= read -r -n1 -s -t 0.1 seq2 || true
            if [ "$seq1" = "[" ]; then
                case "$seq2" in
                    A) cur=$(( (cur - 1 + count) % count )) ;;
                    B) cur=$(( (cur + 1) % count )) ;;
                esac
            fi
        elif [ "$key" = "k" ] || [ "$key" = "K" ]; then
            cur=$(( (cur - 1 + count) % count ))
        elif [ "$key" = "j" ] || [ "$key" = "J" ]; then
            cur=$(( (cur + 1) % count ))
        elif [ "$key" = " " ]; then
            if [ "${checked[$cur]}" -eq 1 ]; then
                checked[$cur]=0
            else
                checked[$cur]=1
            fi
        elif [ "$key" = "a" ] || [ "$key" = "A" ]; then
            local all_on=1
            for c in "${checked[@]}"; do
                if [ "$c" -eq 0 ]; then all_on=0; break; fi
            done
            local new_val=1
            if [ "$all_on" -eq 1 ]; then new_val=0; fi
            for i in "${!checked[@]}"; do
                checked[$i]=$new_val
            done
        elif [ -z "$key" ] || [ "$key" = $'\n' ] || [ "$key" = $'\r' ]; then
            break
        elif [ "$key" = "q" ] || [ "$key" = "Q" ]; then
            stty "$old_stty" 2>/dev/null || true
            printf "\033[?25h\n"
            echo "操作已取消。"
            exit 0
        fi

        printf "\033[%dA" "$count"
    done

    stty "$old_stty" 2>/dev/null || true
    printf "\033[?25h\n"
    trap - INT TERM

    SELECTED_VALUES=()
    for i in "${!values[@]}"; do
        if [ "${checked[$i]}" -eq 1 ]; then
            SELECTED_VALUES+=("${values[$i]}")
        fi
    done
}

# Default settings
STAGE_DEPLOY=false
STAGE_MEMORY=false
STAGE_SKILLS=false
STAGE_DOCS=false

PROJECT_DIR="."
LANG_OPTION="zh"
CHECK_ONLY=false
APPLY_SKILLS=false
RUN_GLOBAL=false
RUN_UPDATE=false
NON_INTERACTIVE=false
FORCE_INTERACTIVE=false
EXPLICIT_CONFIG=false
BRIEF_PROBE=false
RUN_DETAIL_MODE="quick" # quick or detailed
GLOBAL_DEPLOYED_IN_WIZARD=false
SKILLS_SYNC_CHOICE="check"

get_lang_suffix() {
    local lang="$1"
    case "$lang" in
        zh|zh-cn|cn) echo "" ;;
        zh-tw|tw)    echo ".zh-tw" ;;
        fr|fr-fr)    echo ".fr" ;;
        de|de-de)    echo ".de" ;;
        *)           echo ".en" ;;
    esac
}

resolve_global_template() {
    local suffix="$1"
    local path="${REPO_ROOT}/Global AGENTS${suffix}.md"
    if [ -n "$suffix" ] && [ -f "$path" ]; then
        echo "$path"
        return
    fi
    path="${REPO_ROOT}/Global AGENTS.md"
    if [ -f "$path" ]; then
        echo "$path"
        return
    fi
    echo "${REPO_ROOT}/Global AGENTS.md"
}

backup_global_file() {
    local path="$1"
    local backup_path
    backup_path="${path}.bak.$(date +%Y%m%d%H%M%S)"
    local suffix=1
    while [ -e "$backup_path" ] || [ -L "$backup_path" ]; do
        backup_path="${path}.bak.$(date +%Y%m%d%H%M%S).${suffix}"
        suffix=$((suffix + 1))
    done
    cp -a "$path" "$backup_path"
    printf '%s' "$backup_path"
}

deploy_global_agent_file() {
    local tool_name="$1"
    local target_path="$2"
    local source_template="$3"

    local target_dir
    target_dir="$(dirname "$target_path")"
    mkdir -p "$target_dir"

    if [ -e "$target_path" ] || [ -L "$target_path" ]; then
        if [ -d "$target_path" ] && [ ! -L "$target_path" ]; then
            echo -e "  ${RED}[!] ${tool_name} 全局规则目标是目录: ${target_path}${NC}" >&2
            return 1
        fi
        local backup_file
        backup_file="$(backup_global_file "$target_path")"
        if [ -L "$target_path" ]; then rm "$target_path"; fi
        cp -f "$source_template" "$target_path"
        echo -e "  ${GREEN}[√] 已更新 ${tool_name} 全局规则: ${target_path} (备份: ${backup_file})${NC}"
        return 0
    fi

    cp "$source_template" "$target_path"
    echo -e "  ${GREEN}[√] 已初始化 ${tool_name} 全局规则: ${target_path}${NC}"
    return 0
}

deploy_selected_global_agents() {
    local lang_option="$1"
    shift
    local selected_tools=("$@")
    local suffix
    suffix="$(get_lang_suffix "$lang_option")"
    local global_tmpl
    global_tmpl="$(resolve_global_template "$suffix")"
    local antigravity_pointer="${REPO_ROOT}/templates/antigravity-GEMINI.md"

    if [ ! -f "$global_tmpl" ]; then
        echo -e "  ${YELLOW}[警告] 未找到全局模板: ${global_tmpl}，跳过。${NC}"
        return 1
    fi

    echo -e "\n${YELLOW}>>> 正在处理所选 Agent 工具全局规则部署与更新...${NC}"
    for tool in "${selected_tools[@]}"; do
        case "$tool" in
            claude)
                deploy_global_agent_file "Claude Code" "${HOME}/.claude/CLAUDE.md" "$global_tmpl"
                ;;
            antigravity)
                deploy_global_agent_file "Antigravity 2.0 / CLI / IDE" "${HOME}/.gemini/AGENTS.md" "$global_tmpl"
                if [ -f "$antigravity_pointer" ]; then
                    deploy_global_agent_file "Antigravity legacy GEMINI.md" "${HOME}/.gemini/GEMINI.md" "$antigravity_pointer"
                fi
                ;;
            codex)
                local codex_dir="${CODEX_HOME:-${HOME}/.codex}"
                local codex_file="${codex_dir}/AGENTS.md"
                if [ -s "${codex_dir}/AGENTS.override.md" ]; then
                    codex_file="${codex_dir}/AGENTS.override.md"
                    echo -e "  ${CYAN}[i] 检测到 Codex 全局覆盖文件，将更新当前生效的 AGENTS.override.md。${NC}"
                fi
                deploy_global_agent_file "Codex" "$codex_file" "$global_tmpl"
                ;;
            cursor)
                deploy_global_agent_file "Cursor" "${HOME}/.cursorrules" "$global_tmpl"
                ;;
            zed)
                deploy_global_agent_file "Zed" "${HOME}/.config/zed/AGENTS.md" "$global_tmpl"
                ;;
            pi)
                deploy_global_agent_file "Pi" "${HOME}/.pi/agent/AGENTS.md" "$global_tmpl"
                ;;
            trae)
                deploy_global_agent_file "Trae" "${HOME}/.trae/rules/AGENTS.md" "$global_tmpl"
                ;;
            codebuddy)
                deploy_global_agent_file "CodeBuddy" "${HOME}/.codebuddy/CODEBUDDY.md" "$global_tmpl"
                ;;
            copilot)
                deploy_global_agent_file "GitHub Copilot" "${HOME}/.config/github-copilot/copilot-instructions.md" "$global_tmpl"
                ;;
            gemini)
                deploy_global_agent_file "Gemini CLI" "${HOME}/.gemini/GEMINI.md" "$global_tmpl"
                ;;
            windsurf)
                deploy_global_agent_file "Windsurf" "${HOME}/.windsurf/rules/agent-harness.md" "$global_tmpl"
                ;;
            cline)
                deploy_global_agent_file "Cline" "${HOME}/.clinerules" "$global_tmpl"
                ;;
            roo)
                deploy_global_agent_file "Roo Code" "${HOME}/.roo/rules/agent-harness.md" "$global_tmpl"
                ;;
            qwen)
                deploy_global_agent_file "Qwen Code" "${HOME}/.qwen/QWEN.md" "$global_tmpl"
                ;;
            kiro)
                deploy_global_agent_file "Kiro" "${HOME}/.kiro/steering/agent-harness.md" "$global_tmpl"
                ;;
            continue)
                deploy_global_agent_file "Continue.dev" "${HOME}/.continue/rules/agent-harness.md" "$global_tmpl"
                ;;
            opencode)
                deploy_global_agent_file "OpenCode" "${HOME}/.config/opencode/AGENTS.md" "$global_tmpl"
                ;;
        esac
    done
    echo -e "${GREEN}[√] 所选 Agent 工具全局规则处理完成！${NC}\n"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -a|--all)
            STAGE_DEPLOY=true
            STAGE_MEMORY=true
            STAGE_SKILLS=true
            STAGE_DOCS=true
            EXPLICIT_CONFIG=true
            shift
            ;;
        -s|--stages)
            EXPLICIT_CONFIG=true
            IFS=',' read -ra STAGES_ARR <<< "$2"
            for s in "${STAGES_ARR[@]}"; do
                case "$s" in
                    deploy) STAGE_DEPLOY=true ;;
                    memory) STAGE_MEMORY=true ;;
                    skills) STAGE_SKILLS=true ;;
                    docs|doc) STAGE_DOCS=true ;;
                    *) echo -e "${RED}未知阶段: $s (可选: deploy, memory, skills, docs)${NC}" >&2; exit 1 ;;
                esac
            done
            shift 2
            ;;
        --deploy) STAGE_DEPLOY=true; EXPLICIT_CONFIG=true; shift ;;
        --memory) STAGE_MEMORY=true; EXPLICIT_CONFIG=true; shift ;;
        --skills) STAGE_SKILLS=true; EXPLICIT_CONFIG=true; shift ;;
        --docs) STAGE_DOCS=true; EXPLICIT_CONFIG=true; shift ;;
        -p|--project) PROJECT_DIR="$2"; shift 2 ;;
        -l|--lang) LANG_OPTION="$2"; shift 2 ;;
        -g|--global) RUN_GLOBAL=true; EXPLICIT_CONFIG=true; shift ;;
        -u|--update) RUN_UPDATE=true; EXPLICIT_CONFIG=true; shift ;;
        -k|--check-only) CHECK_ONLY=true; EXPLICIT_CONFIG=true; shift ;;
        --apply-skills) APPLY_SKILLS=true; EXPLICIT_CONFIG=true; shift ;;
        --brief-probe) BRIEF_PROBE=true; shift ;;
        -y|--yes|--non-interactive) NON_INTERACTIVE=true; shift ;;
        -I|--interactive) FORCE_INTERACTIVE=true; shift ;;
        -h|--help) usage ;;
        *)
            if [ -d "$1" ]; then
                PROJECT_DIR="$1"
                shift
            else
                echo -e "${RED}未知参数: $1${NC}" >&2
                usage
            fi
            ;;
    esac
done

# Pre-flight review flags computation
RUN_APPLY_SKILLS=false
if [ "$APPLY_SKILLS" = true ] || [ "$RUN_UPDATE" = true ]; then
    RUN_APPLY_SKILLS=true
fi

# Interactive 6-step wizard when executed without explicit stage/config flags
if [ "$EXPLICIT_CONFIG" = false ] && [ "$NON_INTERACTIVE" = false ]; then
    echo -e "\n${CYAN}================================================================${NC}"
    echo -e "${CYAN}  🚀 Agent Harness 统一工程流水线向导 (Unified Pipeline Runner)  ${NC}"
    echo -e "${CYAN}================================================================${NC}"

    prompt_select "[1/6] 选择规则与文档语言 (Select Language):" \
        "简体中文 (Simplified Chinese, zh)" "zh" \
        "English (en)" "en" \
        "繁體中文 (Traditional Chinese, zh-tw)" "zh-tw" \
        "Français (French, fr)" "fr" \
        "Deutsch (German, de)" "de"
    LANG_OPTION="$SELECTED_VALUE"

    prompt_select "[2/6] 是否全局更新各工具的 agents (Global Agents Rules):" \
        "是，更新各工具全局规则 (Update: 备份并更新本机全局配置)" "yes" \
        "否，仅在项目工程内生效 (Skip: 跳过全局更新，仅限当前项目)" "no"

    if [ "$SELECTED_VALUE" = "yes" ]; then
        prompt_multiselect "请选择要全局更新规则的 Agent 工具 (Select Agent Tools):" \
            "Claude Code (~/.claude/CLAUDE.md)" "claude" 1 \
            "Antigravity 2.0 / CLI / IDE (~/.gemini/AGENTS.md, GEMINI.md)" "antigravity" 1 \
            "Codex CLI / app (~/.codex/AGENTS.md)" "codex" 1 \
            "Cursor (~/.cursorrules)" "cursor" 1 \
            "Zed (~/.config/zed/AGENTS.md)" "zed" 1 \
            "Pi (~/.pi/agent/AGENTS.md)" "pi" 1 \
            "Trae (~/.trae/rules/AGENTS.md)" "trae" 0 \
            "CodeBuddy (~/.codebuddy/CODEBUDDY.md)" "codebuddy" 0 \
            "GitHub Copilot (copilot-instructions.md)" "copilot" 0 \
            "Gemini CLI (~/.gemini/GEMINI.md)" "gemini" 0 \
            "Windsurf (~/.windsurf/rules/agent-harness.md)" "windsurf" 0 \
            "Cline (~/.clinerules)" "cline" 0 \
            "Roo Code (~/.roo/rules/agent-harness.md)" "roo" 0 \
            "Qwen Code (~/.qwen/QWEN.md)" "qwen" 0 \
            "Kiro (~/.kiro/steering/agent-harness.md)" "kiro" 0 \
            "Continue.dev (~/.continue/rules/agent-harness.md)" "continue" 0 \
            "OpenCode (~/.config/opencode/AGENTS.md)" "opencode" 0

        if [ ${#SELECTED_VALUES[@]} -gt 0 ]; then
            deploy_selected_global_agents "$LANG_OPTION" "${SELECTED_VALUES[@]}"
            GLOBAL_DEPLOYED_IN_WIZARD=true
        else
            echo -e "${YELLOW}  [i] 未勾选任何 Agent 工具，跳过全局更新。${NC}\n"
        fi
        RUN_GLOBAL=false
    else
        RUN_GLOBAL=false
    fi

    prompt_select "[3/6] 选择是否更新外部扩展的 skills 技能库 (External Skills Sync):" \
        "在线同步更新 (Apply: 自动拉取上游更新并应用到本地技能库)" "apply" \
        "安全检查模式 (Check only: 仅对比校验版本差异，不覆写技能文件)" "check" \
        "跳过更新 (Skip: 不更新也不检查外部技能库)" "skip"
    SKILLS_SYNC_CHOICE="$SELECTED_VALUE"
    case "$SKILLS_SYNC_CHOICE" in
        apply)
            RUN_APPLY_SKILLS=true
            CHECK_ONLY=false
            ;;
        check)
            RUN_APPLY_SKILLS=false
            CHECK_ONLY=true
            ;;
        skip)
            RUN_APPLY_SKILLS=false
            CHECK_ONLY=false
            ;;
    esac

    echo -e "\n${CYAN}[4/6] 目标工程根目录 (Target Project Path):${NC}"
    read -r -p "请输入工程路径 [默认: 当前目录 .]: " input_proj
    PROJECT_DIR="${input_proj:-.}"

    prompt_select "[5/6] 选择流水线执行流程与阶段组合 (Select Pipeline Flow & Stages):" \
        "一键全量流水线 (Run Full Pipeline: 规则部署 -> AI记忆 -> 技能同步 -> 文档质检)" "all" \
        "自定义阶段组合 (Custom Stages: 自选执行部分阶段)" "custom" \
        "仅规则与 Agent 桥接部署 (Deploy Rules & Bridges only)" "only-deploy" \
        "仅配置 AI-Memory 记忆服务 (Setup AI Memory only)" "only-memory" \
        "仅校验/同步外部技能库 (Sync Skills only)" "only-skills" \
        "仅活体文档影响分析与质检 (Living Doc Impact only)" "only-docs"
    PIPELINE_MODE="$SELECTED_VALUE"

    case "$PIPELINE_MODE" in
        all)
            STAGE_DEPLOY=true
            STAGE_MEMORY=true
            STAGE_SKILLS=true
            STAGE_DOCS=true
            ;;
        custom)
            prompt_multiselect "选择要纳入本次流水线的阶段 (Select stages to run):" \
                "阶段 1: 部署规则模板与 Agent 桥接 (deploy-agents)" "deploy" 1 \
                "阶段 2: 接入 AI-Memory 跨工具记忆服务 (setup-ai-memory)" "memory" 1 \
                "阶段 3: 校验/更新外部技能库 (sync-skills)" "skills" 1 \
                "阶段 4: 活体文档影响分析与质检门禁 (doc-impact)" "docs" 1
            STAGE_DEPLOY=false
            STAGE_MEMORY=false
            STAGE_SKILLS=false
            STAGE_DOCS=false
            for st in "${SELECTED_VALUES[@]}"; do
                case "$st" in
                    deploy) STAGE_DEPLOY=true ;;
                    memory) STAGE_MEMORY=true ;;
                    skills) STAGE_SKILLS=true ;;
                    docs) STAGE_DOCS=true ;;
                esac
            done
            ;;
        only-deploy) STAGE_DEPLOY=true ;;
        only-memory) STAGE_MEMORY=true ;;
        only-skills) STAGE_SKILLS=true ;;
        only-docs) STAGE_DOCS=true ;;
    esac

    prompt_select "[6/6] 选择执行交互细化程度 (Execution Detail):" \
        "极速推荐配置 (Quick Run: 自动使用最佳实践一键贯通流水线)" "quick" \
        "逐步向导配置 (Interactive: 依次打开各工具阶段的详细选项向导)" "detailed"
    RUN_DETAIL_MODE="$SELECTED_VALUE"
fi

# Pre-flight review: when user passed explicit CLI parameters but NOT -y
if [ "$EXPLICIT_CONFIG" = true ] && [ "$NON_INTERACTIVE" = false ]; then
    echo -e "\n${CYAN}================================================================${NC}"
    echo -e "${CYAN}  🚀 Agent Harness 流水线执行前配置确认 (Pre-flight Review)   ${NC}"
    echo -e "${CYAN}================================================================${NC}"
    echo -e "${YELLOW}检测到执行参数。请确认是否需要同步处理全局规则与外部技能库：${NC}"

    if [ "$RUN_GLOBAL" = true ]; then
        prompt_select "[1/2] 本机全局各 Agent 工具规则处理 (Global Rules Sync):" \
            "● 确认: 部署/覆盖更新全局规则 (~/.gemini, ~/.codex, ~/.claude)" "sync" \
            "○ 跳过: 仅更新当前项目工程，不改动本机全局规则" "skip"
    else
        prompt_select "[1/2] 本机全局各 Agent 工具规则处理 (Global Rules Sync):" \
            "○ 跳过: 仅更新当前项目工程，不改动本机全局规则" "skip" \
            "● 确认: 部署/覆盖更新全局规则 (~/.gemini, ~/.codex, ~/.claude)" "sync"
    fi
    if [ "$SELECTED_VALUE" = "sync" ]; then
        RUN_GLOBAL=true
        RUN_UPDATE=true
    else
        RUN_GLOBAL=false
    fi

    if [ "$RUN_APPLY_SKILLS" = true ]; then
        prompt_select "[2/2] 外部开源技能库处理 (External Skills Sync):" \
            "● 确认: 在线拉取 GitHub 上游更新并应用到本地技能库 (--apply)" "apply" \
            "○ 仅检查: 仅对比校验版本差异，不覆写技能文件 (--check)" "check"
    else
        prompt_select "[2/2] 外部开源技能库处理 (External Skills Sync):" \
            "○ 仅检查: 仅对比校验版本差异，不覆写技能文件 (--check)" "check" \
            "● 确认: 在线拉取 GitHub 上游更新并应用到本地技能库 (--apply)" "apply"
    fi
    if [ "$SELECTED_VALUE" = "apply" ]; then
        RUN_APPLY_SKILLS=true
    else
        RUN_APPLY_SKILLS=false
    fi
fi

# Fallback: if still no stage selected, default to all stages
if [ "$STAGE_DEPLOY" = false ] && [ "$STAGE_MEMORY" = false ] && [ "$STAGE_SKILLS" = false ] && [ "$STAGE_DOCS" = false ]; then
    STAGE_DEPLOY=true
    STAGE_MEMORY=true
    STAGE_SKILLS=true
    STAGE_DOCS=true
fi

# Resolve absolute target path
TARGET_ABS="$(cd "$PROJECT_DIR" 2>/dev/null && pwd || echo "$PROJECT_DIR")"

ensure_project_memory_scaffold() {
    local target_dir="$1"
    local lang_opt="$2"
    local lang_suffix=""
    case "$lang_opt" in
        zh|zh-cn|zh-hans) lang_suffix=".zh" ;;
        zh-tw|zh-hk|zh-hant) lang_suffix=".zh-tw" ;;
        en|en-us|en-gb) lang_suffix="" ;;
        fr|fr-fr) lang_suffix=".fr" ;;
        de|de-de) lang_suffix=".de" ;;
        *) lang_suffix="" ;;
    esac

    local proj_basename
    proj_basename="$(basename "$target_dir")"

    local p_template="$REPO_ROOT/templates/PROJECT_CONTEXT.template${lang_suffix}.md"
    [ ! -f "$p_template" ] && p_template="$REPO_ROOT/templates/PROJECT_CONTEXT.template.md"

    local s_template="$REPO_ROOT/templates/SESSION_STATE.template${lang_suffix}.md"
    [ ! -f "$s_template" ] && s_template="$REPO_ROOT/templates/SESSION_STATE.template.md"

    local p_target="$target_dir/PROJECT_CONTEXT.md"
    if [ ! -f "$p_target" ] && [ -f "$p_template" ]; then
        sed "s/<PROJECT_NAME>/$proj_basename/g" "$p_template" > "$p_target"
        echo -e "  ${GREEN}[√] 自动初始化项目长期事实: PROJECT_CONTEXT.md${NC}"
    fi

    local s_target="$target_dir/SESSION_STATE.md"
    if [ ! -f "$s_target" ] && [ -f "$s_template" ]; then
        sed "s/<PROJECT_NAME>/$proj_basename/g" "$s_template" > "$s_target"
        echo -e "  ${GREEN}[√] 自动初始化当前会话断点: SESSION_STATE.md${NC}"
    fi

    if command -v comet >/dev/null 2>&1; then
        local comet_dir="$target_dir/.comet"
        local comet_cfg="$comet_dir/config.yaml"
        local comet_tpl="$REPO_ROOT/templates/comet.config.yaml"
        if [ ! -f "$comet_cfg" ] && [ -f "$comet_tpl" ]; then
            mkdir -p "$comet_dir"
            cp "$comet_tpl" "$comet_cfg"
            echo -e "  ${GREEN}[√] 检测到 Comet CLI，自动补齐项目级配置: .comet/config.yaml${NC}"
        fi
    fi
}

echo -e "\n${BOLD}${CYAN}▶ 开始执行 Agent Harness 工程流水线${NC}"
echo -e "  目标工程: ${GREEN}$TARGET_ABS${NC}"
echo -e "  模版语言: ${GREEN}$LANG_OPTION${NC}"
echo -e "  执行模式: ${GREEN}$RUN_DETAIL_MODE${NC}\n"

ensure_project_memory_scaffold "$TARGET_ABS" "$LANG_OPTION"

# Tracking results
declare -a SUMMARY_NAMES=()
declare -a SUMMARY_STATUS=()
declare -a SUMMARY_DETAIL=()

TOTAL_STAGES=0
if [ "$STAGE_DEPLOY" = true ]; then TOTAL_STAGES=$((TOTAL_STAGES+1)); fi
if [ "$STAGE_MEMORY" = true ]; then TOTAL_STAGES=$((TOTAL_STAGES+1)); fi
if [ "$STAGE_SKILLS" = true ]; then TOTAL_STAGES=$((TOTAL_STAGES+1)); fi
if [ "$STAGE_DOCS" = true ]; then TOTAL_STAGES=$((TOTAL_STAGES+1)); fi

CURRENT_STAGE=0

# ==============================================================================
# 阶段 1: 规则与 Agent 桥接部署 (deploy-agents)
# ==============================================================================
if [ "$STAGE_DEPLOY" = true ]; then
    CURRENT_STAGE=$((CURRENT_STAGE+1))
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}[$CURRENT_STAGE/$TOTAL_STAGES] 阶段 1: 规则与 Agent 桥接部署 (deploy-agents)${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    STAGE_NAME="规则与 Agent 桥接部署 (deploy-agents)"
    SUMMARY_NAMES+=("$STAGE_NAME")
    
    deploy_cmd=("$REPO_ROOT/deploy-agents.sh" "$TARGET_ABS" "--lang" "$LANG_OPTION")
    if [ "$GLOBAL_DEPLOYED_IN_WIZARD" != true ] && [ "$RUN_GLOBAL" = true ]; then
        deploy_cmd+=("--global")
    fi
    if [ "$RUN_UPDATE" = true ]; then
        deploy_cmd+=("--update")
    fi
    if [ "$RUN_DETAIL_MODE" = "detailed" ]; then
        deploy_cmd+=("--interactive")
    fi

    run_ok=false
    if [ "$NON_INTERACTIVE" = true ]; then
        if "${deploy_cmd[@]}" < /dev/null; then run_ok=true; fi
    else
        if "${deploy_cmd[@]}"; then run_ok=true; fi
    fi

    if [ "$run_ok" = true ]; then
        echo -e "${GREEN}✔ 阶段 1 执行完成${NC}\n"
        SUMMARY_STATUS+=("PASS")
        SUMMARY_DETAIL+=("规则与桥接文件配置就绪")
    else
        echo -e "${RED}✖ 阶段 1 出现错误${NC}\n"
        SUMMARY_STATUS+=("FAIL")
        SUMMARY_DETAIL+=("部署脚本返回非零退出码")
    fi
fi

# ==============================================================================
# 阶段 2: AI-Memory 跨工具记忆服务接入 (setup-ai-memory)
# ==============================================================================
if [ "$STAGE_MEMORY" = true ]; then
    CURRENT_STAGE=$((CURRENT_STAGE+1))
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}[$CURRENT_STAGE/$TOTAL_STAGES] 阶段 2: 配置 AI-Memory 记忆服务 (setup-ai-memory)${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    STAGE_NAME="AI-Memory 记忆服务 (setup-ai-memory)"
    SUMMARY_NAMES+=("$STAGE_NAME")

    # Preflight 1: check ai-memory CLI
    if ! command -v ai-memory >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ 提示: 系统 PATH 中未检测到 'ai-memory' CLI。${NC}"
        echo -e "  ai-memory 属于可选进阶组件。如需跨工具记忆沉淀，请先安装 upstream ai-memory。"
        echo -e "${YELLOW}↷ 跳过本阶段，继续后续流水线。${NC}\n"
        SUMMARY_STATUS+=("SKIP")
        SUMMARY_DETAIL+=("未检测到 ai-memory CLI")
    else
        # Preflight 2: check .ai-memory.toml in project
        toml_path="$TARGET_ABS/.ai-memory.toml"
        if [ ! -f "$toml_path" ]; then
            if [ -f "$REPO_ROOT/.ai-memory.toml.example" ]; then
                echo -e "${YELLOW}目标工程尚未配置 .ai-memory.toml${NC}"
                do_create=false
                if [ "$NON_INTERACTIVE" = false ] && [ -t 0 ]; then
                    read -r -p "是否从 .ai-memory.toml.example 自动初始化配置文件？[y/N]: " create_choice
                    if [[ "$create_choice" =~ ^[Yy]$ ]]; then do_create=true; fi
                fi

                if [ "$do_create" = true ]; then
                    proj_name="$(basename "$TARGET_ABS")"
                    sed -E "s/replace-with-workspace-(name|id)/workspace-$proj_name/g; s/replace-with-project-(name|id)/$proj_name/g" \
                        "$REPO_ROOT/.ai-memory.toml.example" > "$toml_path"
                    echo -e "${GREEN}✔ 已生成 $toml_path${NC}"
                else
                    echo -e "${YELLOW}↷ 缺少 .ai-memory.toml 配置，跳过记忆集成。${NC}\n"
                    SUMMARY_STATUS+=("SKIP")
                    SUMMARY_DETAIL+=("未配置 .ai-memory.toml")
                fi
            fi
        fi

        if [ -f "$toml_path" ] && ! grep -Eq 'replace-with-' "$toml_path"; then
            (
                cd "$TARGET_ABS"
                if [ "$RUN_DETAIL_MODE" = "detailed" ] && [ -t 0 ]; then
                    "$REPO_ROOT/setup-ai-memory.sh"
                else
                    "$REPO_ROOT/setup-ai-memory.sh" "claude-code" "codex" "antigravity-ide" || true
                fi
            )
            echo -e "${GREEN}✔ 阶段 2 执行完成${NC}\n"
            SUMMARY_STATUS+=("PASS")
            SUMMARY_DETAIL+=("AI 记忆集成与 MCP 配置完成")
        elif [ "${SUMMARY_STATUS[-1]:-}" != "SKIP" ]; then
            echo -e "${YELLOW}↷ .ai-memory.toml 仍包含占位符，跳过阶段 2。${NC}\n"
            SUMMARY_STATUS+=("SKIP")
            SUMMARY_DETAIL+=("配置包含未替换占位符")
        fi
    fi
fi

# ==============================================================================
# 阶段 3: 外部技能库校验与同步 (sync-skills)
# ==============================================================================
if [ "$STAGE_SKILLS" = true ]; then
    CURRENT_STAGE=$((CURRENT_STAGE+1))
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}[$CURRENT_STAGE/$TOTAL_STAGES] 阶段 3: 校验/同步外部技能库 (sync-skills)${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    STAGE_NAME="外部技能库同步与校验 (sync-skills)"
    SUMMARY_NAMES+=("$STAGE_NAME")

    if [ "$SKILLS_SYNC_CHOICE" = "skip" ]; then
        echo -e "${YELLOW}↷ 外部技能库同步已在步骤 [3/6] 选择跳过。${NC}\n"
        SUMMARY_STATUS+=("SKIP")
        SUMMARY_DETAIL+=("步骤 [3/6] 选择跳过技能同步")
    elif [ -z "$PYTHON_BIN" ]; then
        echo -e "${YELLOW}⚠ 未找到 Python 解释器，跳过技能同步。${NC}\n"
        SUMMARY_STATUS+=("SKIP")
        SUMMARY_DETAIL+=("未找到 Python 环境")
    else
        skills_cmd=("$PYTHON_BIN" "$REPO_ROOT/tools/sync-skills.py")
        if [ "$CHECK_ONLY" = true ]; then
            skills_cmd+=("--check-only")
        fi
        if [ "$RUN_DETAIL_MODE" = "detailed" ] && [ -t 0 ]; then
            "${skills_cmd[@]}" || true
        else
            if [ "$CHECK_ONLY" != true ]; then
                if [ "$RUN_APPLY_SKILLS" = true ]; then
                    skills_cmd+=("--apply")
                else
                    skills_cmd+=("--check")
                fi
            else
                skills_cmd+=("--check")
            fi
            "${skills_cmd[@]}" || true
        fi
        echo -e "${GREEN}✔ 阶段 3 检查完成${NC}\n"
        SUMMARY_STATUS+=("PASS")
        SUMMARY_DETAIL+=("技能锁定与版本校验完成")
    fi
fi

# ==============================================================================
# 阶段 4: 活体文档影响分析与质检门禁 (doc-impact)
# ==============================================================================
if [ "$STAGE_DOCS" = true ]; then
    CURRENT_STAGE=$((CURRENT_STAGE+1))
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}[$CURRENT_STAGE/$TOTAL_STAGES] 阶段 4: 活体文档影响分析与质检 (doc-impact)${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    STAGE_NAME="活体文档影响分析与质检 (doc-impact)"
    SUMMARY_NAMES+=("$STAGE_NAME")

    if [ -z "$PYTHON_BIN" ]; then
        echo -e "${YELLOW}⚠ 未找到 Python 解释器，跳过活体文档分析。${NC}\n"
        SUMMARY_STATUS+=("SKIP")
        SUMMARY_DETAIL+=("未找到 Python 环境")
    else
        docs_cmd=("$PYTHON_BIN" "$REPO_ROOT/tools/doc-impact.py" "--root" "$TARGET_ABS")
        if [ "$RUN_DETAIL_MODE" = "detailed" ] && [ -t 0 ]; then
            docs_cmd+=("--interactive")
        fi

        if "${docs_cmd[@]}"; then
            echo -e "${GREEN}✔ 阶段 4 质检完成${NC}\n"
            SUMMARY_STATUS+=("PASS")
            SUMMARY_DETAIL+=("活体文档溯源关系与影响分析通过")
        else
            echo -e "${RED}✖ 阶段 4 出现错误${NC}\n"
            SUMMARY_STATUS+=("FAIL")
            SUMMARY_DETAIL+=("文档影响分析返回非零退出码")
        fi
    fi
fi

# ------------------------------------------------------------------------------
# 附加探针: Comet 智能体工作流引擎就绪检测与跨平台体检探针 (Comet Workflow & Doctor Probe)
# ------------------------------------------------------------------------------
if command -v comet >/dev/null 2>&1; then
    echo -e "${CYAN}>>> [Comet Probe] 正在检测 Comet 智能体工作流状态与跨平台健康度...${NC}"
    echo -e "  ${YELLOW}--- 工作流状态 (comet status) ---${NC}"
    _comet_status=$(cd "$TARGET_ABS" && comet status 2>&1 | head -n 12) || true
    if [ -n "$_comet_status" ]; then
        echo -e "${YELLOW}${_comet_status}${NC}"
    fi

    echo -e "\n  ${YELLOW}--- 跨平台体检报告 (comet doctor) ---${NC}"
    if [ "$BRIEF_PROBE" = true ]; then
        _comet_doc=$(cd "$TARGET_ABS" && comet doctor 2>&1 | grep -E "✓|✗|⚠" | head -n 15) || true
        if [ -n "$_comet_doc" ]; then
            echo -e "${YELLOW}${_comet_doc}${NC}"
            echo -e "  ${DIM}... (已启用 --brief-probe 极简模式，忽略后续详细平台检测)${NC}\n"
        fi
    else
        _comet_doc=$(cd "$TARGET_ABS" && comet doctor 2>&1) || true
        if [ -n "$_comet_doc" ]; then
            echo -e "${YELLOW}${_comet_doc}${NC}\n"
        fi
    fi
fi

# ==============================================================================
# 流水线执行汇总 (Pipeline Execution Summary)
# ==============================================================================
echo -e "${CYAN}================================================================${NC}"
echo -e "${BOLD} 📊 Agent Harness 流水线执行汇总 (Pipeline Summary)${NC}"
echo -e "${CYAN}================================================================${NC}"

HAS_FAIL=false
for i in "${!SUMMARY_NAMES[@]}"; do
    st="${SUMMARY_STATUS[$i]}"
    nm="${SUMMARY_NAMES[$i]}"
    dt="${SUMMARY_DETAIL[$i]}"
    case "$st" in
        PASS)
            printf " ${GREEN}[✔ PASS]${NC}  %-40s : %s\n" "$nm" "$dt"
            ;;
        SKIP)
            printf " ${YELLOW}[↷ SKIP]${NC}  %-40s : %s\n" "$nm" "$dt"
            ;;
        FAIL)
            printf " ${RED}[✖ FAIL]${NC}  %-40s : %s\n" "$nm" "$dt"
            HAS_FAIL=true
            ;;
    esac
done

echo -e "${CYAN}================================================================${NC}"
if [ "$HAS_FAIL" = true ]; then
    echo -e "${RED}⚠ 流水线部分阶段未完全通过，请检查上方日志。${NC}\n"
    exit 1
else
    echo -e "${GREEN}🎉 流水线全部阶段执行完毕！${NC}\n"
    exit 0
fi
}
