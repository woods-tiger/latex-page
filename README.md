# latex-page：把 LaTeX 搬出自家的渲染器

**一句话**：与其迁就聊天客户端的公式渲染缺陷，不如把公式写进 Markdown、渲染成自己能控制的 HTML 页面——本地 KaTeX、离线可用、可打印。

---

## 解决什么问题

部分 Markdown 客户端（包括 **DeepSeek Harness 的部分版本**）在把 `$$...$$` 交给 KaTeX 之前，会先做一次"取串"：

- 只识别少数几种 `$$` 形状；
- 遇到不认识的形状时，**不会报错**，而是把整块当成普通文本；
- 更糟的是它可能**吞掉后续正文**，于是你看到"前半段正常、后半段全变成红色源码"。

这不是 KaTeX 的问题，也不是你的公式写错了。上游分析见：
[DSH `$$` 解析根因（dsh-tex-block-normalizer）](https://github.com/TianzeLuo/dsh-tex-block-normalizer/blob/main/docs/root-cause.md)

**本工具的立场**：不修别人的渲染器，也不强迫自己记住一堆写法禁忌——把公式搬到本地页面，问题自然消失。

---

## 它做什么

```
notes.md  ──(latex_page.py)──▶  page.html  ──(浏览器/打印)──▶  公式排版
```

- 输入：只含标题、段落、引用、`$$` 公式块的 Markdown
- 输出：一个 HTML 页面，用 KaTeX 渲染公式
- 依赖：Python 3.9+；KaTeX 可选本地或 CDN

---

## 快速开始

```bash
# 1) 直接用 CDN（零安装，需要联网）
python latex_page.py examples/formulas.md -o page.html --title "我的公式页"

# 2) 想离线用：装一份 KaTeX 到当前目录
npm install katex@0.16.11
python latex_page.py examples/formulas.md -o page.html --katex local

# 3) 自动判断（本地有就用本地）
python latex_page.py examples/formulas.md -o page.html --katex auto
```

生成后用浏览器打开 `page.html` 即可；`Ctrl+P` 可以直接打印成 A4。

---

## 输入格式（最小 Markdown 子集）

| 语法 | 渲染结果 |
|---|---|
| `# 标题` | 一级标题 |
| `## 标题` | 二级标题（深底白字） |
| `> 引用` | 灰底提示块 |
| `---` | 分隔线 |
| `$$` 独占一行 … `$$` 独占一行 | 公式块（推荐每个公式单独一段） |
| `$x^2$` | 行内公式 |

**建议**：公式块的开闭 `$$` 各自独占一行，中间不要有空行——这是最不容易出错的形状。

---

## 为什么不做成浏览器扩展 / 插件

- 插件要跟随客户端版本升级，宿主一更新就可能失效；
- 公式页是一个**纯静态文件**，十年后照样能打开；
- 顺带得到一个可打印、可搜索、可版本管理的"个人公式手册"。

---

## 局限

- 只支持最小 Markdown 子集（不解析表格、图片、列表）
- 不处理 `\begin{cases}` 等复杂环境的兼容性问题（KaTeX 本身支持，但需要写对）
- 不负责语法高亮、目录生成

---

## 许可

MIT
