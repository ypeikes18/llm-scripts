from typing import Any, TypeAlias
from dataclasses import dataclass, field
from src.actions.action import Action, JsonDict

SearchResult: TypeAlias = dict[str, str | dict[str, Any] | float]

@dataclass
class Search(Action):
    name: str = "search_knowledge"
    config: JsonDict = field(default_factory=lambda: {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "Search for information in the vector database",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        }
    })

    def add_context(self, agent):
        self._vector_store = agent.vector_store

    def execute_function(self, query: str, n_results: int = 3) -> list[SearchResult]:
        """
        Search for information in the vector database.
        
        Args:
            query: Search query string
            n_results: Number of results to return
            
        Returns:
            List of search results with content, metadata, and distance
        """
        results = self._vector_store.search_similar(query, n_results=n_results)
        return [
            {
                "content": doc,
                "metadata": meta,
                "distance": dist
            }

            for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )
        ] 