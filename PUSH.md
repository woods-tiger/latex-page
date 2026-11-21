# 发布步骤（主人只需点 3 下）

仓库已经在本地提交好了，只差推到 GitHub。

## 第 1 步：在 GitHub 建一个**空仓库**

打开 https://github.com/new

| 字段 | 填什么 |
|---|---|
| Repository name | **latex-page** |
| Description | 把 LaTeX 公式渲染成本地 HTML 页面，绕开客户端数学渲染缺陷 |
| Public / Private | 建议 **Public**（要给别人用） |
| Initialize this repository with | **全部留空**（不要 README / .gitignore / license） |

点 **Create repository**。

## 第 2 步：复制仓库地址

建好后页面上会出现 HTTPS 地址，形如：

```
https://github.com/你的用户名/latex-page.git
```

## 第 3 步：在本目录运行两条命令

打开 PowerShell，执行：

```powershell
cd D:\dsh-latex-page
git remote add origin https://github.com/你的用户名/latex-page.git
git push -u origin master
```

> 如果提示登录：选 **Sign in with your browser**（浏览器授权）最省事。
> Windows 凭据管理器里已经有一条 github 记录，可能会自动通过。

---

## 推完之后可以补的东西（可选）

- **配图**：把 `out-cdn.html` 截一张图，命名 `screenshot.png`，README 顶部加一行：
  ```markdown
  ![效果](screenshot.png)
  ```
- **Topics**：在仓库设置里加 `latex`、`markdown`、`katex`、`offline`
- **Release**：`v0.1.0`，附一个 `latex_page.py` 单文件

---

## 如果 push 报错

| 报错 | 处理 |
|---|---|
| `remote origin already exists` | 先 `git remote remove origin`，再加 |
| `Authentication failed` | 用 Personal Access Token 当密码（GitHub → Settings → Developer settings → Tokens） |
| `master` 与 `main` 不一致 | 改成 `git push -u origin HEAD:main` |
| `rejected (fetch first)` | 说明仓库不是空的，先 `git pull --rebase origin master` |
