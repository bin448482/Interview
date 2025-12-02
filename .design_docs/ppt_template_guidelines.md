# PPT 模板选择与复用指南（Pandoc + WSL 场景）

> 目的：下次需要把 `.md` 架构文档（如 `ngse_architecture_en.md`）转换成 PPT 时，能快速找到/复用合适的免费模板。

---

## 1. 推荐免费模板来源

### 1.1 PowerPoint 自带在线模板（首选）

- 打开 PowerPoint（Windows 端）。
- 依次选择：`文件(File)` → `新建(New)`。
- 在顶部搜索框输入关键词（建议）：
  - `business`
  - `technology`
  - `data`
  - `consulting`
- 选一个偏商务/科技风的主题，点击 `创建(Create)`。
- 打开后可按需要调整母版样式（见下文），然后 **另存为 `.pptx` 到本仓库**：
  - 建议路径：`templates/your_architecture_template.pptx`

适合 NGSE 这种架构/数据平台场景：蓝色/灰色为主、结构简洁的企业/科技风模板。

### 1.2 SlidesCarnival（高质量免费模板）

- 浏览器搜索并打开：SlidesCarnival（大量免费 PPT / Google Slides 模板）。
- 搜索或筛选关键词（常用）：
  - `business`
  - `technology`
  - `data`
  - `minimal`
  - `corporate`
- 打开某个模板详情页，选择 “Download as PowerPoint template”（下载为 PowerPoint 模板）。
- 得到 `.pptx` 后：
  - 用 PowerPoint 打开，按需要调整母版（字体/颜色/Logo）。
  - 再保存一份到仓库，例如：
    - `templates/slidescarnival_ngse_style.pptx`

> 说明：SlidesCarnival 模板允许免费使用，一般需保留页面中的 credit（版权说明），用于公开分享时注意遵守。

---

## 2. 在模板里需要调整的关键元素

在 PowerPoint 中打开模板后，建议先进入母版视图统一设定：

- 菜单：`视图(View)` → `幻灯片母版(Slide Master)`。
- 推荐统一调整：
  - **字体/字号**：标题与正文的默认字体、大小。
  - **颜色主题**：主色调偏蓝/灰，契合云平台/数据平台主题。
  - **页脚**：项目名（如 “NGSE Data Platform”）、日期、作者。
  - **默认版式**：至少确保 “标题+内容” 版式美观，适合 Pandoc 生成的普通内容页。

调整完后退出母版视图，`另存为` 到 `templates/` 目录，作为之后 Pandoc 的 `--reference-doc`。

---

## 3. 配合 Pandoc 生成 PPT 的推荐命令

假设：
- Markdown 大纲：`.design_docs/ngse_architecture_en.md`
- 模板文件：`templates/ngse_architecture_template.pptx`
- 输出文件夹：`artifacts/`

在 WSL 项目根目录下执行：

```bash
pandoc .design_docs/ngse_architecture_en.md \
  -o artifacts/ngse_architecture_en.pptx \
  --slide-level=2 \
  --reference-doc=templates/ngse_architecture_template.pptx
```

说明：
- `--slide-level=2`：以二级标题 (`##`) 作为一页幻灯片的起始，适合架构/章节型文档。
- 不指定 `--reference-doc` 时，会使用 Pandoc 默认主题；建议始终指定为本仓库的模板。

---

## 4. 使用/维护约定

- 所有 PPT 模板统一存放在：`templates/` 目录。
- 若是为某个项目专用的模板，命名建议：
  - `templates/<project>_ppt_template.pptx`
  - 例如：`templates/ngse_architecture_template.pptx`
- 更新模板时：
  - 始终通过 PowerPoint 打开模板 → 调整母版 → 覆盖保存同名文件。
  - 不要手动改 `.pptx` 的内部结构（避免 Pandoc 解析异常）。

这样，今后只要记住：

1. 在 PowerPoint 或 SlidesCarnival 挑一个模板 → 存到 `templates/`。
2. 用上面的 Pandoc 命令带上 `--reference-doc`。

就可以快速从 `.md` 大纲生成风格统一的架构 PPT。 

