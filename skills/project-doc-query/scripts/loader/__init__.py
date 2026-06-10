#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
loader 子包入口

暴露 8 个 Loader 类：
- WordLoader（.docx / .doc）
- PDFLoader（.pdf，含扫描件检测）
- TextLoader（.txt）
- MarkdownLoader（.md / .markdown）
- CSVLoader（.csv）
- JSONLoader（.json）
- EmlLoader（.eml）
- ExcelLoader（.xlsx / .xlsm，project-doc skill 自带）
"""

from pathlib import Path
import sys
import importlib.util

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_loaded: dict = {}


def _get_cls(name: str, file_name: str):
    if name in _loaded:
        return _loaded[name]
    mod = _load(f"loader.{name}", _HERE / file_name)
    cls = getattr(mod, name, None)
    _loaded[name] = cls
    return cls


# 全部按需懒加载（缺失依赖不报错）
try:
    WordLoader = _get_cls("WordLoader", "WordLoader.py")
except Exception:
    WordLoader = None  # type: ignore

try:
    PDFLoader = _get_cls("PDFLoader", "PDFLoader.py")
except Exception:
    PDFLoader = None  # type: ignore

try:
    TextLoader = _get_cls("TextLoader", "TextLoader.py")
except Exception:
    TextLoader = None  # type: ignore

try:
    MarkdownLoader = _get_cls("MarkdownLoader", "MarkdownLoader.py")
except Exception:
    MarkdownLoader = None  # type: ignore

try:
    CSVLoader = _get_cls("CSVLoader", "CSVLoader.py")
except Exception:
    CSVLoader = None  # type: ignore

try:
    JSONLoader = _get_cls("JSONLoader", "JSONLoader.py")
except Exception:
    JSONLoader = None  # type: ignore

try:
    EmlLoader = _get_cls("EmlLoader", "EmlLoader.py")
except Exception:
    EmlLoader = None  # type: ignore

try:
    ExcelLoader = _get_cls("ExcelLoader", "ExcelLoader.py")
except Exception:
    ExcelLoader = None  # type: ignore


__all__ = [
    "WordLoader",
    "PDFLoader",
    "TextLoader",
    "MarkdownLoader",
    "CSVLoader",
    "JSONLoader",
    "EmlLoader",
    "ExcelLoader",
]
