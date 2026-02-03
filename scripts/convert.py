#!/usr/bin/env python3
import re
import urllib.request
from pathlib import Path

UPSTREAM = "https://raw.githubusercontent.com/celenityy/BadBlock/651b835e9ea1d9629a357721f9d4b925411efdce/wildcards-star/brave.txt"

DIST_DIR = Path("dist")
TXT_OUT = DIST_DIR / "brave_domain.txt"
YAML_OUT = DIST_DIR / "brave_domain.yaml"

COMMENT_PREFIXES = ("#", "//", ";")

def fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")

def normalize_line(line: str) -> str | None:
    s = line.strip()
    if not s:
        return None
    for p in COMMENT_PREFIXES:
        if s.startswith(p):
            return None
    # 去掉行内注释（只处理 #）
    if "#" in s:
        s = s.split("#", 1)[0].strip()
    if not s:
        return None
    # 压缩空白
    s = re.sub(r"\s+", "", s)
    return s or None

def convert_star_to_plus(dom: str) -> str:
    """
    仅将最常见的 '*.example.com' 转为 '+.example.com'
    多层通配（如 '*.*.x'）保持原样，避免错误语义
    """
    if dom.startswith("*.") and dom.count("*") == 1:
        return "+." + dom[2:]
    return dom

def main():
    raw = fetch(UPSTREAM)
    lines = raw.splitlines()

    s = set()
    for line in lines:
        dom = normalize_line(line)
        if not dom:
            continue
        dom = convert_star_to_plus(dom)
        s.add(dom)

    items = sorted(s)

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # 1) text 输出
    TXT_OUT.write_text("\n".join(items) + "\n", encoding="utf-8")

    # 2) yaml 输出（mihomo domain/yaml 规则集）
    yaml_lines = ["payload:"]
    yaml_lines += [f"  - '{x}'" for x in items]
    YAML_OUT.write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
