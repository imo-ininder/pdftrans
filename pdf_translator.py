#!/usr/bin/env python3
"""
PDF 简繁体转换工具
支持内建字体和系统细体字型
"""

import fitz
from opencc import OpenCC
import os
import sys
import argparse
import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path

# 常量定义
# PyMuPDF garbage collection 级别：
# - 4: 最激进的清理，用于嵌入大型字体文件时
# - 3: 标准清理级别，用于内建字体
GARBAGE_LEVEL_WITH_FONTS = 4
GARBAGE_LEVEL_DEFAULT = 3

# 系统字体路径配置
# 每个平台提供主字体和备用字体列表
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
    """PDF 简繁体转换器"""

    def __init__(self, use_light_font: bool = False, mode: str = 's2t'):
        """
        初始化转换器

        Args:
            use_light_font: 是否使用系统细体字型
            mode: 转换模式 ('s2t' 或 't2s')
        """
        self.converter = OpenCC(mode)
        self.use_light_font = use_light_font
        self.mode = mode
        self.logger = self._setup_logger()

    @staticmethod
    def _setup_logger() -> logging.Logger:
        """配置日志系统"""
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
        判断是否为CJK字符

        Args:
            char: 单个字符

        Returns:
            是否为CJK字符
        """
        return (
            '\u4e00' <= char <= '\u9fff' or  # CJK统一汉字
            '\u3000' <= char <= '\u303f' or  # CJK符号和标点
            '\uff00' <= char <= '\uffef'     # 全形ASCII、全形标点
        )

    @staticmethod
    def int_to_rgb(color_int: int) -> Tuple[float, float, float]:
        """
        将整数颜色转换为RGB元组

        Args:
            color_int: 整数形式的颜色值

        Returns:
            RGB元组 (r, g, b)，值范围 0.0-1.0
        """
        if not isinstance(color_int, int):
            return (0.0, 0.0, 0.0)

        r = ((color_int >> 16) & 0xFF) / 255.0
        g = ((color_int >> 8) & 0xFF) / 255.0
        b = (color_int & 0xFF) / 255.0
        return (r, g, b)

    def _get_system_font_path(self, font_type: str) -> Optional[str]:
        """
        获取系统字体路径（支持多个备选字体）

        Args:
            font_type: 字体类型 ('chinese_light' 或 'latin_light')

        Returns:
            字体文件路径，如果不存在则返回 None
        """
        platform = sys.platform

        # 首先尝试从环境变量获取
        env_var = f'PDF_TRANSLATOR_{font_type.upper()}_FONT'
        env_path = os.environ.get(env_var)
        if env_path and Path(env_path).exists():
            return env_path

        if platform not in SYSTEM_FONTS:
            self.logger.warning(f"不支持的平台: {platform}")
            return None

        # 尝试备选字体列表
        font_paths = SYSTEM_FONTS[platform].get(font_type, [])
        for font_path in font_paths:
            if Path(font_path).exists():
                return font_path

        return None

    def _load_builtin_fonts(self) -> Tuple[fitz.Font, fitz.Font]:
        """
        加载内建字体

        Returns:
            (中文字体, 拉丁字体) 元组
        """
        try:
            chinese_font = fitz.Font("china-t")
        except RuntimeError as e:
            self.logger.warning(f"无法加载 china-t 字体: {e}，使用 cjk")
            chinese_font = fitz.Font("cjk")

        try:
            latin_font = fitz.Font("helv")
        except RuntimeError as e:
            self.logger.warning(f"无法加载 helv 字体: {e}，使用 cour")
            latin_font = fitz.Font("cour")

        return chinese_font, latin_font

    def _load_system_fonts(self) -> Tuple[fitz.Font, fitz.Font]:
        """
        加载系统细体字型

        Returns:
            (中文字体, 拉丁字体) 元组
        """
        # 加载中文字体
        chinese_path = self._get_system_font_path('chinese_light')
        if chinese_path:
            try:
                chinese_font = fitz.Font(fontfile=chinese_path)
                self.logger.info(f"✓ 已载入系统中文字体: {Path(chinese_path).name}")
            except (RuntimeError, FileNotFoundError) as e:
                self.logger.warning(f"⚠️  无法加载系统中文字体: {e}")
                chinese_font = fitz.Font("china-t")
        else:
            self.logger.warning("⚠️  找不到系统中文字体，使用默认字体")
            chinese_font = fitz.Font("china-t")

        # 加载拉丁字体
        latin_path = self._get_system_font_path('latin_light')
        if latin_path:
            try:
                latin_font = fitz.Font(fontfile=latin_path)
                self.logger.info(f"✓ 已载入系统拉丁字体: {Path(latin_path).name}")
            except (RuntimeError, FileNotFoundError) as e:
                self.logger.warning(f"⚠️  无法加载系统拉丁字体: {e}")
                latin_font = fitz.Font("helv")
        else:
            self.logger.warning("⚠️  找不到系统拉丁字体，使用默认字体")
            latin_font = fitz.Font("helv")

        return chinese_font, latin_font

    def _load_fonts(self) -> Tuple[fitz.Font, fitz.Font]:
        """
        根据配置加载字体

        Returns:
            (中文字体, 拉丁字体) 元组
        """
        if self.use_light_font:
            return self._load_system_fonts()
        return self._load_builtin_fonts()

    def convert_text(self, text: str) -> str:
        """
        转换文本

        Args:
            text: 原始文本

        Returns:
            转换后的文本
        """
        if not text:
            return text
        return self.converter.convert(text)

    def _collect_replacements(self, page: fitz.Page) -> List[Dict]:
        """
        收集页面中需要转换的文本片段

        Args:
            page: PDF页面对象

        Returns:
            需要替换的文本片段列表
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

                    # 跳过Private Use Area字符（如\ue000）
                    if all('\ue000' <= c <= '\uf8ff' for c in original_text.strip()):
                        continue

                    # 转换文本
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
        在页面上重新渲染文本

        Args:
            page: PDF页面对象
            replacements: 需要替换的文本片段列表
            chinese_font: 中文字体
            latin_font: 拉丁字体
        """
        # 按颜色分组
        color_groups: Dict[int, List[Dict]] = {}
        for replacement in replacements:
            color_int = replacement["color"]
            if color_int not in color_groups:
                color_groups[color_int] = []
            color_groups[color_int].append(replacement)

        # 处理每个颜色组
        for color_int, group_replacements in color_groups.items():
            color = self.int_to_rgb(color_int)
            writer = fitz.TextWriter(page.rect)

            # 重新绘制文本
            for replacement in group_replacements:
                bbox = replacement["bbox"]
                original_width = bbox[2] - bbox[0]
                converted_text = replacement["converted"]
                fontsize = replacement["size"]

                # 计算自然宽度
                natural_width = 0.0
                for char in converted_text:
                    font = chinese_font if self.is_cjk_character(char) else latin_font
                    char_width = font.text_length(char, fontsize=fontsize)
                    natural_width += char_width

                # 计算缩放因子
                scale_factor = original_width / natural_width if natural_width > 0 else 1.0

                # 逐字符渲染
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
        翻译PDF文件

        Args:
            input_path: 输入PDF文件路径
            output_path: 输出PDF文件路径

        Raises:
            FileNotFoundError: 输入文件不存在
        """
        self.logger.info(f"正在处理 PDF 文件: {input_path}")

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"找不到输入文件: {input_path}")

        doc = fitz.open(input_path)
        total_pages = len(doc)
        self.logger.info(f"PDF 共有 {total_pages} 页")

        # 加载字体
        if self.use_light_font:
            self.logger.info("使用系统细体字型")
            self.logger.info("注意: 使用系统字体会增加文件大小 (~25MB)")
        else:
            self.logger.info("使用内建字体: Droid Sans Fallback (中文) + Helvetica (英文)")

        chinese_font, latin_font = self._load_fonts()
        total_spans_modified = 0

        # 处理每一页
        for page_num in range(total_pages):
            page = doc[page_num]
            self.logger.info(f"处理第 {page_num + 1}/{total_pages} 页...")

            # 收集需要转换的文本
            replacements = self._collect_replacements(page)

            if not replacements:
                continue

            self.logger.info(f"  找到 {len(replacements)} 个需要转换的文本片段")

            # 删除原文本
            for replacement in replacements:
                rect = fitz.Rect(replacement["bbox"])
                page.add_redact_annot(rect)
            page.apply_redactions()

            # 重新渲染文本
            self._render_text(page, replacements, chinese_font, latin_font)

            total_spans_modified += len(replacements)
            self.logger.info(f"  ✓ 已转换 {len(replacements)} 个文本片段")

        self.logger.info(f"\n处理完成: 总共转换了 {total_spans_modified} 个文本片段")

        # 保存
        self.logger.info("正在保存...")
        garbage_level = GARBAGE_LEVEL_WITH_FONTS if self.use_light_font else GARBAGE_LEVEL_DEFAULT
        doc.save(
            output_path,
            garbage=garbage_level,
            deflate=True,
            deflate_fonts=self.use_light_font,
            clean=True
        )
        doc.close()

        # 显示文件大小
        output_size = os.path.getsize(output_path) / 1024 / 1024
        self.logger.info(f"转换完成！输出文件: {output_path}")
        self.logger.info(f"文件大小: {output_size:.1f} MB")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='PDF 简繁体转换工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用内建字体 (文件小, ~19MB)
  python pdf_translator.py input.pdf output.pdf

  # 使用系统细体字型 (文件较大, ~45MB)
  python pdf_translator.py input.pdf output.pdf --light

  # 繁体转简体
  python pdf_translator.py input.pdf output.pdf --mode t2s

环境变量:
  PDF_TRANSLATOR_CHINESE_LIGHT_FONT  自定义中文细体字体路径
  PDF_TRANSLATOR_LATIN_LIGHT_FONT    自定义拉丁细体字体路径
        """
    )

    parser.add_argument('input', help='输入PDF文件路径')
    parser.add_argument('output', help='输出PDF文件路径')
    parser.add_argument(
        '-l', '--light',
        action='store_true',
        help='使用系统细体字型'
    )
    parser.add_argument(
        '--mode',
        choices=['s2t', 't2s'],
        default='s2t',
        help='转换模式: s2t (简转繁), t2s (繁转简)'
    )
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='强制覆盖输出文件'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细日志'
    )

    args = parser.parse_args()

    # 配置日志级别
    if args.verbose:
        logging.getLogger('PDFTranslator').setLevel(logging.DEBUG)

    # 检查输出文件是否存在
    if os.path.exists(args.output) and not args.force:
        response = input(f"输出文件 '{args.output}' 已存在，是否覆盖? (y/n): ")
        if response.lower() != 'y':
            print("操作已取消")
            sys.exit(0)

    translator = PDFTranslator(use_light_font=args.light, mode=args.mode)
    try:
        translator.translate_pdf(args.input, args.output)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
