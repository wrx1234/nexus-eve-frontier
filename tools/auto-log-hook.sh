#!/bin/bash
# Git pre-commit hook — 自动从 git diff 中提取变更并记录到 AI log
# 安装: cp tools/auto-log-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

PROJECT_DIR="$(git rev-parse --show-toplevel)"
LOGGER="$PROJECT_DIR/tools/ai-logger.py"

# 获取本次 commit 的变更文件
CHANGED=$(git diff --cached --name-only --diff-filter=ACMR | head -10)
if [ -z "$CHANGED" ]; then
    exit 0
fi

# 获取 commit message (从 MERGE_MSG 或等 commit 时传入)
MSG=$(cat "$PROJECT_DIR/.git/COMMIT_EDITMSG" 2>/dev/null || echo "code update")

# 自动分类
CATEGORY="code"
echo "$CHANGED" | grep -q "contracts/" && CATEGORY="code"
echo "$CHANGED" | grep -q "RESEARCH\|docs/" && CATEGORY="research"
echo "$CHANGED" | grep -q "test" && CATEGORY="test"
echo "$CHANGED" | grep -q "README\|PROGRESS\|\.md" && CATEGORY="docs"
echo "$CHANGED" | grep -q "DESIGN\|ARCHITECTURE" && CATEGORY="design"

# 记录
FILES_LIST=$(echo "$CHANGED" | tr '\n' ', ')
python3 "$LOGGER" log "Commit: $MSG | Files: $FILES_LIST" \
    --category "$CATEGORY" \
    --phase development \
    -r "Auto-logged from git commit" 2>/dev/null

# 自动重新生成 AI_DISCLOSURE.md
python3 "$LOGGER" summary 2>/dev/null
git add "$PROJECT_DIR/AI_DISCLOSURE.md" "$PROJECT_DIR/ai-logs/prompts.jsonl" 2>/dev/null

exit 0
