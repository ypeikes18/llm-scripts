from src.agent import Agent
from src.actions.retrieve_knowledge import Search
import re
import os
from docx import Document
from src.vector_store import VectorStore


from typing import TypedDict

class Transcript(TypedDict):
    episode_number: str
    episode_title: str
    content: str

def read_docx(path: str) -> str:
    doc = Document(path)
    paragraphs = [para.text for para in doc.paragraphs]
    return "\n".join(paragraphs)


def get_files(path: str) -> list[Transcript]:
    """Given a path, get all the files in the folder along with their content."""
    files_with_content = []
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    for file in files:
        try:
            content = read_docx(os.path.join(path, file))
            files_with_content.append({
                **parse_file_name(file),
                "content": content
            })
        except Exception as e:
            print(f"Error reading file {file}: {e}")
    return files_with_content



def parse_file_name(file_name: str) -> dict[str, str]:
    """
    :param file_name: the name of the file to parse. Formatted like 
        #1 –  Miles   Brundage on the world_s desperate need for AI strategists and policy experts.docx
    :return: a dictionary with the episode number and title
    """
    # get rid of the .docx
    file_name = file_name.replace(".docx", "")
    try: 
    # split by dash
        parts = file_name.split('–')
        return {
            "episode_number": parts[0][1:].strip(),
            "episode_title": parts[1].strip()
        }
    except Exception as e:
        print(f"Error parsing file name {file_name}: {e}")
        return {
            "episode_number": "UNKNOWN",
            "episode_title": "UNKNOWN"
        }


def transcript_to_documents_metadatas(transcript: Transcript, kernel_size: int = 3):
    chunks = [sub.strip() for sub in transcript["content"].split("\n") if sub != ""]
    metadatas = []
    documents = []
    for i in range(len(chunks)):
        chunk = "".join(chunks[i:i+kernel_size])
        documents.append(chunk)
        metadatas.append({
                'episode_title': transcript["episode_title"],
                'episode_number': transcript["episode_number"],
                'episode_chunk_number': str(i+1),
            }
        )
    return documents, metadatas


def main():
    vector_store = VectorStore()
    transcripts = get_files("./transcripts")
    chunk_lens = []
    episode_lens = []
    for transcript in transcripts:
        print(f"title: {transcript['episode_title']} length: {len(transcript['content'])}")
        chunk_lens = []
        documents, metadatas = transcript_to_documents_metadatas(transcript)
        chunk_lens.extend([len(chunk) for chunk in documents])
        episode_lens.append(sum(chunk_lens))
        continue
        vector_store.add_documents(documents, metadatas)
    breakpoint()
if __name__ == "__main__":
    main()
