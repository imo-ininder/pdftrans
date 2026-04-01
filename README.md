# PDF 簡繁體轉換工具

一個功能強大的 PDF 簡繁體轉換工具，支援精確的字體控制和排版保持。

## 特性

- ✅ 簡體中文 ⇄ 繁體中文雙向轉換
- ✅ 保持原始排版和格式
- ✅ 支援混合中英文內容
- ✅ 可選系統細體字型
- ✅ 跨平台支援（macOS, Linux, Windows）
- ✅ 自訂字體路徑

## 安裝

### 從 PyPI 安裝（推薦）

```bash
pip install pdftrans
```

### 從原始碼安裝

```bash
git clone https://github.com/imo-ininder/pdftrans.git
cd pdftrans
pip install -e .
```

### 依賴

- Python 3.7+
- PyMuPDF >= 1.23.0
- opencc-python-reimplemented >= 0.1.7
- click >= 8.1.0

## 使用方法

安裝後，你可以透過兩種方式使用：

### 方式 1: 命令列工具（推薦）

安裝後會註冊 `pdftrans` 命令：

```bash
# 簡體轉繁體（使用內建字體）
pdftrans input.pdf output.pdf

# 使用系統細體字型
pdftrans input.pdf output.pdf --light

# 繁體轉簡體
pdftrans input.pdf output.pdf --mode t2s

# 強制覆蓋 + 詳細日誌
pdftrans input.pdf output.pdf -f -v

# 檢視說明
pdftrans --help
```

### 方式 2: Python 腳本

```bash
# 簡體轉繁體（使用內建字體）
python pdf_translator.py input.pdf output.pdf

# 使用系統細體字型
python pdf_translator.py input.pdf output.pdf --light

# 繁體轉簡體
python pdf_translator.py input.pdf output.pdf --mode t2s
```

## 命令列選項

```
選項:
  -l, --light              使用系統細體字型 (檔案會增大約 25MB)
  --mode [s2t|t2s]        轉換模式: s2t (簡轉繁), t2s (繁轉簡)
  -f, --force             強制覆蓋輸出檔案
  -v, --verbose           顯示詳細日誌
  --version               顯示版本資訊
  --help                  顯示說明資訊
```

## 字體說明

### 內建字體模式（預設）

- **中文**: Droid Sans Fallback
- **英文**: Helvetica
- **檔案大小**: 約 +4MB
- **優點**: 檔案小，相容性好
- **缺點**: 字體較粗

### 細體字型模式（--light）

| 平台 | 中文字體 | 英文字體 | 備用字體 |
|------|---------|---------|---------|
| macOS | STHeiti Light | Helvetica Neue | PingFang |
| Linux | Noto Sans CJK Light | Liberation Sans | DejaVu Sans |
| Windows | Microsoft YaHei Light | Arial | Calibri |

- **檔案大小**: 約 +30MB
- **優點**: 字體更細更美觀
- **缺點**: 檔案較大

## 自訂字體

透過環境變數指定自訂字體路徑：

```bash
# 設定自訂中文字體
export PDF_TRANSLATOR_CHINESE_LIGHT_FONT="/path/to/your/font.ttf"

# 設定自訂拉丁字體
export PDF_TRANSLATOR_LATIN_LIGHT_FONT="/path/to/your/font.ttf"

# 使用自訂字體轉換
pdftrans input.pdf output.pdf --light
```

## 已知限制

1. **不支援掃描版 PDF**: 僅支援文字型 PDF
2. **字體嵌入**: 使用系統字體會顯著增加檔案大小
3. **處理時間**: 大型 PDF 處理時間較長
4. **複雜排版**: 某些複雜排版可能需要手動調整

## 常見問題

### Q: 轉換後檔案變大了？
A: 使用 `--light` 選項會嵌入完整的系統字體（約 25MB）。如果希望保持檔案小，不要使用 `--light` 選項。

### Q: 找不到 pdftrans 命令？
A: 確保安裝時使用了 `pip install -e .` 或 `pip install pdftrans`，並且 Python 的 scripts 目錄在 PATH 中。

### Q: Windows 上找不到字體？
A: 工具會自動嘗試多個備用字體。如果都找不到，會自動降級到內建字體。

## 開發

```bash
# 複製儲存庫
git clone https://github.com/imo-ininder/pdftrans.git
cd pdftrans

# 安裝開發依賴
pip install -e ".[dev]"

# 執行測試
pytest

# 程式碼格式化
black .
```

## 授權條款

MIT License

## 作者

Tony Liu (tony840622@gmail.com)

## 更新日誌

### v1.0.0 (2026-04-01)
- ✅ 支援簡繁雙向轉換
- ✅ 支援內建字體和系統細體字型
- ✅ 跨平台支援（macOS, Linux, Windows）
- ✅ 自訂字體路徑
- ✅ 命令列工具
- ✅ 完整的類型註解
- ✅ 日誌系統
