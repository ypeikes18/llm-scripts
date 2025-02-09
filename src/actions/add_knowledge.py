from typing import Any, TypeAlias
from dataclasses import dataclass, field
from src.actions.action import Action, JsonDict
from src.vector_store import VectorStore

Metadata: TypeAlias = dict[str, str]

@dataclass
class Knowledge(Action):
    name: str = "add_knowledge"
    config: JsonDict = field(default_factory=lambda: {
        "type": "function",
        "function": {
            "name": "add_knowledge",
            "description": "Add new information to the knowledge base",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content to add to the knowledge base"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata about the content",
                        "properties": {
                            "source": {
                                "type": "string",
                                "description": "Source of the information"
                            },
                            "topic": {
                                "type": "string",
                                "description": "Topic or category of the information"
                            }
                        }
                    }
                },
                "required": ["content"]
            }
        }
    })
    
    def add_context(self, agent):
        self._vector_store = agent.vector_store

    def execute_function(self, content: str, metadata: Metadata | None = None) -> str:
        """
        Add new information to the knowledge base.
        
        Args:
            content: Content to add to the knowledge base
            metadata: Optional metadata about the content
            
        Returns:
            Document ID of the added content
        """
        if metadata is None:
            metadata = {"source": "user_input", "topic": "general"}
            
        # Generate a unique document ID
        doc_id = f"doc_{len(self._vector_store.list_collections())}"
        
        # Add the document to the vector store
        self._vector_store.add_documents(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        return f"Added document with ID: {doc_id}" 