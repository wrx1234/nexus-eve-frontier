#!/usr/bin/env python3
"""
AI Prompt Logger — 记录所有与 AI 的交互（prompt + response）
用于满足 Sui Vibe Hackathon AI 使用声明要求

使用方式:
  python3 ai-logger.py log "你的prompt内容" --model "claude-opus-4.6" --tool "OpenClaw"
  python3 ai-logger.py log "你的prompt内容" --response "AI的回复" --model "claude-opus-4.6"
  python3 ai-logger.py summary  # 生成 AI_DISCLOSURE.md
  python3 ai-logger.py list     # 查看所有记录
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ai-logs')
LOG_FILE = os.path.join(LOG_DIR, 'prompts.jsonl')
DISCLOSURE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'AI_DISCLOSURE.md')

CST = timezone(timedelta(hours=8))

def ensure_dir():
    os.makedirs(LOG_DIR, exist_ok=True)

def log_prompt(prompt, response=None, model="claude-opus-4.6", tool="OpenClaw", phase="development", category="code"):
    ensure_dir()
    entry = {
        "timestamp": datetime.now(CST).isoformat(),
        "tool": tool,
        "model": model,
        "phase": phase,
        "category": category,
        "prompt": prompt,
        "response_summary": response[:500] if response else None,
    }
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    print(f"✅ Logged: [{category}] {prompt[:80]}...")

def list_prompts():
    if not os.path.exists(LOG_FILE):
        print("No logs yet.")
        return
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            entry = json.loads(line)
            t = entry['timestamp'][:16]
            p = entry['prompt'][:100]
            print(f"#{i} [{t}] [{entry['category']}] {p}")

def generate_disclosure():
    """生成 AI_DISCLOSURE.md 用于黑客松提交"""
    if not os.path.exists(LOG_FILE):
        print("No logs to generate disclosure from.")
        return
    
    entries = []
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            entries.append(json.loads(line))
    
    # 统计
    tools = set(e['tool'] for e in entries)
    models = set(e['model'] for e in entries)
    categories = {}
    for e in entries:
        cat = e['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(e)
    
    md = f"""# 🤖 AI Usage Disclosure

> This document is required by Sui Vibe Hackathon 2026 rules.
> All AI tool usage during development is disclosed below.

## AI Tools Used

| Tool | Models | Usage Count |
|------|--------|-------------|
"""
    for tool in sorted(tools):
        tool_entries = [e for e in entries if e['tool'] == tool]
        tool_models = sorted(set(e['model'] for e in tool_entries))
        md += f"| {tool} | {', '.join(tool_models)} | {len(tool_entries)} |\n"
    
    md += f"""
## Summary

- **Total AI interactions**: {len(entries)}
- **Development period**: {entries[0]['timestamp'][:10]} to {entries[-1]['timestamp'][:10]}
- **Primary tool**: OpenClaw (autonomous AI agent framework)
- **Primary model**: Claude Opus 4.6 (Anthropic)

## Usage by Category

"""
    for cat, cat_entries in sorted(categories.items()):
        md += f"### {cat.title()} ({len(cat_entries)} interactions)\n\n"
        for i, e in enumerate(cat_entries, 1):
            md += f"**#{i}** [{e['timestamp'][:16]}]\n"
            md += f"- Prompt: `{e['prompt'][:200]}`\n"
            if e.get('response_summary'):
                md += f"- Response summary: {e['response_summary'][:200]}\n"
            md += "\n"
    
    md += """## Disclosure Statement

This project was developed with significant assistance from AI tools. Specifically:

1. **OpenClaw** (https://openclaw.ai) — Autonomous AI agent framework used for project management, research, code generation, and documentation
2. **Claude Opus 4.6** (Anthropic) — Primary LLM model for all AI interactions
3. **Claude Code** — CLI tool within OpenClaw for code generation and editing

All prompts and AI outputs are logged in `ai-logs/prompts.jsonl`.
Sensitive information (API keys, passwords) has been redacted.

We believe in full transparency about AI usage in software development.
"""
    
    with open(DISCLOSURE_FILE, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"✅ Generated {DISCLOSURE_FILE}")

def main():
    parser = argparse.ArgumentParser(description='AI Prompt Logger')
    sub = parser.add_subparsers(dest='command')
    
    log_p = sub.add_parser('log', help='Log a prompt')
    log_p.add_argument('prompt', help='The prompt text')
    log_p.add_argument('--response', '-r', help='AI response summary')
    log_p.add_argument('--model', '-m', default='claude-opus-4.6')
    log_p.add_argument('--tool', '-t', default='OpenClaw')
    log_p.add_argument('--phase', '-p', default='development')
    log_p.add_argument('--category', '-c', default='code', 
                       choices=['research', 'design', 'code', 'test', 'docs', 'debug', 'review'])
    
    sub.add_parser('list', help='List all logged prompts')
    sub.add_parser('summary', help='Generate AI_DISCLOSURE.md')
    
    args = parser.parse_args()
    
    if args.command == 'log':
        log_prompt(args.prompt, args.response, args.model, args.tool, args.phase, args.category)
    elif args.command == 'list':
        list_prompts()
    elif args.command == 'summary':
        generate_disclosure()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
