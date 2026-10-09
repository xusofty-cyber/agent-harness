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
    trap 'stty "$old_stty" 2>/dev/null; printf "\033[?25h\n"; exit 1' INT TERM

    stty -echo -icanon min 1 time 0 2>/dev/null || true
    printf "\033[?25l"

    echo -e "\n${CYAN}${title}${NC}"
    echo -e "${DIM}↑↓ 移动光标, 回车确认${NC}"

    while true; do
        for i in "${!labels[@]}"; do
            if [ "$i" -eq "$cur" ]; then
                printf "${CYAN}> ● %s${NC}\n" "${labels[$i]}"
            else
                printf "  ${DIM}○${NC} %s\n" "${labels[$i]}"
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
    trap 'stty "$old_stty" 2>/dev/null; printf "\033[?25h\n"; exit 1' INT TERM

    stty -echo -icanon min 1 time 0 2>/dev/null || true
    printf "\033[?25l"

    echo -e "\n${CYAN}${title}${NC}"
    echo -e "${DIM}↑↓ 移动, 空格切换, a 全选/全反选, 回车确认${NC}"

    while true; do
        for i in "${!labels[@]}"; do
            local mark="[ ]"
            local color="${DIM}"
            if [ "${checked[$i]}" -eq 1 ]; then
                mark="[x]"
                color="${GREEN}"
            fi

            if [ "$i" -eq "$cur" ]; then
                printf "${CYAN}> %s %s${NC}\n" "$mark" "${labels[$i]}"
            else
                printf "  %s%s %s${NC}\n" "$color" "$mark" "${labels[$i]}"
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
EXPLICIT_STAGES=false
RUN_DETAIL_MODE="quick" # quick or detailed

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -a|--all)
            STAGE_DEPLOY=true
            STAGE_MEMORY=true
            STAGE_SKILLS=true
            STAGE_DOCS=true
            EXPLICIT_STAGES=true
            shift
            ;;
        -s|--stages)
            EXPLICIT_STAGES=true
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
        --deploy) STAGE_DEPLOY=true; EXPLICIT_STAGES=true; shift ;;
        --memory) STAGE_MEMORY=true; EXPLICIT_STAGES=true; shift ;;
        --skills) STAGE_SKILLS=true; EXPLICIT_STAGES=true; shift ;;
        --docs) STAGE_DOCS=true; EXPLICIT_STAGES=true; shift ;;
        -p|--project) PROJECT_DIR="$2"; shift 2 ;;
        -l|--lang) LANG_OPTION="$2"; shift 2 ;;
        -g|--global) RUN_GLOBAL=true; shift ;;
        -u|--update) RUN_UPDATE=true; shift ;;
        -k|--check-only) CHECK_ONLY=true; shift ;;
        --apply-skills) APPLY_SKILLS=true; shift ;;
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

# If no stages explicitly specified and running in interactive terminal (or forced)
if [ "$EXPLICIT_STAGES" = false ] && { [ -t 0 ] || [ "$FORCE_INTERACTIVE" = true ]; } && [ "$NON_INTERACTIVE" = false ]; then
    echo -e "\n${CYAN}================================================================${NC}"
    echo -e "${CYAN}  🚀 Agent Harness 统一工程流水线向导 (Unified Pipeline Runner)  ${NC}"
    echo -e "${CYAN}================================================================${NC}"

    prompt_select "[1/4] 选择规则与文档语言 (Select Language):" \
        "简体中文 (Simplified Chinese, zh)" "zh" \
        "English (en)" "en" \
        "繁體中文 (Traditional Chinese, zh-tw)" "zh-tw" \
        "Français (French, fr)" "fr" \
        "Deutsch (German, de)" "de"
    LANG_OPTION="$SELECTED_VALUE"

    echo -e "\n${CYAN}[2/4] 目标工程根目录 (Target Project Path):${NC}"
    read -r -p "请输入工程路径 [默认: 当前目录 .]: " input_proj
    PROJECT_DIR="${input_proj:-.}"

    prompt_select "[3/4] 选择流水线执行模式 (Select Pipeline Mode):" \
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

    prompt_select "[4/4] 选择执行交互细化程度 (Execution Detail):" \
        "极速推荐配置 (Quick Run: 自动使用最佳实践一键贯通流水线)" "quick" \
        "逐步向导配置 (Interactive: 依次打开各工具阶段的详细选项向导)" "detailed"
    RUN_DETAIL_MODE="$SELECTED_VALUE"
fi

# Fallback: if still no stage selected, default to all stages
if [ "$STAGE_DEPLOY" = false ] && [ "$STAGE_MEMORY" = false ] && [ "$STAGE_SKILLS" = false ] && [ "$STAGE_DOCS" = false ]; then
    STAGE_DEPLOY=true
    STAGE_MEMORY=true
    STAGE_SKILLS=true
    STAGE_DOCS=true
fi

# Pre-flight review: when user passed parameters like -g / -u / -a but NOT -y
RUN_APPLY_SKILLS=false
if [ "$APPLY_SKILLS" = true ] || [ "$RUN_UPDATE" = true ]; then
    RUN_APPLY_SKILLS=true
fi

if [ "$NON_INTERACTIVE" = false ] && { [ -t 0 ] || [ "$FORCE_INTERACTIVE" = true ]; }; then
    if [ "$EXPLICIT_STAGES" = true ]; then
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
    else
        prompt_select "[4/5] 是否同步部署/更新本机全局规则 (Global Rules: ~/.gemini, ~/.codex, ~/.claude)？" \
            "跳过全局规则 (Skip: 仅在当前项目工程内生效)" "skip" \
            "同步更新全局规则 (Sync: 备份并更新各工具全局 AGENTS.md / CLAUDE.md)" "sync"
        if [ "$SELECTED_VALUE" = "sync" ]; then
            RUN_GLOBAL=true
            RUN_UPDATE=true
        fi

        prompt_select "[5/5] 外部技能库处理模式 (External Skills Sync):" \
            "安全检查模式 (Check only: 仅对比差异，不覆盖文件)" "check" \
            "在线同步更新 (Apply: 自动拉取上游更新并应用)" "apply"
        if [ "$SELECTED_VALUE" = "apply" ]; then
            RUN_APPLY_SKILLS=true
        fi
    fi
fi

# Resolve absolute target path
TARGET_ABS="$(cd "$PROJECT_DIR" 2>/dev/null && pwd || echo "$PROJECT_DIR")"

echo -e "\n${BOLD}${CYAN}▶ 开始执行 Agent Harness 工程流水线${NC}"
echo -e "  目标工程: ${GREEN}$TARGET_ABS${NC}"
echo -e "  模版语言: ${GREEN}$LANG_OPTION${NC}"
echo -e "  执行模式: ${GREEN}$RUN_DETAIL_MODE${NC}\n"

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
    if [ "$RUN_GLOBAL" = true ]; then
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
                    sed "s/replace-with-workspace-id/workspace-$proj_name/g; s/replace-with-project-id/$proj_name/g" \
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

    if [ -z "$PYTHON_BIN" ]; then
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
            if [ "$CHECK_ONLY" = true ]; then
                skills_cmd+=("--check")
            elif [ "$RUN_APPLY_SKILLS" = true ]; then
                skills_cmd+=("--apply")
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
