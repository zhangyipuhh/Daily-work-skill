#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
JSONLoader 模块（project-doc-write skill 自带）

Date: 2026-06-10
Author: project-doc skill 套件
"""

from pathlib import Path
from typing import List, Any, Dict
import json

try:
    from langchain_core.documents import Document  # type: ignore
except Exception:
    Document = None  # type: ignore


class _SimpleDoc:
    __slots__ = ("page_content", "metadata")

    def __init__(self, page_content: str = "", metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}


class JSONLoader:
    LOADER_NAME = "JSONLoader"

    def __init__(self, file_path: str, jq_schema: str = ".[]", text_content: bool = False):
        self.file_path = Path(file_path)
        self.jq_schema = jq_schema
        self.text_content = text_content
        self._data = None

    def _load_data(self):
        if self._data is None:
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
            self._data = json.loads(text)
        return self._data

    def _resolve_jq(self, data: Any, schema: str) -> List[Any]:
        if not schema or schema == ".":
            return [data]
        parts = [p for p in schema.split(".") if p]
        results = [data]
        for part in parts:
            new_results = []
            for item in results:
                if part == "[]":
                    if isinstance(item, list):
                        new_results.extend(item)
                    else:
                        new_results.append(item)
                else:
                    if isinstance(item, dict) and part in item:
                        new_results.append(item[part])
            results = new_results
        return results

    def _make_doc(self, page_content: str, metadata: Dict[str, Any]):
        DocCls = Document if Document is not None else _SimpleDoc
        return DocCls(page_content=page_content, metadata=metadata)

    def load(self) -> List[Any]:
        data = self._load_data()
        items = self._resolve_jq(data, self.jq_schema)
        documents: List[Any] = []
        for idx, item in enumerate(items):
            if self.text_content and isinstance(item, (str, int, float, bool)):
                page_content = str(item)
            else:
                page_content = json.dumps(item, ensure_ascii=False, indent=2)
            metadata = {
                "source": str(self.file_path),
                "type": "json_item",
                "index": idx,
                "jq_schema": self.jq_schema,
            }
            documents.append(self._make_doc(page_content=page_content, metadata=metadata))
        return documents

    def lazy_load(self) -> List[Any]:
        return self.load()

    @property
    def exists(self) -> bool:
        return self.file_path.exists()
