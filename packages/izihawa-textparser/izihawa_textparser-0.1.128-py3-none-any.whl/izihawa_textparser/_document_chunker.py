import dataclasses
import re
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from typing import List

from izihawa_textparser.utils import is_banned_section
from izihawa_textutils.utils import remove_markdown
from langchain_core.documents import Document
from unstructured.cleaners.core import clean

from ._text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter


@dataclass
class Chunk:
    document_id: str
    field: str
    chunk_id: int
    title: str
    text: str
    start_index: int
    length: int
    updated_at: int
    issued_at: int | None = None
    type: str | None = None
    language: str | None = None
    issns: list[str] | None = None


@dataclass
class StoredChunk:
    document_id: str
    field: str
    chunk_id: int
    title: str
    start_index: int
    length: int
    updated_at: int
    issued_at: int | None = None
    type: str | None = None
    language: str | None = None
    issns: list[str] | None = None


def extract_title_parts(document: dict, split):
    title_parts = []
    if "title" in document:
        title_parts.append(document["title"])
    for hn in range(1, 7):
        if hn_value := split.metadata.get(f"h{hn}"):
            title_parts.append(hn_value)
    return title_parts


def length_function(remove_tables: bool, text: str):
    return len(remove_markdown(text, remove_tables=remove_tables))


def merge_chunks(a: Chunk, b: Chunk) -> Chunk:
    if a.chunk_id > b.chunk_id:
        t = a
        a = b
        b = t
    new_chunk = Chunk(**dataclasses.asdict(a))
    new_chunk.length = b.start_index - a.start_index + b.length
    new_chunk.text = a.text + "\n\n" + b.text
    return new_chunk


def _is_table(text: str):
    return "\\begin{tabular}" in text or (text.startswith("|") and text.endswith("|"))


def _get_language(document: dict):
    return document["languages"][0] if "languages" in document else None


def is_jdk(language: str) -> bool:
    return language in ['zh', 'ko', 'ja']


class DocumentChunker:
    def __init__(
        self,
        chunk_size: int = 1024,
        chunk_overlap: int = 128,
        min_chunk_length: int = 128,
        add_metadata: bool = False,
        add_year: bool = False,
        return_each_line: bool = False,
        remove_tables: bool = False,
        strip_whitespace: bool = True,
        separators: list[str] | None = None,
    ):
        if separators is None:
            separators = ["\n\n", "\n", ". ", " ", ""]
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            keep_separator=True,
            strip_whitespace=strip_whitespace,
            length_function=partial(length_function, remove_tables),
            separators=separators,
        )
        self._jkc_text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=int(chunk_size / 2),
            chunk_overlap=int(chunk_overlap / 2),
            keep_separator=True,
            strip_whitespace=strip_whitespace,
            length_function=partial(length_function, remove_tables),
            separators=separators,
        )
        self._markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "h1"),
                ("##", "h2"),
                ("###", "h3"),
                ("####", "h4"),
                ("#####", "h5"),
                ("######", "h6"),
            ],
            return_each_line=return_each_line,
        )
        self._chunk_overlap = chunk_overlap
        self._min_chunk_length = min_chunk_length
        self._add_metadata = add_metadata
        self._add_year = add_year
        self._remove_tables = remove_tables

    def _is_figure_header(self, text: str, min_chunk_length: int | None = None):
        if min_chunk_length is None:
            min_chunk_length = self._min_chunk_length
        return bool(re.search(r"^[Tt]ab(le|\.)", text)) or len(text) < min_chunk_length

    def _splits_to_chunks(self, document: dict, field: str, splits):
        chunks = []
        min_chunk_length = self._min_chunk_length
        if is_jdk(_get_language(document)):
            min_chunk_length = int(min_chunk_length / 2)
        for chunk_id, split in enumerate(splits):
            page_content = str(split.page_content)
            chunk_text = clean(
                remove_markdown(page_content, remove_tables=self._remove_tables),
                extra_whitespace=True,
                dashes=True,
                bullets=True,
                trailing_punctuation=True,
            )
            title_parts = extract_title_parts(document, split)
            parts = [chunk_text]

            if self._add_metadata:
                parts.append(f'TITLE: {" ".join(title_parts)}')
            if (
                self._add_year
                and "issued_at" in document
                and document["issued_at"] != -62135596800
            ):
                issued_at = datetime.fromtimestamp(document["issued_at"], tz=None)
                parts.append(f"YEAR: {issued_at.year}")

            chunk = Chunk(
                document_id=document["id"],
                field=field,
                chunk_id=chunk_id,
                start_index=split.metadata["start_index"],
                length=len(page_content),
                issued_at=document.get("issued_at"),
                updated_at=document["updated_at"],
                type=document.get("type"),
                language=_get_language(document),
                title="\n".join(title_parts),
                text="\n".join(parts),
                issns=document.get('metadata', {}).get('issns'),
            )

            if any(is_banned_section(title_part) for title_part in title_parts):
                continue

            while chunks and (
                (_is_table(chunk.text) and self._is_figure_header(chunks[-1].text, min_chunk_length=min_chunk_length))
                or (self._is_figure_header(chunk.text, min_chunk_length=min_chunk_length) and _is_table(chunks[-1].text))
            ):
                chunk = merge_chunks(chunks[-1], chunk)
                chunks.pop(len(chunks) - 1)

            chunks.append(chunk)

        filtered_chunks = [chunk for chunk in chunks if len(chunk.text) >= min_chunk_length]
        return filtered_chunks

    def markdown_to_splits(self, text: str) -> list[Document]:
        return self._markdown_splitter.split_text(text)

    def text_to_splits(self, text: str, language: str) -> list[Document]:
        if is_jdk(language):
            return self._jkc_text_splitter.split_documents(
                self.markdown_to_splits(text)
            )
        else:
            return self._text_splitter.split_documents(
                self.markdown_to_splits(text)
            )

    def text_to_chunks(self, document, field):
        return self._splits_to_chunks(
            document,
            field,
            self.text_to_splits(document.get(field, ""), _get_language(document)),
        )

    def document_to_chunks(self, document: dict) -> List[Chunk]:
        return [
            *self.text_to_chunks(document, "abstract"),
            *self.text_to_chunks(document, "content"),
        ]

    def splits_to_text(self, splits) -> list[str]:
        previous_header = {}
        text_parts = []
        for split in splits:
            text = ""
            current_header = split.metadata
            for i in range(1, 7):
                h = f"h{i}"
                if previous_header.get(h) == current_header.get(h):
                    continue
                else:
                    for j in range(i, 7):
                        hj = f"h{j}"
                        if hj in current_header:
                            text_parts.append("#" * j + " " + current_header[hj])
                        else:
                            break
                    break
            text += split.page_content
            text_parts.append(text)
            previous_header = current_header
        return text_parts
