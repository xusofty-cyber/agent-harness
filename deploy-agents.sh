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
    echo "  $0 <项目根目录路径> [--global|-g] [--update|-u] [--initialize|-i] [--directory <相对目录>] [--check|-k]"
    echo "  $0 --global|-g [--update|-u]   # 初始化全局配置；--update 先备份再覆盖已有规则"
    echo ""
    echo -e "${CYAN}参数说明 (Parameters):${NC}"
    echo "  <项目根目录路径>   目标项目所在的相对路径或绝对路径。"
    echo "  --global, -g       初始化 Claude、Antigravity 2.0/CLI/IDE、Codex 用户全局规则。"
    echo "  --update, -u       更新模板仓库；与 --global 一起使用时，先备份再覆盖全局规则。"
    echo "  --initialize, -i 识别项目事实，生成 AGENTS.md 并列出待确认项。"
    echo "  --directory       与 --initialize 配合，为现有子目录生成目录级 AGENTS.md。"
    echo "  --check, -k       检查项目级规则中的初始化占位项；可搭配 --directory 检查模块规则。"
    echo "  --comet-init       若系统中已安装 comet CLI，自动在目标项目中运行 comet init。"
    echo "  --ai-memory-init, -m 初始化项目 .ai-memory.toml 并接入跨工具记忆 (ai-memory)。"
    echo ""
    echo -e "${CYAN}示例 (Examples):${NC}"
    echo "  $0 /path/to/my-project"
    echo "  $0 /path/to/my-project --global --update"
    echo "  $0 /path/to/my-project --comet-init"
    echo "  $0 /path/to/my-project --ai-memory-init"
    echo "  $0 --global --update"
    exit 1
}

# Parse arguments
TARGET_PROJECT_ARG=""
DEPLOY_GLOBAL=false
DO_UPDATE=false
DO_COMET_INIT=false
DO_AI_MEMORY_INIT=false
DO_INITIALIZE=false
DO_CHECK=false
DIRECTORY_PATH=""

args=("$@")
arg_index=0
while [ "$arg_index" -lt "$#" ]; do
    arg="${args[$arg_index]}"
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
        --ai-memory-init|-m)
            DO_AI_MEMORY_INIT=true
            ;;
        --initialize|-i)
            DO_INITIALIZE=true
            ;;
        --check|-k)
            DO_CHECK=true
            ;;
        --directory)
            arg_index=$((arg_index + 1))
            if [ "$arg_index" -ge "$#" ]; then echo "[!] --directory requires a relative path" >&2; exit 2; fi
            DIRECTORY_PATH="${args[$arg_index]}"
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
    arg_index=$((arg_index + 1))
done

if [ -n "$DIRECTORY_PATH" ] && [ "$DO_INITIALIZE" != true ] && [ "$DO_CHECK" != true ]; then echo "[!] --directory requires --initialize or --check" >&2; exit 2; fi
if { [ "$DO_INITIALIZE" = true ] || [ "$DO_CHECK" = true ]; } && [ -z "$TARGET_PROJECT_ARG" ]; then echo "[!] --initialize/--check requires a project path" >&2; exit 2; fi
if [ "$DO_CHECK" = true ] && [ "$DEPLOY_GLOBAL" = true ]; then echo "[!] --check cannot be combined with --global" >&2; exit 2; fi

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
DIRECTORY_TEMPLATE="${SCRIPT_DIR}/Directory AGENTS.md"
SOURCE_RULES_DIR="${SCRIPT_DIR}/.agents/rules"
SOURCE_SKILLS_DIR="${SCRIPT_DIR}/.agents/skills"
SOURCE_SKILLS_LOCK="${SCRIPT_DIR}/skills-lock.json"
SOURCE_CLAUDE_SETTINGS="${SCRIPT_DIR}/.claude/settings.json"
SOURCE_AI_MEMORY_EXAMPLE="${SCRIPT_DIR}/.ai-memory.toml.example"

# Back up managed target paths before an explicit update replaces them.
backup_path() {
    local path="$1"
    if [ -e "$path" ] || [ -L "$path" ]; then
        cp -a "$path" "${path}.bak.$(date +%Y%m%d%H%M%S)"
    fi
}

backup_global_rule() {
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

    if command -v ocr >/dev/null 2>&1; then
        echo -e "  ${GREEN}[√] 已检测到 Open Code Review CLI (ocr)：可启用 open-code-review 技能的 Tier A 委托评审。${NC}"
    else
        echo "  Open Code Review CLI (ocr) 未安装。open-code-review 技能仍可用（Tier B 方法论模式），安装后可启用零 Token 开销的委托评审。"
        if prompt_yes_no "现在安装 Open Code Review CLI？"; then
            if npm install -g @alibaba-group/open-code-review; then
                echo -e "  ${GREEN}[√] ocr 已安装。委托模式无需配置 LLM Key，由当前 Agent 直接推理。${NC}"
            else
                echo "  [!] ocr 安装失败。可手动执行：npm install -g @alibaba-group/open-code-review"
            fi
        else
            echo "  安装命令：npm install -g @alibaba-group/open-code-review"
        fi
    fi
}

init_guidance() {
    local template="$1" output="$2" scope="$3" root="$4"
    local project_name="" repository_url="" default_branch="" language="" package_manager="" ci_path="" purpose="" owners="" module_name="" directory_path="" responsibility=""
    local readme_summary="" manifests=() locks=() pending="" key value content status tmp item file label
    local install_suggestion="" dev_suggestion="" build_suggestion="" unit_test_suggestion="" targeted_test_suggestion="" integration_suggestion="" lint_suggestion="" format_suggestion="" type_check_suggestion="" migration_suggestion="" local_test_suggestion="" local_lint_suggestion="" framework_suggestion="" store_suggestion="" frameworks="" stores="" script_report="" report_type="" report_value="" run_prefix="npm run" suggestion="" python_cmd="" local_manager=""
    project_name="$(basename "$root")"
    module_name="$project_name"
    if [ "$scope" = project ]; then
        repository_url="$(git -C "$root" remote get-url origin 2>/dev/null || true)"
        if [[ "$repository_url" == *://*@* ]]; then repository_url=""; fi
        default_branch="$(git -C "$root" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)"
        default_branch="${default_branch#origin/}"
        for item in 'package.json:JavaScript/TypeScript (package.json; runtime version to confirm)' 'pyproject.toml:Python (pyproject.toml; runtime version to confirm)' 'Cargo.toml:Rust (Cargo.toml)' 'go.mod:Go (go.mod)' 'CMakeLists.txt:C/C++ (CMakeLists.txt)' ; do
            file="${item%%:*}"; label="${item#*:}"
            if [ -f "$root/$file" ]; then manifests+=("$label"); fi
        done
        for item in 'pnpm-lock.yaml:pnpm' 'yarn.lock:Yarn' 'package-lock.json:npm' 'uv.lock:uv' 'poetry.lock:Poetry' 'Cargo.lock:Cargo' 'go.sum:Go modules' 'Pipfile.lock:Pipenv'; do
            file="${item%%:*}"; label="${item#*:}"
            if [ -f "$root/$file" ]; then locks+=("$label"); fi
        done
        for file in "$root"/*.csproj; do if [ -f "$file" ]; then manifests+=(".NET (project file)"); break; fi; done
        language="$(IFS='; '; echo "${manifests[*]}")"
        package_manager="$(IFS=', '; echo "${locks[*]}")"
        if [ -d "$root/.github/workflows" ]; then
            for file in "$root/.github/workflows"/*.yml "$root/.github/workflows"/*.yaml; do
                if [ -f "$file" ]; then ci_path="${ci_path:+$ci_path, }.github/workflows/$(basename "$file")"; fi
            done
        fi
        for file in .gitlab-ci.yml Jenkinsfile azure-pipelines.yml; do if [ -f "$root/$file" ]; then ci_path="${ci_path:+$ci_path, }$file"; fi; done
        if [ -f "$root/README.md" ]; then
            readme_summary="$(awk 'NF && $0 !~ /^[[:space:]]*#/ {print; exit}' "$root/README.md")"
        fi
        if [ -t 0 ] && [ -r /dev/tty ]; then
            if [ -n "$readme_summary" ]; then
                read -r -p "项目用途（留空接受 README 摘要：$readme_summary）: " purpose </dev/tty
                purpose="${purpose:-$readme_summary}"
            else
                read -r -p "项目用途（一句话；留空标记待确认）: " purpose </dev/tty
            fi
            read -r -p "核心维护者（团队/账号；留空标记待确认）: " owners </dev/tty
        fi
    else
        directory_path="${root#"$TARGET_PROJECT_DIR"/}"
        directory_path="${directory_path//\\//}"
        if [ -t 0 ] && [ -r /dev/tty ]; then read -r -p "目录职责（一句话；留空交给 Agent 检查）: " responsibility </dev/tty; fi
    fi

    if command -v python3 >/dev/null 2>&1 && python3 -c 'import json' >/dev/null 2>&1; then python_cmd=python3
    elif command -v python >/dev/null 2>&1 && python -c 'import json' >/dev/null 2>&1; then python_cmd=python
    fi
    if [ -f "$root/package.json" ] && [ -n "$python_cmd" ]; then
        script_report="$("$python_cmd" - "$root/package.json" 2>/dev/null <<'PY'
import json, sys
try:
    with open(sys.argv[1], encoding='utf-8') as source: data = json.load(source)
except Exception:
    raise SystemExit(0)
manager = (data.get('packageManager') or '').split('@')[0]
if manager: print('manager\t' + manager)
scripts = data.get('scripts') or {}
for name in ('dev','build','test','test:unit','test:e2e','test:integration','e2e','lint','format','fmt','typecheck','type-check','db:migrate','migrate'):
    if name in scripts: print('script\t' + name)
deps = set((data.get('dependencies') or {})) | set((data.get('devDependencies') or {}))
for package, label in (('next','Next.js'),('react','React'),('vue','Vue'),('@angular/core','Angular'),('express','Express'),('fastify','Fastify')):
    if package in deps: print('framework\t' + label)
for package in ('pg','mysql','mysql2','sqlite3','better-sqlite3','mongoose','prisma','@prisma/client','redis','ioredis'):
    if package in deps: print('store\t' + package)
PY
)" || script_report=""
    elif [ -f "$root/package.json" ] && command -v node >/dev/null 2>&1; then
        script_report="$(node -e 'const p=require(process.argv[1]); const m=(p.packageManager||"").split("@")[0]; if(m) console.log("manager\t"+m); for (const n of ["dev","build","test","test:unit","test:e2e","test:integration","e2e","lint","format","fmt","typecheck","type-check","db:migrate","migrate"]) if (p.scripts?.[n] !== undefined) console.log("script\t"+n); const d={...(p.dependencies||{}),...(p.devDependencies||{})}; for (const [n,l] of [["next","Next.js"],["react","React"],["vue","Vue"],["@angular/core","Angular"],["express","Express"],["fastify","Fastify"]]) if(d[n]) console.log("framework\t"+l); for(const n of ["pg","mysql","mysql2","sqlite3","better-sqlite3","mongoose","prisma","@prisma/client","redis","ioredis"]) if(d[n]) console.log("store\t"+n)' "$root/package.json" 2>/dev/null)" || script_report=""
    fi
    case "$package_manager" in pnpm*) run_prefix='pnpm run'; install_suggestion='建议确认：pnpm install --frozen-lockfile（根据锁文件推导）' ;; Yarn*) run_prefix='yarn run'; install_suggestion='建议确认：yarn install --immutable（根据锁文件推导）' ;; npm*) install_suggestion='建议确认：npm ci（根据锁文件推导）' ;; esac
    while IFS="$(printf '\t')" read -r report_type report_value; do
        [ -n "$report_type" ] || continue
        report_value="${report_value%$'\r'}"
        case "$report_type" in
            manager)
                local_manager="$report_value"
                case "$local_manager" in
                    pnpm) run_prefix='pnpm run' ; [ "$scope" = project ] && { package_manager='建议确认：pnpm（package.json packageManager）'; install_suggestion='建议确认：pnpm install --frozen-lockfile（packageManager 字段）'; } ;;
                    yarn) run_prefix='yarn run' ; [ "$scope" = project ] && { package_manager='建议确认：yarn（package.json packageManager）'; install_suggestion='建议确认：yarn install --immutable（packageManager 字段）'; } ;;
                    npm) run_prefix='npm run' ; [ "$scope" = project ] && { package_manager='建议确认：npm（package.json packageManager）'; install_suggestion='建议确认：npm ci（packageManager 字段）'; } ;;
                esac
                ;;
            script)
                suggestion="建议确认：$run_prefix $report_value（package.json scripts.$report_value）"
                case "$report_value" in
                    dev) dev_suggestion="$suggestion" ;;
                    build) build_suggestion="$suggestion" ;;
                    test|test:unit) unit_test_suggestion="$suggestion"; targeted_test_suggestion="建议确认：$run_prefix $report_value -- <test-path>（需核验参数）"; local_test_suggestion="$suggestion" ;;
                    test:e2e|test:integration|e2e) integration_suggestion="$suggestion" ;;
                    lint) lint_suggestion="$suggestion"; local_lint_suggestion="$suggestion" ;;
                    format|fmt) format_suggestion="$suggestion" ;;
                    typecheck|type-check) type_check_suggestion="$suggestion" ;;
                    db:migrate|migrate) migration_suggestion="$suggestion" ;;
                esac
                ;;
            framework) frameworks="${frameworks:+$frameworks, }$report_value" ;;
            store) stores="${stores:+$stores, }$report_value" ;;
        esac
    done <<EOF
$script_report
EOF
    if [ -n "$frameworks" ]; then framework_suggestion="建议确认：$frameworks（package.json dependencies）"; fi
    if [ -n "$stores" ]; then store_suggestion="建议确认：$stores（依赖清单；实际运行配置需复核）"; fi

    content="$(cat "$template")"
    while [[ "$content" =~ \<([A-Z][A-Z0-9_]*)\> ]]; do
        key="${BASH_REMATCH[1]}"; value=""
        case "$key" in
            PROJECT_NAME) value="$project_name" ;;
            REPOSITORY_URL) value="$repository_url" ;;
            DEFAULT_BRANCH) value="$default_branch" ;;
            LANGUAGE_AND_VERSION) value="$language" ;;
            PACKAGE_MANAGER) value="$package_manager" ;;
            INSTALL_COMMAND) value="$install_suggestion" ;;
            DEV_COMMAND) value="$dev_suggestion" ;;
            BUILD_COMMAND) value="$build_suggestion" ;;
            UNIT_TEST_COMMAND) value="$unit_test_suggestion" ;;
            TARGETED_TEST_COMMAND) value="$targeted_test_suggestion" ;;
            INTEGRATION_TEST_COMMAND) value="$integration_suggestion" ;;
            LINT_COMMAND) value="$lint_suggestion" ;;
            FORMAT_COMMAND) value="$format_suggestion" ;;
            TYPE_CHECK_COMMAND) value="$type_check_suggestion" ;;
            MIGRATION_COMMAND) value="$migration_suggestion" ;;
            FRAMEWORK) value="$framework_suggestion" ;;
            DATABASE_AND_CACHE) value="$store_suggestion" ;;
            CI_PATH) value="$ci_path" ;;
            PROJECT_PURPOSE) value="$purpose" ;;
            OWNERS) value="$owners" ;;
            MODULE_NAME) value="$module_name" ;;
            DIRECTORY_PATH) value="$directory_path" ;;
            RESPONSIBILITY) value="$responsibility" ;;
            LOCAL_TEST_COMMAND) value="$local_test_suggestion" ;;
            LOCAL_LINT_COMMAND) value="$local_lint_suggestion" ;;
        esac
        if [ -z "$value" ] || [[ "$value" == 待* ]] || [[ "$value" == 建议确认：* ]]; then
            case ",$pending," in *",$key,"*) ;; *) pending="${pending:+$pending, }$key" ;; esac
        fi
        if [ -z "$value" ]; then
            value="待确认（$key）"
        fi
        content="${content//"<$key>"/"$value"}"
    done
    if [ -n "$pending" ]; then
        status="## 初始化待确认项\n\n"
        IFS=', ' read -r -a pending_items <<< "$pending"
        for pending_item in "${pending_items[@]}"; do status+="- $pending_item\n"; done
    else
        status="## 初始化状态\n\n自动识别字段已填充；请复核后使用。"
    fi
    tmp="$(mktemp "${output}.tmp.XXXXXX")"
    { printf '%b\n\n<!-- Generated by deploy-agents.sh --initialize; review before use. -->\n\n' "$status"; printf '%s\n' "$content"; } > "$tmp"
    mv "$tmp" "$output"
    echo "  [√] 已初始化规则文件: $output"
    if [ -n "$pending" ]; then
        echo "  [i] 待 Agent 检查或人工确认: $pending"
        echo "  [下一步] 请让当前编码 Agent 检查此文件待确认项；仅填入有仓库证据的信息，对业务定位、维护者和模块边界先询问，不要猜测。"
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
if { [ "$DO_INITIALIZE" = true ] || [ "$DO_CHECK" = true ]; } && [ -n "$DIRECTORY_PATH" ]; then
    case "$DIRECTORY_PATH" in /*|../*|*/../*|*/..) echo "[!] --directory must be a relative path inside the project" >&2; exit 2 ;; esac
    DIRECTORY_ROOT="$(cd "${TARGET_PROJECT_DIR}/${DIRECTORY_PATH}" 2>/dev/null && pwd -P)" || { echo "[!] Directory does not exist: $DIRECTORY_PATH" >&2; exit 1; }
    PROJECT_ROOT_REAL="$(cd "$TARGET_PROJECT_DIR" && pwd -P)"
    case "$DIRECTORY_ROOT" in "$PROJECT_ROOT_REAL"/*) ;; *) echo "[!] --directory resolves outside the project" >&2; exit 2 ;; esac
    if [ -f "${DIRECTORY_ROOT}/AGENTS.md" ] && [ -e "${DIRECTORY_ROOT}/AGENTS.generated.md" ]; then echo "[!] Existing generated directory guidance would be overwritten." >&2; exit 1; fi
fi
if [ "$DO_INITIALIZE" = true ] && [ -f "${TARGET_PROJECT_DIR}/AGENTS.md" ] && [ -e "${TARGET_PROJECT_DIR}/AGENTS.generated.md" ]; then echo "[!] Existing generated project guidance would be overwritten." >&2; exit 1; fi
if [ "$DO_CHECK" = true ]; then
    check_failed=false
    checked_count=0
    check_files=("${TARGET_PROJECT_DIR}/AGENTS.md" "${TARGET_PROJECT_DIR}/AGENTS.generated.md")
    if [ -n "$DIRECTORY_PATH" ]; then check_files+=("${DIRECTORY_ROOT}/AGENTS.md" "${DIRECTORY_ROOT}/AGENTS.generated.md"); fi
    for check_file in "${check_files[@]}"; do
        if [ ! -f "$check_file" ]; then continue; fi
        checked_count=$((checked_count + 1))
        if grep -nE '<[A-Z][A-Z0-9_]*>|待确认（[A-Z][A-Z0-9_]*）|待用户确认|待 Agent 检查|建议确认：' "$check_file"; then
            echo "[!] Unresolved initialization fields in: $check_file"
            check_failed=true
        else
            echo "[√] No initialization placeholders: $check_file"
        fi
    done
    if [ "$checked_count" -eq 0 ]; then echo "[!] No AGENTS.md or AGENTS.generated.md found to check."; check_failed=true; fi
    [ "$check_failed" = false ] || exit 1
    exit 0
fi

echo -e "\n${CYAN}==================================================${NC}"
echo -e "${CYAN} 目标项目路径: ${TARGET_PROJECT_DIR}${NC}"
echo -e "${CYAN}==================================================${NC}"

# ==============================================================================
# 3. Deploy Project AGENTS.md & Bridges
# ==============================================================================
echo -e "\n${YELLOW}>>> [2/3] 正在部署项目级规则与跨工具桥接...${NC}"

TARGET_AGENTS="${TARGET_PROJECT_DIR}/AGENTS.md"
HAD_PROJECT_AGENTS=false
if [ -f "$TARGET_AGENTS" ]; then HAD_PROJECT_AGENTS=true; fi
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

if [ "$DO_INITIALIZE" = true ]; then
    PROJECT_OUTPUT="$TARGET_AGENTS"
    if [ "$HAD_PROJECT_AGENTS" = true ]; then PROJECT_OUTPUT="${TARGET_PROJECT_DIR}/AGENTS.generated.md"; fi
    if [ "$HAD_PROJECT_AGENTS" = true ] && [ -e "$PROJECT_OUTPUT" ]; then echo "[!] Refusing to overwrite existing generated guidance: $PROJECT_OUTPUT" >&2; exit 1; fi
    init_guidance "$PROJECT_TEMPLATE" "$PROJECT_OUTPUT" project "$TARGET_PROJECT_DIR"

    if [ -n "$DIRECTORY_PATH" ]; then
        if [ ! -f "$DIRECTORY_TEMPLATE" ]; then echo "[!] Directory template not found: $DIRECTORY_TEMPLATE" >&2; exit 1; fi
        DIRECTORY_AGENTS="${DIRECTORY_ROOT}/AGENTS.md"
        DIRECTORY_OUTPUT="$DIRECTORY_AGENTS"
        if [ -f "$DIRECTORY_AGENTS" ]; then DIRECTORY_OUTPUT="${DIRECTORY_ROOT}/AGENTS.generated.md"; fi
        if [ -f "$DIRECTORY_AGENTS" ] && [ -e "$DIRECTORY_OUTPUT" ]; then echo "[!] Refusing to overwrite existing generated guidance: $DIRECTORY_OUTPUT" >&2; exit 1; fi
        init_guidance "$DIRECTORY_TEMPLATE" "$DIRECTORY_OUTPUT" directory "$DIRECTORY_ROOT"
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

# Sync .ai-memory.toml.example
if [ -f "${SOURCE_AI_MEMORY_EXAMPLE}" ]; then
    TARGET_AI_MEMORY_EXAMPLE="${TARGET_PROJECT_DIR}/.ai-memory.toml.example"
    TARGET_AI_MEMORY="${TARGET_PROJECT_DIR}/.ai-memory.toml"
    if [ ! -f "${TARGET_AI_MEMORY}" ] && [ ! -f "${TARGET_AI_MEMORY_EXAMPLE}" ]; then
        cp "${SOURCE_AI_MEMORY_EXAMPLE}" "${TARGET_AI_MEMORY_EXAMPLE}"
        echo -e "  ${GREEN}[√] 已同步 .ai-memory.toml.example 供参照${NC}"
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
# 8. Initialize Living Documentation Scaffold (docs/{specs,architecture,reference,guides,adr})
# ==============================================================================
# living-doc-scaffold
TARGET_DOCS_DIR="${TARGET_PROJECT_DIR}/docs"
for doc_subdir in specs architecture reference guides adr; do
    if [ ! -d "${TARGET_DOCS_DIR}/${doc_subdir}" ]; then
        mkdir -p "${TARGET_DOCS_DIR}/${doc_subdir}"
    fi
done
echo -e "  ${GREEN}[√] 已就绪文档骨架目录: docs/{specs,architecture,reference,guides,adr}${NC}"

# ==============================================================================
# 9. Optional Comet CLI Init (--comet-init)
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

# ==============================================================================
# 10. Optional ai-memory Init (--ai-memory-init)
# ==============================================================================
if [ "$DO_AI_MEMORY_INIT" = true ]; then
    TARGET_AI_MEMORY="${TARGET_PROJECT_DIR}/.ai-memory.toml"
    if [ -f "${TARGET_AI_MEMORY}" ]; then
        echo "  [i] 目标项目已存在 .ai-memory.toml，保持现有配置。"
    else
        echo -e "\n${YELLOW}>>> 正在初始化目标项目 .ai-memory.toml...${NC}"
        proj_name="$(basename "${TARGET_PROJECT_DIR}")"
        parent_dir="$(dirname "${TARGET_PROJECT_DIR}")"
        ws_name="$(basename "${parent_dir}")"
        if [ -z "$ws_name" ] || [ "$ws_name" = "/" ] || [ "$ws_name" = "." ]; then
            ws_name="$proj_name"
        fi
        cat <<EOF > "${TARGET_AI_MEMORY}"
# Auto-generated by deploy-agents --ai-memory-init
workspace = "${ws_name}"
project = "${proj_name}"

[capture]
ignore_paths = [
  "**/.env*",
  "**/*.pem",
  "**/*.key",
  "**/secrets/**",
  "**/credentials/**",
  "**/private/**",
]
EOF
        echo -e "  ${GREEN}[√] 已生成 .ai-memory.toml (workspace: ${ws_name}, project: ${proj_name})${NC}"
    fi

    if command -v ai-memory >/dev/null 2>&1; then
        echo -e "  ${GREEN}[√] 检测到系统已安装 ai-memory CLI。${NC}"
    else
        echo -e "  ${YELLOW}[!] 指定了 --ai-memory-init，但在系统 PATH 中未找到 ai-memory 工具。${NC}"
        echo -e "      可通过官方指南安装 ai-memory，并在项目根目录运行 setup-ai-memory.sh 接入 Agent。"
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
elif command -v ai-memory >/dev/null 2>&1; then
    echo -e "\n${YELLOW}[TIP] 检测到 ai-memory CLI。使用 -m / --ai-memory-init 或配置 .ai-memory.toml 即可启用跨工具项目记忆。${NC}"
else
    echo -e "\n${NC}[i] 规则与技能文件已部署；是否自动加载取决于宿主工具。${NC}"
fi
echo -e "${GREEN}==================================================${NC}"
