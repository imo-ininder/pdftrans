#!/usr/bin/env python3
"""
PDF 简繁体转换 CLI 工具
"""

import click
import os
import sys
from pdf_translator import PDFTranslator


@click.command()
@click.argument('input_pdf', type=click.Path(exists=True))
@click.argument('output_pdf', type=click.Path())
@click.option('--light', '-l', is_flag=True,
              help='使用系统细体字型 (文件会增大约 25MB)')
@click.option('--mode', type=click.Choice(['s2t', 't2s']), default='s2t',
              help='转换模式: s2t (简转繁), t2s (繁转简)')
@click.option('--force', '-f', is_flag=True,
              help='强制覆盖输出文件')
@click.option('--verbose', '-v', is_flag=True,
              help='显示详细处理信息')
@click.version_option(version='1.0.0')
def main(input_pdf, output_pdf, light, mode, force, verbose):
    """
    PDF 简繁体转换工具 - 保留原始布局的简繁转换

    \b
    INPUT_PDF: 输入 PDF 文件路径
    OUTPUT_PDF: 输出 PDF 文件路径

    \b
    示例:
      # 简体转繁体（使用内建字体）
      pdftrans input.pdf output.pdf

      # 使用系统细体字型
      pdftrans input.pdf output.pdf --light

      # 繁体转简体
      pdftrans input.pdf output.pdf --mode t2s

      # 强制覆盖 + 详细日志
      pdftrans input.pdf output.pdf -f -v
    """
    try:
        # 检查输出文件是否存在
        if os.path.exists(output_pdf) and not force:
            if not click.confirm(f"输出文件 '{output_pdf}' 已存在，是否覆盖?"):
                click.echo("操作已取消")
                sys.exit(0)

        # 创建转换器
        translator = PDFTranslator(use_light_font=light, mode=mode)

        if verbose:
            click.echo(f"输入文件: {input_pdf}")
            click.echo(f"输出文件: {output_pdf}")
            click.echo(f"转换模式: {mode}")
            click.echo(f"字体模式: {'系统细体' if light else '内建字体'}")
            click.echo("")

        # 执行转换
        translator.translate_pdf(input_pdf, output_pdf)

        # 显示完成信息
        click.secho(f"\n✓ 转换完成！", fg='green', bold=True)

        # 显示文件大小信息
        if verbose:
            input_size = os.path.getsize(input_pdf) / 1024 / 1024
            output_size = os.path.getsize(output_pdf) / 1024 / 1024
            click.echo(f"输入文件大小: {input_size:.2f} MB")
            click.echo(f"输出文件大小: {output_size:.2f} MB")
            click.echo(f"大小变化: {output_size - input_size:+.2f} MB")

    except FileNotFoundError as e:
        click.secho(f"✗ 错误: {e}", fg='red', bold=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ 处理失败: {e}", fg='red', bold=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
