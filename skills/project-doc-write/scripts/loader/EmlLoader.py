#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
EmlLoader 模块（project-doc-write skill 自带）

Date: 2026-06-10
Author: project-doc skill 套件
"""

from pathlib import Path
from typing import List, Any, Dict
import email
from email import policy
from email.header import decode_header, make_header
from email.utils import getaddresses

try:
    from langchain_core.documents import Document  # type: ignore
except Exception:
    Document = None  # type: ignore


class _SimpleDoc:
    __slots__ = ("page_content", "metadata")

    def __init__(self, page_content: str = "", metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}


def _decode_header_value(value: str) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return value


def _extract_body(msg) -> str:
    plain_texts: List[str] = []
    html_texts: List[str] = []
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            if "attachment" in content_disposition.lower():
                continue
            try:
                payload = part.get_payload(decode=True)
            except Exception:
                continue
            if payload is None:
                continue
            charset = part.get_content_charset() or "utf-8"
            try:
                decoded = payload.decode(charset, errors="ignore")
            except Exception:
                decoded = payload.decode("utf-8", errors="ignore")
            if content_type == "text/plain":
                plain_texts.append(decoded)
            elif content_type == "text/html":
                html_texts.append(decoded)
    else:
        content_type = msg.get_content_type()
        try:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or "utf-8"
            decoded = payload.decode(charset, errors="ignore") if payload else ""
        except Exception:
            decoded = ""
        if content_type == "text/plain":
            plain_texts.append(decoded)
        elif content_type == "text/html":
            html_texts.append(decoded)
    if plain_texts:
        return "\n\n".join(plain_texts)
    if html_texts:
        import re
        text = "\n\n".join(html_texts)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&lt;", "<", text)
        text = re.sub(r"&gt;", ">", text)
        text = re.sub(r"&amp;", "&", text)
        return text
    return ""


class EmlLoader:
    LOADER_NAME = "EmlLoader"

    def __init__(self, file_path: str, prefer_encoding: str = "utf-8"):
        self.file_path = Path(file_path)
        self.prefer_encoding = prefer_encoding
        self._msg = None

    def _parse(self):
        if self._msg is None:
            if not self.file_path.exists():
                raise FileNotFoundError(f"文件不存在: {self.file_path}")
            raw = self.file_path.read_bytes()
            for enc in (self.prefer_encoding, "utf-8", "gb18030", "gbk", "latin-1"):
                try:
                    text = raw.decode(enc)
                    break
                except Exception:
                    continue
            else:
                text = raw.decode("utf-8", errors="ignore")
            self._msg = email.message_from_string(text, policy=policy.default)
        return self._msg

    def _make_doc(self, page_content: str, metadata: Dict[str, Any]):
        DocCls = Document if Document is not None else _SimpleDoc
        return DocCls(page_content=page_content, metadata=metadata)

    def load(self) -> List[Any]:
        msg = self._parse()
        subject = _decode_header_value(str(msg.get("Subject", "")))
        from_ = _decode_header_value(str(msg.get("From", "")))
        to_raw = str(msg.get("To", ""))
        cc_raw = str(msg.get("Cc", ""))
        date = str(msg.get("Date", ""))
        message_id = str(msg.get("Message-ID", ""))
        to_addrs = [name for name, addr in getaddresses([to_raw, cc_raw]) if name or addr]
        to = ", ".join(to_addrs) if to_addrs else (to_raw + (", " + cc_raw if cc_raw else ""))
        attachments: List[str] = []
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))
                if "attachment" in content_disposition.lower():
                    filename = part.get_filename()
                    if filename:
                        attachments.append(_decode_header_value(filename))
        body = _extract_body(msg)
        page_content = (
            f"## 主题\n{subject}\n\n"
            f"## 发件人\n{from_}\n\n"
            f"## 收件人\n{to}\n\n"
            f"## 日期\n{date}\n\n"
            f"## 正文\n{body}"
        )
        metadata = {
            "source": str(self.file_path),
            "type": "eml",
            "subject": subject,
            "from": from_,
            "to": to,
            "date": date,
            "message_id": message_id,
            "attachments": attachments,
            "body_length": len(body),
            "is_scanned": len(body.strip()) < 100,
        }
        return [self._make_doc(page_content=page_content, metadata=metadata)]

    def lazy_load(self) -> List[Any]:
        return self.load()

    @property
    def exists(self) -> bool:
        return self.file_path.exists()
