# Rendering Spec（渲染规范）

所有 `engineering-docs` 模板输出必须遵循本规范，保证不同 Agent 产出的文档
**视觉格式一致**：标题字号、段落格式、字体、表格、代码块。

> 设计参考：中文公文/技术文档通用排版惯例，兼容 pandoc → Word 转换。

---

## 一、标题层级

| 层级 | Markdown | 中文字体 | 英文字体 | 字号 | 加粗 | 段前/段后 |
|---|---|---|---|---|---|---|
| H1 | `#` | 黑体 | Times New Roman | 小二（18pt） | ✅ | 24pt / 24pt |
| H2 | `##` | 黑体 | Times New Roman | 三号（16pt） | ✅ | 12pt / 12pt |
| H3 | `###` | 黑体 | Times New Roman | 小三（15pt） | ✅ | 6pt / 6pt |
| H4 | `####` | 黑体 | Times New Roman | 小四（12pt） | ✅ | 6pt / 6pt |

- H1 仅用于文档标题（一个文档一个 H1）。
- 章节编号用 `1.` `1.1` `1.1.1` 数字编号，不用中文"一、"（便于交叉引用）。

## 二、段落格式

| 项目 | 规范 |
|---|---|
| 正文字体 | 中文宋体，英文 Times New Roman，小四（12pt） |
| 行距 | 1.5 倍 |
| 首行缩进 | 2 字符 |
| 段前/段后 | 0pt（靠空行分段，Markdown 原生空行即可） |
| 对齐 | 两端对齐 |

## 三、表格

- 表头加粗，底色浅灰（#F2F2F2）。
- 单元格：宋体/ Times New Roman，五号（10.5pt）。
- 表格标题置于表格上方：`表 1-1 xxx`，小四加粗居中。

## 四、代码块 / 引用

- 代码块：等宽字体（Consolas / Courier New），小五（9pt），浅灰底。
- 行内代码：等宽字体，浅灰底。
- 引用块（`>`）：左侧 6pt 粗边框，用于提示/注意。

## 五、图片与公式

- 图片标题置于图片下方：`图 1-1 xxx`，小四居中。
- 图片居中，宽度不超过版心。
- 公式用 LaTeX 行内 `$...$` / 独立 `$$...$$`，编号右对齐 `(1-1)`。

## 六、页眉页脚（Word 交付时）

- 页眉：文档标题，宋体小五，居中。
- 页脚：页码 `第 X 页 共 Y 页`，宋体小五，居中。

---

## 交付为 Word

Markdown 定稿后，用 pandoc 转换为 Word：

```bash
# 1. 一键获取中文 Word 参考模板（只需一次）
./scripts/fetch-word-template.sh
#    （下载自 Achuan-2/pandoc_docx_template，社区验证的中文排版）

# 2. 转换
pandoc input.md -o output.docx --reference-doc template.docx

# 3. 如需处理 HTML 标签/图片标题/字体颜色，加 lua 过滤器
pandoc input.md -t html | pandoc -f html -o output.docx \
  --reference-doc template.docx --lua-filter markdown-to-docx.lua
```

> 参考模板只需保证**样式名**与本规范对应（Heading 1-4、正文、表格等），
> 具体字号已在模板中按上表设置好，转换时自动应用。

## 严格模板场景

如需**严格套用机构固定 Word 模板**（如学位论文、公文格式），
超出 pandoc 能力时，可参考 `zouchenzhen/docx-template-translator-skill`
（Apache-2.0）的工作流：inspect 模板 → 生成专用后处理脚本 → Word 定稿。
