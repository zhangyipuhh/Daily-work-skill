#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
loader 子包入口（project-doc-write skill 自带）

Date: 2026-06-10
Author: project-doc skill 套件
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


try:
    WordLoader = _get_cls("WordLoader", "WordLoader.py")
except Exception:
    WordLoader = None
try:
    PDFLoader = _get_cls("PDFLoader", "PDFLoader.py")
except Exception:
    PDFLoader = None
try:
    TextLoader = _get_cls("TextLoader", "TextLoader.py")
except Exception:
    TextLoader = None
try:
    MarkdownLoader = _get_cls("MarkdownLoader", "MarkdownLoader.py")
except Exception:
    MarkdownLoader = None
try:
    CSVLoader = _get_cls("CSVLoader", "CSVLoader.py")
except Exception:
    CSVLoader = None
try:
    JSONLoader = _get_cls("JSONLoader", "JSONLoader.py")
except Exception:
    JSONLoader = None
try:
    EmlLoader = _get_cls("EmlLoader", "EmlLoader.py")
except Exception:
    EmlLoader = None
try:
    ExcelLoader = _get_cls("ExcelLoader", "ExcelLoader.py")
except Exception:
    ExcelLoader = None


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
