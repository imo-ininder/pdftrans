from setuptools import setup, find_packages
from pathlib import Path

# 读取长描述
long_description = Path("README.md").read_text(encoding="utf-8")

setup(
    name='pdftrans',
    version='1.0.0',
    description='PDF 簡繁體轉換工具 - 保留原始佈局',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Tony Liu',
    author_email='tony840622@gmail.com',
    url='https://github.com/imo-ininder/pdftrans',
    py_modules=['pdf_translator', 'cli'],
    install_requires=[
        'PyMuPDF>=1.23.0',
        'opencc-python-reimplemented>=0.1.7',
        'click>=8.1.0',
    ],
    entry_points={
        'console_scripts': [
            'pdftrans=cli:main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Text Processing',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
