#!/usr/bin/env python3
"""
PDF 簡繁體轉換 CLI 工具
"""

import click
import os
import sys
from pdf_translator import PDFTranslator


@click.command()
@click.argument('input_pdf', type=click.Path(exists=True))
@click.argument('output_pdf', type=click.Path())
@click.option('--light', '-l', is_flag=True,
              help='使用系統細體字型 (檔案會增大約 25MB)')
@click.option('--mode', type=click.Choice(['s2t', 't2s']), default='s2t',
              help='轉換模式: s2t (簡轉繁), t2s (繁轉簡)')
@click.option('--force', '-f', is_flag=True,
              help='強制覆蓋輸出檔案')
@click.option('--verbose', '-v', is_flag=True,
              help='顯示詳細處理資訊')
@click.version_option(version='1.0.0')
def main(input_pdf, output_pdf, light, mode, force, verbose):
    """
    PDF 簡繁體轉換工具 - 保留原始佈局的簡繁轉換

    \b
    INPUT_PDF: 輸入 PDF 檔案路徑
    OUTPUT_PDF: 輸出 PDF 檔案路徑

    \b
    範例:
      # 簡體轉繁體（使用內建字體）
      pdftrans input.pdf output.pdf

      # 使用系統細體字型
      pdftrans input.pdf output.pdf --light

      # 繁體轉簡體
      pdftrans input.pdf output.pdf --mode t2s

      # 強制覆蓋 + 詳細日誌
      pdftrans input.pdf output.pdf -f -v
    """
    try:
        # 檢查輸出檔案是否存在
        if os.path.exists(output_pdf) and not force:
            if not click.confirm(f"輸出檔案 '{output_pdf}' 已存在，是否覆蓋？"):
                click.echo("操作已取消")
                sys.exit(0)

        # 建立轉換器
        translator = PDFTranslator(use_light_font=light, mode=mode)

        if verbose:
            click.echo(f"輸入檔案: {input_pdf}")
            click.echo(f"輸出檔案: {output_pdf}")
            click.echo(f"轉換模式: {mode}")
            click.echo(f"字體模式: {'系統細體' if light else '內建字體'}")
            click.echo("")

        # 執行轉換
        translator.translate_pdf(input_pdf, output_pdf)

        # 顯示完成資訊
        click.secho(f"\n✓ 轉換完成！", fg='green', bold=True)

        # 顯示檔案大小資訊
        if verbose:
            input_size = os.path.getsize(input_pdf) / 1024 / 1024
            output_size = os.path.getsize(output_pdf) / 1024 / 1024
            click.echo(f"輸入檔案大小: {input_size:.2f} MB")
            click.echo(f"輸出檔案大小: {output_size:.2f} MB")
            click.echo(f"大小變化: {output_size - input_size:+.2f} MB")

    except FileNotFoundError as e:
        click.secho(f"✗ 錯誤: {e}", fg='red', bold=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ 處理失敗: {e}", fg='red', bold=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
