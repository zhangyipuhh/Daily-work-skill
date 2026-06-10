#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
PDFLoader 模块（project-doc-query skill 自带）

忠实复制自原版，已改造：
- 替代 langchain_community.PyPDFLoader 为纯 Python 的 pypdf
- 每页一个 Document（含扫描件检测：page_content 长度 < 100 字符视为扫描件）
- langchain_core 可选

Date: 2026-06-10
Author: project-doc skill 套件（原作者 张镠谱）
"""

from pathlib import Path
from typing import List, Any, Dict

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None  # type: ignore

try:
    from langchain_core.documents import Document  # type: ignore
except Exception:
    Document = None  # type: ignore


class _SimpleDoc:
    __slots__ = ("page_content", "metadata")

    def __init__(self, page_content: str = "", metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}


class PDFLoader:
    """PDF 文件加载器（基于 pypdf）"""

    LOADER_NAME = "PDFLoader"

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._reader = None

    def _get_reader(self):
        if PdfReader is None:
            raise ImportError("缺少依赖 pypdf，请先安装：pip install pypdf")
        if self._reader is None:
            if not self.file_path.exists():
                raise FileNotFoundError(f"文件不存在: {self.file_path}")
            self._reader = PdfReader(str(self.file_path))
        return self._reader

    def _make_doc(self, page_content: str, metadata: Dict[str, Any]):
        DocCls = Document if Document is not None else _SimpleDoc
        return DocCls(page_content=page_content, metadata=metadata)

    def load(self) -> List[Any]:
        """加载 PDF：每页一个 Document"""
        reader = self._get_reader()
        documents: List[Any] = []
        for page_idx, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
            except Exception as e:
                text = ""

            metadata = {
                "source": str(self.file_path),
                "type": "pdf_page",
                "page": page_idx + 1,
                "page_count": len(reader.pages),
                "text_length": len(text),
                # 扫描件提示：调用方用此字段判断
                "is_scanned": len(text.strip()) < 100,
            }
            documents.append(self._make_doc(page_content=text, metadata=metadata))
        return documents

    def lazy_load(self) -> List[Any]:
        return self.load()

    @property
    def exists(self) -> bool:
        return self.file_path.exists()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python PDFLoader.py <pdf_path>")
        sys.exit(1)
    loader = PDFLoader(sys.argv[1])
    if loader.exists:
        docs = loader.load()
        print(f"加载 {len(docs)} 页")
        for d in docs:
            tag = "[扫描件]" if d.metadata.get("is_scanned") else "[文本]"
            print(f"  {tag} p{d.metadata['page']} 文本长度={d.metadata['text_length']}")
    else:
        print(f"文件不存在: {loader.file_path}")
