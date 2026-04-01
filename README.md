# PDF 简繁体转换工具

一个功能强大的 PDF 简繁体转换工具，支持精确的字体控制和排版保持。

## 特性

- ✅ 简体中文 ⇄ 繁体中文双向转换
- ✅ 保持原始排版和格式
- ✅ 支持混合中英文内容
- ✅ 可选系统细体字型
- ✅ 跨平台支持（macOS, Linux, Windows）
- ✅ 自定义字体路径

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install pdftrans
```

### 从源码安装

```bash
git clone https://github.com/yourusername/pdftrans.git
cd pdftrans
pip install -e .
```

### 依赖

- Python 3.7+
- PyMuPDF >= 1.23.0
- opencc-python-reimplemented >= 0.1.7
- click >= 8.1.0

## 使用方法

安装后，你可以通过两种方式使用：

### 方式 1: 命令行工具（推荐）

安装后会注册 `pdftrans` 命令：

```bash
# 简体转繁体（使用内建字体）
pdftrans input.pdf output.pdf

# 使用系统细体字型
pdftrans input.pdf output.pdf --light

# 繁体转简体
pdftrans input.pdf output.pdf --mode t2s

# 强制覆盖 + 详细日志
pdftrans input.pdf output.pdf -f -v

# 查看帮助
pdftrans --help
```

### 方式 2: Python 脚本

```bash
# 简体转繁体（使用内建字体）
python pdf_translator.py input.pdf output.pdf

# 使用系统细体字型
python pdf_translator.py input.pdf output.pdf --light

# 繁体转简体
python pdf_translator.py input.pdf output.pdf --mode t2s
```

## 命令行选项

```
选项:
  -l, --light              使用系统细体字型 (文件会增大约 25MB)
  --mode [s2t|t2s]        转换模式: s2t (简转繁), t2s (繁转简)
  -f, --force             强制覆盖输出文件
  -v, --verbose           显示详细日志
  --version               显示版本信息
  --help                  显示帮助信息
```

## 字体说明

### 内建字体模式（默认）

- **中文**: Droid Sans Fallback
- **英文**: Helvetica
- **文件大小**: 约 +4MB
- **优点**: 文件小，兼容性好
- **缺点**: 字体较粗

### 细体字型模式（--light）

| 平台 | 中文字体 | 英文字体 | 备用字体 |
|------|---------|---------|---------|
| macOS | STHeiti Light | Helvetica Neue | PingFang |
| Linux | Noto Sans CJK Light | Liberation Sans | DejaVu Sans |
| Windows | Microsoft YaHei Light | Arial | Calibri |

- **文件大小**: 约 +30MB
- **优点**: 字体更细更美观
- **缺点**: 文件较大

## 自定义字体

通过环境变量指定自定义字体路径：

```bash
# 设置自定义中文字体
export PDF_TRANSLATOR_CHINESE_LIGHT_FONT="/path/to/your/font.ttf"

# 设置自定义拉丁字体
export PDF_TRANSLATOR_LATIN_LIGHT_FONT="/path/to/your/font.ttf"

# 使用自定义字体转换
pdftrans input.pdf output.pdf --light
```

## 已知限制

1. **不支持扫描版 PDF**: 仅支持文本型 PDF
2. **字体嵌入**: 使用系统字体会显著增加文件大小
3. **处理时间**: 大型 PDF 处理时间较长
4. **复杂排版**: 某些复杂排版可能需要手动调整

## 常见问题

### Q: 转换后文件变大了？
A: 使用 `--light` 选项会嵌入完整的系统字体（约 25MB）。如果希望保持文件小，不要使用 `--light` 选项。

### Q: 找不到 pdftrans 命令？
A: 确保安装时使用了 `pip install -e .` 或 `pip install pdftrans`，并且 Python 的 scripts 目录在 PATH 中。

### Q: Windows 上找不到字体？
A: 工具会自动尝试多个备用字体。如果都找不到，会自动降级到内建字体。

## 开发

```bash
# 克隆仓库
git clone https://github.com/yourusername/pdftrans.git
cd pdftrans

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black .
```

## 许可证

MIT License

## 作者

Your Name

## 更新日志

### v1.0.0 (2024-04-01)
- ✅ 支持简繁双向转换
- ✅ 支持内建字体和系统细体字型
- ✅ 跨平台支持（macOS, Linux, Windows）
- ✅ 自定义字体路径
- ✅ 命令行工具
- ✅ 完整的类型注解
- ✅ 日志系统
