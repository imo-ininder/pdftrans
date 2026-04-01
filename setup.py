from setuptools import setup, find_packages

setup(
    name='pdftrans',
    version='1.0.0',
    description='PDF 简繁体转换工具 - 保留原始布局',
    author='Tony Liu',
    py_modules=['pdf_translator', 'cli'],
    install_requires=[
        'PyMuPDF>=1.23.0',
        'opencc-python-reimplemented>=0.1.7',
        'click>=8.1.0',
    ],
    entry_points={
        'console_scripts': [
            'pdftrans=cli:convert',
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
