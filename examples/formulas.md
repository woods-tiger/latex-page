# 反函数与参数方程 · 求导公式

> 这个文件用来演示 `latex_page.py` 的输入格式。
> 用 `$$` 独占一行包住公式，每个公式单独一段最稳。

## 一、反函数求导

$$
x'(y)=\frac{dx}{dy}=\frac{1}{y'(x)}
$$

$$
x''(y)=\frac{d}{dy}\left(\frac{1}{y'(x)}\right)=\frac{-y''}{\left[y'(x)\right]^{3}}
$$

> 注意：导数互为倒数，但必须取在**对应点**上。

## 二、参数方程求导

$$
\frac{dy}{dx}=\frac{y'_t}{x'_t}
$$

$$
y''_{xx}=\frac{x'_t\,y''_t-x''_t\,y'_t}{\left(x'_t\right)^{3}}
$$

> 口诀：每对 $x$ 求一次导，就除一次 $\dfrac{dx}{dt}$。

## 三、Leibniz 公式

$$
\left(f_1f_2\cdots f_n\right)^{(k)}=\sum_{i_1+\cdots+i_n=k}\frac{k!}{i_1!\,i_2!\cdots i_n!}\prod_{j=1}^{n}f_j^{(i_j)}
$$

---

## 行内公式示例

由 $(uv)'=u'v+uv'$ 出发，可以归纳出上面的高次导数公式。
