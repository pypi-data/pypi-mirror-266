import asyncio
import copy
import json
import os
import sys
from typing import Any

import aiofiles
import fire
import langchain
from aiobaseclient import BaseClient
from aiokit import MultipleAsyncExecution
from izihawa_netlib import ClientPool
from izihawa_textparser import DocumentChunker, GrobidParser
from izihawa_utils.file import yield_files
from langchain.text_splitter import HeaderType, LineType
from langchain_core.documents import Document


class MarkdownHeaderTextSplitter(langchain.text_splitter.MarkdownHeaderTextSplitter):
    def aggregate_lines_to_chunks(self, lines: list[LineType]) -> list[Document]:
        """Combine lines with common metadata into chunks
        Args:
            lines: Line of text / associated header metadata
        """
        aggregated_chunks: list[LineType] = []

        for line in lines:
            if (
                aggregated_chunks
                and aggregated_chunks[-1]["metadata"] == line["metadata"]
            ):
                # If the last line in the aggregated list
                # has the same metadata as the current line,
                # append the current content to the last lines's content
                aggregated_chunks[-1]["content"] += "  \n" + line["content"]
            elif (
                aggregated_chunks
                and aggregated_chunks[-1]["metadata"] != line["metadata"]
                # may be issues if other metadata is present
                and len(aggregated_chunks[-1]["metadata"]) < len(line["metadata"])
                and aggregated_chunks[-1]["content"].split("\n")[-1].startswith("#")
                and not self.strip_headers
            ):
                # If the last line in the aggregated list
                # has different metadata as the current line,
                # and has shallower header level than the current line,
                # and the last line is a header,
                # and we are not stripping headers,
                # append the current content to the last line's content
                aggregated_chunks[-1]["content"] += "  \n" + line["content"]
                # and update the last line's metadata
                aggregated_chunks[-1]["metadata"] = line["metadata"]
            else:
                # Otherwise, append the current line to the aggregated list
                aggregated_chunks.append(line)

        return [
            Document(page_content=chunk["content"], metadata=chunk["metadata"])
            for chunk in aggregated_chunks
        ]

    def split_text(self, text: str) -> list[Document]:
        """Split markdown file
        Args:
            text: Markdown file"""

        # Split the input text by newline character ("\n").
        lines = text.split("\n")
        # Final output
        lines_with_metadata: list[LineType] = []
        # Content and metadata of the chunk currently being processed
        current_content: list[str] = []
        current_metadata: dict[str, Any] = {"start_index": 0}
        next_start_index = 0
        # Keep track of the nested header structure
        # header_stack: List[Dict[str, Union[int, str]]] = []
        header_stack: list[HeaderType] = []
        initial_metadata: dict[str, str] = {}

        in_code_block = False
        shifting_whitespace_mode = False

        for line in lines:
            next_start_index += len(line) + 1
            stripped_line = line.strip()

            if shifting_whitespace_mode and not stripped_line:
                current_metadata["start_index"] += 1
            if stripped_line:
                shifting_whitespace_mode = False

            if stripped_line.startswith("```"):
                # code block in one row
                if stripped_line.count("```") >= 2:
                    in_code_block = False
                else:
                    in_code_block = not in_code_block

            if in_code_block:
                current_content.append(stripped_line)
                continue

            # Check each line against each of the header types (e.g., #, ##)
            for sep, name in self.headers_to_split_on:
                # Check if line starts with a header that we intend to split on
                if stripped_line.startswith(sep) and (
                    # Header with no text OR header is followed by space
                    # Both are valid conditions that sep is being used a header
                    len(stripped_line) == len(sep)
                    or stripped_line[len(sep)] == " "
                ):
                    # Ensure we are tracking the header as metadata
                    if name is not None:
                        # Get the current header level
                        current_header_level = sep.count("#")

                        # Pop out headers of lower or same level from the stack
                        while (
                            header_stack
                            and header_stack[-1]["level"] >= current_header_level
                        ):
                            # We have encountered a new header
                            # at the same or higher level
                            popped_header = header_stack.pop()
                            # Clear the metadata for the
                            # popped header in initial_metadata
                            if popped_header["name"] in initial_metadata:
                                initial_metadata.pop(popped_header["name"])

                        # Push the current header to the stack
                        current_metadata["start_index"] += len(stripped_line) + 1
                        shifting_whitespace_mode = True
                        header: HeaderType = {
                            "level": current_header_level,
                            "name": name,
                            "data": stripped_line[len(sep) :].strip(),
                        }
                        header_stack.append(header)
                        # Update initial_metadata with the current header
                        initial_metadata[name] = header["data"]

                    # Add the previous line to the lines_with_metadata
                    # only if current_content is not empty
                    if current_content:
                        metadata = current_metadata.copy()
                        current_metadata["start_index"] = next_start_index
                        lines_with_metadata.append(
                            {
                                "content": "\n".join(current_content),
                                "metadata": metadata,
                            }
                        )
                        current_content.clear()

                    break
            else:
                current_content.append(stripped_line)

            start_index = current_metadata["start_index"]
            current_metadata = initial_metadata.copy()
            current_metadata["start_index"] = start_index

        if current_content:
            lines_with_metadata.append(
                {"content": "\n".join(current_content), "metadata": current_metadata}
            )

        # lines_with_metadata has each line with associated header metadata
        # aggregate these into chunks based on common metadata
        if not self.return_each_line:
            return self.aggregate_lines_to_chunks(lines_with_metadata)
        else:
            return [
                Document(page_content=chunk["content"], metadata=chunk["metadata"])
                for chunk in lines_with_metadata
            ]


class RecursiveCharacterTextSplitter(
    langchain.text_splitter.RecursiveCharacterTextSplitter
):
    def create_documents(
        self, texts: list[str], metadatas: list[dict] | None = None
    ) -> list[Document]:
        """Create documents from a list of texts."""
        _metadatas = metadatas or [{}] * len(texts)
        documents = []
        for i, text in enumerate(texts):
            index = -1
            for chunk in self.split_text(text):
                metadata = copy.deepcopy(_metadatas[i])
                start_index = metadata["start_index"]
                index = text.find(chunk, index + 1)
                metadata["start_index"] = start_index + index
                new_doc = Document(page_content=chunk, metadata=metadata)
                documents.append(new_doc)
        return documents



async def process_with_grobid(sciparse, filepath, target_dir):
    async with aiofiles.open(filepath, "rb") as f:
        processed_document = await sciparse.parse_paper(await f.read())
        target_filepath = os.path.join(
            target_dir, os.path.basename(filepath).removesuffix(".pdf") + ".txt"
        )
        async with aiofiles.open(
            target_filepath,
            "w",
        ) as output:
            r = await asyncio.get_running_loop().run_in_executor(
                None, lambda: json.dumps(processed_document)
            )
            print("writing", target_filepath)
            await output.write(r)


async def process_with_nougat(nougat_client, filepath, target_dir):
    async with aiofiles.open(filepath, "rb") as f:
        nougat_response = await nougat_client.post(
            data={"file": await f.read(), "type": "application/pdf"}
        )
        target_filepath = os.path.join(
            target_dir, os.path.basename(filepath).removesuffix(".pdf") + ".txt"
        )
        async with aiofiles.open(
            target_filepath,
            "w",
        ) as output:
            print("writing", target_filepath)
            await output.write(nougat_response)


async def grobid(
    source_dir: str,
    target_dir: str,
    base_url: str = "http://127.0.0.1:8070",
    threads: int = 32,
):
    executor = MultipleAsyncExecution(threads)

    grobid_client_1 = BaseClient(base_url)
    await grobid_client_1.start()

    client_pool = ClientPool([(grobid_client_1, threads)])
    sciparse = GrobidParser(client_pool)

    for filepath in yield_files(f'{source_dir.rstrip("/")}'):
        await executor.execute(process_with_grobid(sciparse, filepath, target_dir))

    await executor.join()


async def nougat(
    source_dir: str,
    target_dir: str,
    endpoint: str = "http://localhost:8503/",
    threads: int = 2,
):
    executor = MultipleAsyncExecution(threads)

    nougat_client = BaseClient(
        endpoint,
        default_headers={
            "Accept": "application/json",
        },
    )
    await nougat_client.start()

    for filepath in yield_files(f'{source_dir.rstrip("/")}'):
        await executor.execute(process_with_nougat(nougat_client, filepath, target_dir))

    await executor.join()


async def split():
    md = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "h1"),
            ("##", "h2"),
            ("###", "h3"),
            ("####", "h4"),
            ("#####", "h5"),
            ("######", "h6"),
        ],
        return_each_line=False,
    )
    for s in md.split_text(sys.stdin.read()):
        print(s)


if __name__ == '__main__':
    fire.Fire(
        {
            "grobid": grobid,
            "nougat": nougat,
            "split": split
        }
    )
