#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
DocumentLoader 模块（project-doc-write skill 自带 - 独立自包含版）

与 project-doc-query/scripts/DocumentLoader.py 同构（独立副本）。
8 种 Loader：Word / PDF / Text / Markdown / CSV / JSON / Eml / Excel。

Date: 2026-06-10
Author: project-doc skill 套件
"""

from pathlib import Path
from typing import Union, List, Dict, Optional, Type, Any

# langchain_core 是可选依赖
try:
    from langchain_core.documents import Document  # type: ignore
except Exception:
    Document = None  # type: ignore


class _SimpleDoc:
    __slots__ = ("page_content", "metadata")

    def __init__(self, page_content: str = "", metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}


from loader import (  # noqa: E402
    WordLoader, PDFLoader, TextLoader, MarkdownLoader,
    CSVLoader, JSONLoader, EmlLoader, ExcelLoader,
)


LOADER_MAPPING: Dict[str, Any] = {
    '.txt': TextLoader,
    '.md': MarkdownLoader,
    '.markdown': MarkdownLoader,
    '.pdf': PDFLoader,
    '.docx': WordLoader,
    '.doc': WordLoader,
    '.csv': CSVLoader,
    '.json': JSONLoader,
    '.eml': EmlLoader,
    '.xlsx': ExcelLoader,
    '.xlsm': ExcelLoader,
}

LOADER_DEFAULT_KWARGS: Dict[str, Dict[str, Any]] = {
    '.txt': {'encoding': 'utf-8'},
    '.md': {},
    '.markdown': {},
    '.pdf': {},
    '.docx': {'load_method': 'default'},
    '.doc': {'load_method': 'default'},
    '.csv': {'encoding': 'utf-8'},
    '.json': {'jq_schema': '.[]', 'text_content': False},
    '.eml': {'prefer_encoding': 'utf-8'},
    '.xlsx': {'data_only': True, 'include_hidden': False},
    '.xlsm': {'data_only': True, 'include_hidden': False},
}


class DocumentLoader:
    def __init__(
        self,
        path: Union[str, Path],
        glob: str = "**/*",
        silent_errors: bool = True,
        custom_mapping: Optional[Dict[str, Type]] = None,
        custom_kwargs: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        self.path = Path(path)
        self.glob = glob
        self.silent_errors = silent_errors
        self.mapping = {**LOADER_MAPPING, **(custom_mapping or {})}
        self.kwargs_map = {**LOADER_DEFAULT_KWARGS, **(custom_kwargs or {})}

    def _get_loader_class(self, file_path: Path) -> Optional[Type]:
        ext = file_path.suffix.lower()
        return self.mapping.get(ext)

    def _get_loader_kwargs(self, file_path: Path) -> Dict[str, Any]:
        ext = file_path.suffix.lower()
        return self.kwargs_map.get(ext, {}).copy()

    def _load_single(self, file_path: Path, **override_kwargs) -> List[Any]:
        try:
            loader_cls = self._get_loader_class(file_path)
            if loader_cls is None:
                if self.silent_errors:
                    print(f"[SKIP] 不支持的文件类型: {file_path}")
                    return []
                raise ValueError(f"不支持的文件类型: {file_path.suffix}")
            kwargs = self._get_loader_kwargs(file_path)
            kwargs.update(override_kwargs)
            loader_name = loader_cls.__name__ if loader_cls else "?"
            print(f"[FILE] {file_path.name} -> {loader_name}")
            loader = loader_cls(str(file_path), **kwargs)
            docs = loader.load()
            for doc in docs:
                if hasattr(doc, "metadata") and isinstance(doc.metadata, dict):
                    doc.metadata.setdefault("source", str(file_path))
                    doc.metadata.setdefault("file_type", file_path.suffix.lower())
                    doc.metadata.setdefault("loader_used", loader_name)
            return docs
        except Exception as e:
            if self.silent_errors:
                print(f"[ERR] 跳过 {file_path}: {e}")
                return []
            raise

    def load(self, **override_kwargs) -> List[Any]:
        if self.path.is_file():
            return self._load_single(self.path, **override_kwargs)
        elif self.path.is_dir():
            all_docs = []
            for file_path in self.path.glob(self.glob):
                if not file_path.is_file():
                    continue
                ext = file_path.suffix.lower()
                if ext not in self.mapping:
                    continue
                docs = self._load_single(file_path, **override_kwargs)
                all_docs.extend(docs)
            print(f"\n[OK] 总计: {len(all_docs)} 个文档片段")
            return all_docs
        else:
            raise FileNotFoundError(f"路径不存在: {self.path}")

    def load_with_config(self, file_type: str, **kwargs) -> List[Any]:
        if self.path.is_file():
            return self._load_single(self.path, **kwargs)
        elif self.path.is_dir():
            all_docs = []
            for file_path in self.path.glob(self.glob):
                if not file_path.is_file():
                    continue
                if file_path.suffix.lower() != file_type.lower():
                    continue
                docs = self._load_single(file_path, **kwargs)
                all_docs.extend(docs)
            return all_docs
        else:
            raise FileNotFoundError(f"路径不存在: {self.path}")
