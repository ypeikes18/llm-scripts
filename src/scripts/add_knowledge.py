from src.vector_store import VectorStore
from src.scripts.transcripts_utils import get_files, Transcript, parse_file_name


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
    

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        transcripts_path = sys.argv[1]
    else:
        transcripts_path = "./test_transcripts"

    vector_store = VectorStore()
    transcripts = get_files(transcripts_path)
    chunk_lens = []
    episode_lens = []
    for transcript in transcripts:
        print(f"title: {transcript['episode_title']} length: {len(transcript['content'])}")
        chunk_lens = []
        documents, metadatas = transcript_to_documents_metadatas(transcript)
        chunk_lens.extend([len(chunk) for chunk in documents])
        episode_lens.append(sum(chunk_lens))
        vector_store.add_documents(documents, metadatas)
