#!/usr/bin/env python3
import re
import sys
import urllib.request
from pathlib import Path

UPSTREAM = "https://raw.githubusercontent.com/celenityy/BadBlock//main/wildcards-star/brave.txt"

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
    # 去掉行内注释（尽量保守，只处理 # 后注释）
    if "#" in s:
        s = s.split("#", 1)[0].strip()
    if not s:
        return None
    # 压缩中间空白
    s = re.sub(r"\s+", "", s)
    return s or None

def add_apex_for_wildcard(dom: str, out: set[str]):
    """
    若 dom 为 '*.a.b' 这种形式，补 'a.b'
    注意：'*.*.x' 这种多层通配不强行补（容易引入错误语义），只补最常见的 '*.' 前缀。
    """
    if dom.startswith("*.") and len(dom) > 2:
        apex = dom[2:]
        # 避免把 '*' 本身这种奇怪情况加进去
        if "*" not in apex and apex:
            out.add(apex)

def main():
    raw = fetch(UPSTREAM)
    lines = raw.splitlines()

    s = set()
    for line in lines:
        dom = normalize_line(line)
        if not dom:
            continue
        s.add(dom)
        add_apex_for_wildcard(dom, s)

    items = sorted(s)

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # 1) text 输出：一行一个
    TXT_OUT.write_text("\n".join(items) + "\n", encoding="utf-8")

    # 2) yaml 输出：payload 列表（behavior: domain + format: yaml 的格式要求）
    # mihomo 的 domain/yaml 规则集一般是 payload: - 'xxx' 这种结构[3](https://en.clash.wiki/premium/rule-providers.html)
    yaml_lines = ["payload:"]
    yaml_lines += [f"  - '{x}'" for x in items]
    YAML_OUT.write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
