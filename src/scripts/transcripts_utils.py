from typing import TypedDict
import os
from docx import Document

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