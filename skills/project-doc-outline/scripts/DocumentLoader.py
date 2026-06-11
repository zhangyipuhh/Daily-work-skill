#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
DocumentLoader 模块（project-doc-query skill 自带 - 独立自包含版）

通用文件加载工具，支持多种文件类型的智能加载。
- 8 种 Loader：Word / PDF / Text / Markdown / CSV / JSON / Eml / Excel
- 单文件或批量文件夹加载
- 自动识别文件类型并选择对应的加载器
- langchain_core 是可选依赖

调用方式（同 skill 内）：
    from DocumentLoader import DocumentLoader, LOADER_MAPPING, ExcelLoader
    # 或者从子包
    from loader import WordLoader, PDFLoader, EmlLoader

Date: 2026-06-10
Author: project-doc skill 套件（原作者 张镠谱）
"""

from pathlib import Path
from typing import Union, List, Dict, Optional, Type, Any
import importlib

# langchain_core 是可选依赖
try:
    from langchain_core.documents import Document  # type: ignore
except Exception:
    Document = None  # type: ignore


class _SimpleDoc:
    """当 langchain_core 不可用时使用的轻量 Document 替身。"""
    __slots__ = ("page_content", "metadata")

    def __init__(self, page_content: str = "", metadata: Optional[Dict[str, Any]] = None):
        self.page_content = page_content
        self.metadata = metadata or {}


# 从同包 loader 子包导入所有 Loader
from loader import (  # noqa: E402
    WordLoader, PDFLoader, TextLoader, MarkdownLoader,
    CSVLoader, JSONLoader, EmlLoader, ExcelLoader,
)


# 文件扩展名 → 加载器类 映射表
LOADER_MAPPING: Dict[str, Any] = {
    # 文本文件
    '.txt': TextLoader,
    '.md': MarkdownLoader,
    '.markdown': MarkdownLoader,

    # 文档
    '.pdf': PDFLoader,
    '.docx': WordLoader,
    '.doc': WordLoader,

    # 数据文件
    '.csv': CSVLoader,
    '.json': JSONLoader,

    # 邮件
    '.eml': EmlLoader,

    # project-doc 套件自带：Excel
    '.xlsx': ExcelLoader,
    '.xlsm': ExcelLoader,
}

# 各加载器的默认参数配置
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
    '.xlsx': {'data_only': True, 'include_hidden': False, 'sheet_name': None, 'keyword': None, 'row_range': None},
    '.xlsm': {'data_only': True, 'include_hidden': False, 'sheet_name': None, 'keyword': None, 'row_range': None},
}


class DocumentLoader:
    """
    通用文件加载器

    Attributes:
        path: 文件或文件夹路径
        glob: 批量加载时的匹配规则
        silent_errors: 是否跳过加载失败的文件
    """

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

            # 统一补充 metadata
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


# ========== 使用示例 ==========

if __name__ == "__main__":
    import sys
    test_files = [
        r"D:\项目文档\202410-C0008-泊头市关于开展地籍调查省级示范点建设项目\01_项目策划\~$(...)策划表V1.0.xlsm",
    ]
    # 实际测试在 _test.py 中跑
