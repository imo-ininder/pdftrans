#!/usr/bin/env python3
"""
PDF 簡繁體轉換工具
支援內建字體和系統細體字型
"""

import fitz
from opencc import OpenCC
import os
import sys
import argparse
import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path

# 常數定義
# PyMuPDF garbage collection 級別：
# - 4: 最激進的清理，用於嵌入大型字體檔案時
# - 3: 標準清理級別，用於內建字體
GARBAGE_LEVEL_WITH_FONTS = 4
GARBAGE_LEVEL_DEFAULT = 3

# 系統字體路徑配置
# 每個平台提供主字體和備用字體列表
SYSTEM_FONTS = {
    'darwin': {  # macOS
        'chinese_light': [
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/PingFang.ttc',
        ],
        'latin_light': [
            '/System/Library/Fonts/HelveticaNeue.ttc',
            '/System/Library/Fonts/Helvetica.ttc',
        ],
    },
    'linux': {
        'chinese_light': [
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Light.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        ],
        'latin_light': [
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        ],
    },
    'win32': {
        'chinese_light': [
            'C:/Windows/Fonts/msyhl.ttc',     # Microsoft YaHei Light
            'C:/Windows/Fonts/msyh.ttc',      # Microsoft YaHei (fallback)
            'C:/Windows/Fonts/simsun.ttc',    # SimSun (fallback)
        ],
        'latin_light': [
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/calibri.ttf',
        ],
    }
}


class PDFTranslator:
    """PDF 簡繁體轉換器"""

    def __init__(self, use_light_font: bool = False, mode: str = 's2t'):
        """
        初始化轉換器

        Args:
            use_light_font: 是否使用系統細體字型
            mode: 轉換模式 ('s2t' 或 't2s')
        """
        self.converter = OpenCC(mode)
        self.use_light_font = use_light_font
        self.mode = mode
        self.logger = self._setup_logger()

    @staticmethod
    def _setup_logger() -> logging.Logger:
        """配置日誌系統"""
        logger = logging.getLogger('PDFTranslator')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    @staticmethod
    def is_cjk_character(char: str) -> bool:
        """
        判斷是否為 CJK 字元

        Args:
            char: 單個字元

        Returns:
            是否為 CJK 字元
        """
        return (
            '\u4e00' <= char <= '\u9fff' or  # CJK 統一漢字
            '\u3000' <= char <= '\u303f' or  # CJK 符號和標點
            '\uff00' <= char <= '\uffef'     # 全形 ASCII、全形標點
        )

    @staticmethod
    def int_to_rgb(color_int: int) -> Tuple[float, float, float]:
        """
        將整數顏色轉換為 RGB 元組

        Args:
            color_int: 整數形式的顏色值

        Returns:
            RGB 元組 (r, g, b)，值範圍 0.0-1.0
        """
        if not isinstance(color_int, int):
            return (0.0, 0.0, 0.0)

        r = ((color_int >> 16) & 0xFF) / 255.0
        g = ((color_int >> 8) & 0xFF) / 255.0
        b = (color_int & 0xFF) / 255.0
        return (r, g, b)

    def _get_system_font_path(self, font_type: str) -> Optional[str]:
        """
        取得系統字體路徑（支援多個備選字體）

        Args:
            font_type: 字體類型 ('chinese_light' 或 'latin_light')

        Returns:
            字體檔案路徑，如果不存在則返回 None
        """
        platform = sys.platform

        # 首先嘗試從環境變數取得
        env_var = f'PDF_TRANSLATOR_{font_type.upper()}_FONT'
        env_path = os.environ.get(env_var)
        if env_path and Path(env_path).exists():
            return env_path

        if platform not in SYSTEM_FONTS:
            self.logger.warning(f"不支援的平台: {platform}")
            return None

        # 嘗試備選字體列表
        font_paths = SYSTEM_FONTS[platform].get(font_type, [])
        for font_path in font_paths:
            if Path(font_path).exists():
                return font_path

        return None

    def _load_builtin_fonts(self) -> Tuple[fitz.Font, fitz.Font]:
        """
        載入內建字體

        Returns:
            (中文字體, 拉丁字體) 元組
        """
        try:
            chinese_font = fitz.Font("china-t")
        except RuntimeError as e:
            self.logger.warning(f"無法載入 china-t 字體: {e}，使用 cjk")
            chinese_font = fitz.Font("cjk")

        try:
            latin_font = fitz.Font("helv")
        except RuntimeError as e:
            self.logger.warning(f"無法載入 helv 字體: {e}，使用 cour")
            latin_font = fitz.Font("cour")

        return chinese_font, latin_font

    def _load_system_fonts(self) -> Tuple[fitz.Font, fitz.Font]:
        """
        載入系統細體字型

        Returns:
            (中文字體, 拉丁字體) 元組
        """
        # 載入中文字體
        chinese_path = self._get_system_font_path('chinese_light')
        if chinese_path:
            try:
                chinese_font = fitz.Font(fontfile=chinese_path)
                self.logger.info(f"✓ 已載入系統中文字體: {Path(chinese_path).name}")
            except (RuntimeError, FileNotFoundError) as e:
                self.logger.warning(f"⚠️  無法載入系統中文字體: {e}")
                chinese_font = fitz.Font("china-t")
        else:
            self.logger.warning("⚠️  找不到系統中文字體，使用預設字體")
            chinese_font = fitz.Font("china-t")

        # 載入拉丁字體
        latin_path = self._get_system_font_path('latin_light')
        if latin_path:
            try:
                latin_font = fitz.Font(fontfile=latin_path)
                self.logger.info(f"✓ 已載入系統拉丁字體: {Path(latin_path).name}")
            except (RuntimeError, FileNotFoundError) as e:
                self.logger.warning(f"⚠️  無法載入系統拉丁字體: {e}")
                latin_font = fitz.Font("helv")
        else:
            self.logger.warning("⚠️  找不到系統拉丁字體，使用預設字體")
            latin_font = fitz.Font("helv")

        return chinese_font, latin_font

    def _load_fonts(self) -> Tuple[fitz.Font, fitz.Font]:
        """
        根據配置載入字體

        Returns:
            (中文字體, 拉丁字體) 元組
        """
        if self.use_light_font:
            return self._load_system_fonts()
        return self._load_builtin_fonts()

    def convert_text(self, text: str) -> str:
        """
        轉換文字

        Args:
            text: 原始文字

        Returns:
            轉換後的文字
        """
        if not text:
            return text
        return self.converter.convert(text)

    def _collect_replacements(self, page: fitz.Page) -> List[Dict]:
        """
        收集頁面中需要轉換的文字片段

        Args:
            page: PDF 頁面物件

        Returns:
            需要替換的文字片段列表
        """
        text_dict = page.get_text("dict")
        blocks = text_dict.get("blocks", [])
        replacements = []

        for block in blocks:
            if block.get("type") != 0:
                continue

            lines = block.get("lines", [])
            for line in lines:
                spans = line.get("spans", [])
                for span in spans:
                    original_text = span.get("text", "")
                    if not original_text or not original_text.strip():
                        continue

                    # 跳過 Private Use Area 字元（如 \ue000）
                    if all('\ue000' <= c <= '\uf8ff' for c in original_text.strip()):
                        continue

                    # 轉換文字
                    converted_text = self.convert_text(original_text)

                    replacements.append({
                        "bbox": span["bbox"],
                        "original": original_text,
                        "converted": converted_text,
                        "size": span.get("size", 12),
                        "color": span.get("color", 0),
                    })

        return replacements

    def _render_text(
        self,
        page: fitz.Page,
        replacements: List[Dict],
        chinese_font: fitz.Font,
        latin_font: fitz.Font
    ) -> None:
        """
        在頁面上重新渲染文字

        Args:
            page: PDF 頁面物件
            replacements: 需要替換的文字片段列表
            chinese_font: 中文字體
            latin_font: 拉丁字體
        """
        # 按顏色分組
        color_groups: Dict[int, List[Dict]] = {}
        for replacement in replacements:
            color_int = replacement["color"]
            if color_int not in color_groups:
                color_groups[color_int] = []
            color_groups[color_int].append(replacement)

        # 處理每個顏色組
        for color_int, group_replacements in color_groups.items():
            color = self.int_to_rgb(color_int)
            writer = fitz.TextWriter(page.rect)

            # 重新繪製文字
            for replacement in group_replacements:
                bbox = replacement["bbox"]
                original_width = bbox[2] - bbox[0]
                converted_text = replacement["converted"]
                fontsize = replacement["size"]

                # 計算自然寬度
                natural_width = 0.0
                for char in converted_text:
                    font = chinese_font if self.is_cjk_character(char) else latin_font
                    char_width = font.text_length(char, fontsize=fontsize)
                    natural_width += char_width

                # 計算縮放因子
                scale_factor = original_width / natural_width if natural_width > 0 else 1.0

                # 逐字元渲染
                x_pos = bbox[0]
                y_pos = bbox[3]

                for char in converted_text:
                    font = chinese_font if self.is_cjk_character(char) else latin_font
                    point = fitz.Point(x_pos, y_pos)
                    writer.append(point, char, font=font, fontsize=fontsize)

                    char_width = font.text_length(char, fontsize=fontsize)
                    x_pos += char_width * scale_factor

            writer.write_text(page, color=color)

    def translate_pdf(self, input_path: str, output_path: str) -> None:
        """
        翻譯 PDF 檔案

        Args:
            input_path: 輸入 PDF 檔案路徑
            output_path: 輸出 PDF 檔案路徑

        Raises:
            FileNotFoundError: 輸入檔案不存在
        """
        self.logger.info(f"正在處理 PDF 檔案: {input_path}")

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"找不到輸入檔案: {input_path}")

        doc = fitz.open(input_path)
        total_pages = len(doc)
        self.logger.info(f"PDF 共有 {total_pages} 頁")

        # 載入字體
        if self.use_light_font:
            self.logger.info("使用系統細體字型")
            self.logger.info("注意: 使用系統字體會增加檔案大小 (~25MB)")
        else:
            self.logger.info("使用內建字體: Droid Sans Fallback (中文) + Helvetica (英文)")

        chinese_font, latin_font = self._load_fonts()
        total_spans_modified = 0

        # 處理每一頁
        for page_num in range(total_pages):
            page = doc[page_num]
            self.logger.info(f"處理第 {page_num + 1}/{total_pages} 頁...")

            # 收集需要轉換的文字
            replacements = self._collect_replacements(page)

            if not replacements:
                continue

            self.logger.info(f"  找到 {len(replacements)} 個需要轉換的文字片段")

            # 刪除原文字
            for replacement in replacements:
                rect = fitz.Rect(replacement["bbox"])
                page.add_redact_annot(rect)
            page.apply_redactions()

            # 重新渲染文字
            self._render_text(page, replacements, chinese_font, latin_font)

            total_spans_modified += len(replacements)
            self.logger.info(f"  ✓ 已轉換 {len(replacements)} 個文字片段")

        self.logger.info(f"\n處理完成: 總共轉換了 {total_spans_modified} 個文字片段")

        # 儲存
        self.logger.info("正在儲存...")
        garbage_level = GARBAGE_LEVEL_WITH_FONTS if self.use_light_font else GARBAGE_LEVEL_DEFAULT
        doc.save(
            output_path,
            garbage=garbage_level,
            deflate=True,
            deflate_fonts=self.use_light_font,
            clean=True
        )
        doc.close()

        # 顯示檔案大小
        output_size = os.path.getsize(output_path) / 1024 / 1024
        self.logger.info(f"轉換完成！輸出檔案: {output_path}")
        self.logger.info(f"檔案大小: {output_size:.1f} MB")


def main():
    """主函式"""
    parser = argparse.ArgumentParser(
        description='PDF 簡繁體轉換工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 使用內建字體 (檔案小, ~19MB)
  python pdf_translator.py input.pdf output.pdf

  # 使用系統細體字型 (檔案較大, ~45MB)
  python pdf_translator.py input.pdf output.pdf --light

  # 繁體轉簡體
  python pdf_translator.py input.pdf output.pdf --mode t2s

環境變數:
  PDF_TRANSLATOR_CHINESE_LIGHT_FONT  自訂中文細體字體路徑
  PDF_TRANSLATOR_LATIN_LIGHT_FONT    自訂拉丁細體字體路徑
        """
    )

    parser.add_argument('input', help='輸入 PDF 檔案路徑')
    parser.add_argument('output', help='輸出 PDF 檔案路徑')
    parser.add_argument(
        '-l', '--light',
        action='store_true',
        help='使用系統細體字型'
    )
    parser.add_argument(
        '--mode',
        choices=['s2t', 't2s'],
        default='s2t',
        help='轉換模式: s2t (簡轉繁), t2s (繁轉簡)'
    )
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='強制覆蓋輸出檔案'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='顯示詳細日誌'
    )

    args = parser.parse_args()

    # 配置日誌級別
    if args.verbose:
        logging.getLogger('PDFTranslator').setLevel(logging.DEBUG)

    # 檢查輸出檔案是否存在
    if os.path.exists(args.output) and not args.force:
        response = input(f"輸出檔案 '{args.output}' 已存在，是否覆蓋？(y/n): ")
        if response.lower() != 'y':
            print("操作已取消")
            sys.exit(0)

    translator = PDFTranslator(use_light_font=args.light, mode=args.mode)
    try:
        translator.translate_pdf(args.input, args.output)
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
