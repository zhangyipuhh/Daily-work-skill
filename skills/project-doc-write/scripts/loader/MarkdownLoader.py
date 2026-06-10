#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
MarkdownLoader 模块（project-doc-write skill 自带）

Date: 2026-06-10
Author: project-doc skill 套件
"""

from pathlib import Path
from typing import List, Any, Dict

try:
    from langchain_core.documents import Document  # type: ignore
except Exception:
    Document = None  # type: ignore


class _SimpleDoc:
    __slots__ = ("page_content", "metadata")

    def __init__(self, page_content: str = "", metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}


class MarkdownLoader:
    LOADER_NAME = "MarkdownLoader"

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def _make_doc(self, page_content: str, metadata: Dict[str, Any]):
        DocCls = Document if Document is not None else _SimpleDoc
        return DocCls(page_content=page_content, metadata=metadata)

    def load(self) -> List[Any]:
        if not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在: {self.file_path}")
        for enc in ("utf-8", "utf-8-sig", "gb18030", "gbk"):
            try:
                text = self.file_path.read_text(encoding=enc)
                break
            except Exception:
                continue
        else:
            text = self.file_path.read_text(encoding="utf-8", errors="ignore")
        metadata = {
            "source": str(self.file_path),
            "type": "markdown",
            "length": len(text),
        }
        return [self._make_doc(page_content=text, metadata=metadata)]

    def lazy_load(self) -> List[Any]:
        return self.load()

    @property
    def exists(self) -> bool:
        return self.file_path.exists()
