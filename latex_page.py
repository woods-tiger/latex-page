#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
latex_page.py —— 把带 LaTeX 的 Markdown 渲染成本地 HTML 公式页

为什么需要它：
    某些聊天/笔记客户端（例如 DeepSeek Harness 的部分版本）在解析 $$...$$
    时只支持特定形状，遇到"开栏同行带内容"等写法会吞掉后文、把源码标红。
    与其反复迁就渲染器，不如把公式搬到一个自己能控制的页面里渲染。

用法：
    python latex_page.py notes.md -o page.html
    python latex_page.py notes.md -o page.html --katex auto
    python latex_page.py notes.md -o page.html --title "我的公式页"

--katex 取值：
    cdn     （默认）从 jsDelivr 加载 KaTeX，零安装，需联网
    local   指向本地 katex 目录（需要先 npm install katex 或下载 dist）
    auto    先看本地目录是否存在，存在用本地，否则用 CDN

输入 Markdown 支持的语法（够用即可）：
    # 一级标题       ## 二级标题       ### 三级标题
    普通段落（自动换行合并）
    $$...$$         独占一行的公式块（推荐每行一个公式）
    $...$           行内公式
    > 引用
    ---             分隔线

退出码：0 成功；1 输入文件不存在或参数错误。
"""
from __future__ import annotations

import argparse
import html
import os
import re
import sys
from pathlib import Path

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{style_block}
</head>
<body>
<main>
{body}
</main>
<script defer src="{katex_js}"></script>
<script defer src="{katex_autorender}"></script>
<script defer src="{katex_path}/contrib/auto-render.min.js" onerror="void 0"></script>
<script>
document.addEventListener("DOMContentLoaded", function () {{
  if (typeof renderMathInElement !== "function") {{
    document.body.insertAdjacentHTML("afterbegin",
      '<p style="color:#c00">KaTeX 未能加载：请检查 --katex 路径或网络。</p>');
    return;
  }}
  renderMathInElement(document.body, {{
    delimiters: [
      {{left: "$$", right: "$$", display: true}},
      {{left: "$", right: "$", display: false}}
    ],
    throwOnError: false
  }});
}});
</script>
</body>
</html>
"""

STYLE = """<style>
  :root { --accent: #a00; --ink: #1a1a1a; --muted: #666; }
  body { margin: 0; background: #fff; color: var(--ink);
         font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
         line-height: 1.75; }
  main { max-width: 920px; margin: 0 auto; padding: 32px 24px 96px; }
  h1 { font-size: 24px; border-bottom: 3px solid var(--accent); padding-bottom: 8px; }
  h2 { font-size: 18px; margin-top: 34px; background: #222; color: #fff;
       padding: 7px 12px; border-radius: 3px; }
  h3 { font-size: 15px; color: var(--accent); margin-top: 22px;
       border-left: 4px solid var(--accent); padding-left: 9px; }
  blockquote { margin: 14px 0; padding: 10px 16px; background: #f7f7f7;
               border-left: 4px solid #ccc; color: var(--muted); }
  hr { border: none; border-top: 1px solid #e5e5e5; margin: 26px 0; }
  .formula { background: #fafafa; border: 1px solid #ececec; border-radius: 6px;
             padding: 8px 14px; margin: 10px 0; overflow-x: auto; }
  code { background:#eee; padding:1px 5px; border-radius:3px; font-size:13px; }
  footer { max-width: 920px; margin: 0 auto; padding: 0 24px 40px;
           color: var(--muted); font-size: 13px; }
  @media print { body { font-size: 11pt; } h2 { background: #eee; color: #000; } }
</style>"""


def inline_fmt(text: str) -> str:
    """行内格式：**粗体**、`代码`（先转义，再替换）"""
    s = html.escape(text)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s

def md_to_html(md: str) -> str:
    """最小 Markdown 转换：标题/段落/引用/分隔线/公式块。"""
    out = []
    lines = md.splitlines()
    i = 0
    para = []

    def flush_para():
        nonlocal para
        if para:
            text = " ".join(x.strip() for x in para if x.strip())
            if text:
                out.append(f"<p>{inline_fmt(text)}</p>")
            para = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 公式块：$$ 独占一行开，$$ 独占一行闭
        if stripped == "$$":
            flush_para()
            i += 1
            buf = []
            while i < len(lines) and lines[i].strip() != "$$":
                buf.append(lines[i])
                i += 1
            expr = "\n".join(buf).strip()
            out.append(f'<div class="formula">$${expr}$$</div>')
            i += 1
            continue

        if not stripped:
            flush_para()
            i += 1
            continue

        if stripped.startswith("#"):
            flush_para()
            level = len(stripped) - len(stripped.lstrip("#"))
            level = min(level, 6)
            text = stripped[level:].strip()
            out.append(f"<h{level}>{inline_fmt(text)}</h{level}>")
            i += 1
            continue

        if stripped in ("---", "***", "___"):
            flush_para()
            out.append("<hr>")
            i += 1
            continue

        if stripped.startswith(">"):
            flush_para()
            out.append(f"<blockquote>{inline_fmt(stripped[1:].strip())}</blockquote>")
            i += 1
            continue

        para.append(line)
        i += 1

    flush_para()
    return "\n".join(out)


def resolve_katex(mode: str, script_dir: Path) -> tuple[str, str]:
    """返回 (katex_js_url, katex_path) —— path 用于拼接 contrib/auto-render.min.js"""
    cdn_path = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist"
    local_candidates = [
        script_dir / "node_modules" / "katex" / "dist",
        script_dir / "katex" / "dist",
    ]

    def local_url() -> str | None:
        for c in local_candidates:
            if (c / "katex.min.js").exists():
                return c.as_uri().rsplit("/", 1)[0]
        return None

    if mode == "local":
        url = local_url()
        if not url:
            print("[warn] 未找到本地 KaTeX，回退到 CDN", file=sys.stderr)
            return f"{cdn_path}/katex.min.js", cdn_path
        return f"{url}/katex.min.js", url

    if mode == "auto":
        url = local_url()
        if url:
            return f"{url}/katex.min.js", url
        return f"{cdn_path}/katex.min.js", cdn_path

    return f"{cdn_path}/katex.min.js", cdn_path


def main() -> int:
    ap = argparse.ArgumentParser(description="把 Markdown + LaTeX 渲染成本地 HTML 公式页")
    ap.add_argument("input", help="输入的 Markdown 文件（UTF-8）")
    ap.add_argument("-o", "--output", default="formula-page.html", help="输出 HTML 路径")
    ap.add_argument("--title", default="公式页", help="页面标题")
    ap.add_argument("--katex", choices=["cdn", "local", "auto"], default="cdn",
                    help="KaTeX 资源来源（默认 cdn）")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.is_file():
        print(f"[error] 找不到输入文件：{src}", file=sys.stderr)
        return 1

    md = src.read_text(encoding="utf-8")
    body = md_to_html(md)
    katex_js, katex_path = resolve_katex(args.katex, src.resolve().parent)

    style_block = STYLE
    if katex_path.startswith("http"):
        style_block += f'\n<link rel="stylesheet" href="{katex_path}/katex.min.css">'
    else:
        style_block += f'\n<link rel="stylesheet" href="{katex_path}/katex.min.css">'

    page = TEMPLATE.format(
        title=html.escape(args.title),
        style_block=style_block,
        body=body,
        katex_js=katex_js,
        katex_autorender=f"{katex_path}/contrib/auto-render.min.js",
        katex_path=katex_path,
    )

    out = Path(args.output)
    out.write_text(page, encoding="utf-8")
    print(f"[ok] 已生成：{out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

