#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
TextLoader 模块（project-doc-query skill 自带）

忠实复制自原版，已改造：
- 替代 langchain_community.TextLoader 为 Python open()
- 保留 chardet 自动检测编码（缺失时回退 utf-8/gb18030 试探）
- 整个文件为 1 个 Document

Date: 2026-06-10
Author: project-doc skill 套件（原作者 张镠谱）
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


class TextLoader:
    LOADER_NAME = "TextLoader"

    def __init__(self, file_path: str, encoding: str = "utf-8"):
        self.file_path = Path(file_path)
        self.encoding = encoding
        self._detected_encoding: str = ""

    def _detect_encoding(self) -> str:
        """自动检测编码：chardet 优先，否则 utf-8/gb18030 试探"""
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
            self._detected_encoding = self._detect_encoding()
        with open(self.file_path, "r", encoding=self._detected_encoding) as f:
            text = f.read()
        metadata = {
            "source": str(self.file_path),
            "type": "text",
            "encoding": self._detected_encoding,
            "length": len(text),
        }
        return [self._make_doc(page_content=text, metadata=metadata)]

    def lazy_load(self) -> List[Any]:
        return self.load()

    @property
    def exists(self) -> bool:
        return self.file_path.exists()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python TextLoader.py <txt_path>")
        sys.exit(1)
    loader = TextLoader(sys.argv[1])
    if loader.exists:
        docs = loader.load()
        print(f"加载 {len(docs)} 个片段，编码={docs[0].metadata['encoding']}")
    else:
        print(f"文件不存在: {loader.file_path}")
