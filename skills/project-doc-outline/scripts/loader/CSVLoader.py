#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
CSVLoader 模块（project-doc-query skill 自带）

忠实复制自原版，已改造：
- 替代 langchain_community.CSVLoader 为 Python csv 模块
- 保留 chardet 编码检测
- 每行 1 个 Document

Date: 2026-06-10
Author: project-doc skill 套件（原作者 张镠谱）
"""

from pathlib import Path
from typing import List, Any, Dict
import csv

try:
    from langchain_core.documents import Document  # type: ignore
except Exception:
    Document = None  # type: ignore


class _SimpleDoc:
    __slots__ = ("page_content", "metadata")

    def __init__(self, page_content: str = "", metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}


class CSVLoader:
    LOADER_NAME = "CSVLoader"

    def __init__(self, file_path: str, encoding: str = "utf-8", source_encoding: str = None):
        self.file_path = Path(file_path)
        self.encoding = encoding
        self.source_encoding = source_encoding
        self._detected_encoding: str = ""

    def _detect_encoding(self) -> str:
        try:
            import chardet  # type: ignore
            with open(self.file_path, "rb") as f:
                raw = f.read(10000)
            result = chardet.detect(raw)
            detected = result.get("encoding")
            if detected:
                return detected
        except Exception:
            pass
        for enc in ("utf-8", "utf-8-sig", "gb18030", "gbk"):
            try:
                with open(self.file_path, "r", encoding=enc) as f:
                    f.read(1024)
                return enc
            except Exception:
                continue
        return self.encoding

    def _make_doc(self, page_content: str, metadata: Dict[str, Any]):
        DocCls = Document if Document is not None else _SimpleDoc
        return DocCls(page_content=page_content, metadata=metadata)

    def load(self) -> List[Any]:
        if not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在: {self.file_path}")
        if not self._detected_encoding:
            self._detected_encoding = self.source_encoding or self._detect_encoding()

        documents: List[Any] = []
        with open(self.file_path, "r", encoding=self._detected_encoding, newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if not rows:
            return documents

        header = rows[0]
        for row_idx, row in enumerate(rows[1:], start=1):
            page_content = " | ".join(row)
            metadata = {
                "source": str(self.file_path),
                "type": "csv_row",
                "row_index": row_idx,
                "columns": header,
                "encoding": self._detected_encoding,
            }
            documents.append(self._make_doc(page_content=page_content, metadata=metadata))

        return documents

    def lazy_load(self) -> List[Any]:
        return self.load()

    @property
    def exists(self) -> bool:
        return self.file_path.exists()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python CSVLoader.py <csv_path>")
        sys.exit(1)
    loader = CSVLoader(sys.argv[1])
    if loader.exists:
        docs = loader.load()
        print(f"加载 {len(docs)} 行，编码={docs[0].metadata['encoding'] if docs else '?'}")
    else:
        print(f"文件不存在: {loader.file_path}")
