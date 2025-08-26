"""Custom spacy-llm task for detecting and merging related thought chunks"""

from typing import List, Dict, Any, Tuple, Optional, Callable
import spacy
from spacy.tokens import Doc
from spacy_llm.registry import registry
from spacy_llm.tasks import BuiltinTask
from spacy_llm.util import split_labels
import logging

logger = logging.getLogger(__name__)

class ChunkRelationship:
    """Data class for chunk relationship information"""
    def __init__(self, chunk1_id: int, chunk2_id: int, confidence: float, relationship_type: str):
        self.chunk1_id = chunk1_id
        self.chunk2_id = chunk2_id
        self.confidence = confidence
        self.relationship_type = relationship_type

class ChunkRelationshipTask(BuiltinTask[List[ChunkRelationship]]):
    """Custom task to detect semantic relationships between text chunks"""
    
    def __init__(
        self,
        confidence_threshold: float = 0.7,
        max_chunk_distance: int = 3,
        template: str = "",
        parse_responses: Optional[Callable[[List[Doc]], List[ChunkRelationship]]] = None,
        prompt_example_type: str = "chunk_relationship",
        **kwargs
    ):
        self.confidence_threshold = confidence_threshold
        self.max_chunk_distance = max_chunk_distance
        
        # Default template for relationship detection
        if not template:
            template = self._get_default_template()
        
        if parse_responses is None:
            parse_responses = self._parse_responses
            
        super().__init__(
            template=template,
            parse_responses=parse_responses,
            prompt_example_type=prompt_example_type,
            **kwargs
        )

    def _get_default_template(self) -> str:
        """Get the default Jinja2 template for chunk relationship detection"""
        return """
You are analyzing text chunks to identify semantic relationships. 
Your task is to determine if two text segments discuss the same topic, person, or concept.

Given the following two text chunks, analyze their semantic relationship:

Chunk 1: "{{chunk1}}"
Chunk 2: "{{chunk2}}"

Consider these relationship types:
- SAME_TOPIC: Both chunks discuss the same subject matter
- SAME_PERSON: Both chunks mention or discuss the same person
- SAME_EVENT: Both chunks refer to the same event or situation
- CAUSE_EFFECT: One chunk describes a cause, the other an effect
- TEMPORAL_SEQUENCE: The chunks describe events in temporal order
- NONE: No meaningful relationship

Respond with:
RELATIONSHIP: [relationship_type]
CONFIDENCE: [0.0 to 1.0]
REASONING: [brief explanation]

Example:
Chunk 1: "My boss won't leave me alone about the report"
Chunk 2: "She has been riding me a lot lately - I think she's trying to get me fired"
RELATIONSHIP: SAME_PERSON
CONFIDENCE: 0.95
REASONING: Both chunks discuss the same boss and her behavior toward the speaker.
""".strip()

    def generate_prompts(self, docs: List[Doc]) -> List[str]:
        """Generate prompts for relationship detection between chunks"""
        prompts = []
        
        for doc in docs:
            # Extract chunks from doc (assuming they're stored in doc._.chunks)
            chunks = getattr(doc._, 'chunks', [])
            
            if len(chunks) < 2:
                continue
                
            # Compare each chunk with nearby chunks
            for i, chunk1 in enumerate(chunks):
                for j in range(i + 1, min(i + self.max_chunk_distance + 1, len(chunks))):
                    chunk2 = chunks[j]
                    
                    # Create prompt for this chunk pair
                    prompt = self._template.render(
                        chunk1=chunk1.get('text', ''),
                        chunk2=chunk2.get('text', '')
                    )
                    prompts.append(prompt)
        
        return prompts

    def _parse_responses(self, docs: List[Doc], responses: List[str]) -> List[List[ChunkRelationship]]:
        """Parse LLM responses to extract chunk relationships"""
        all_relationships = []
        
        response_idx = 0
        for doc in docs:
            doc_relationships = []
            chunks = getattr(doc._, 'chunks', [])
            
            if len(chunks) < 2:
                all_relationships.append(doc_relationships)
                continue
            
            # Process responses for this document
            for i in range(len(chunks)):
                for j in range(i + 1, min(i + self.max_chunk_distance + 1, len(chunks))):
                    if response_idx >= len(responses):
                        break
                        
                    try:
                        relationship = self._parse_single_response(responses[response_idx], i, j)
                        if relationship and relationship.confidence >= self.confidence_threshold:
                            doc_relationships.append(relationship)
                    except Exception as e:
                        logger.warning(f"Failed to parse relationship response: {e}")
                    
                    response_idx += 1
            
            all_relationships.append(doc_relationships)
        
        return all_relationships

    def _parse_single_response(self, response: str, chunk1_id: int, chunk2_id: int) -> Optional[ChunkRelationship]:
        """Parse a single LLM response for chunk relationship"""
        try:
            lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
            
            relationship_type = "NONE"
            confidence = 0.0
            
            for line in lines:
                if line.startswith("RELATIONSHIP:"):
                    relationship_type = line.split(":", 1)[1].strip()
                elif line.startswith("CONFIDENCE:"):
                    confidence_str = line.split(":", 1)[1].strip()
                    try:
                        confidence = float(confidence_str)
                    except ValueError:
                        confidence = 0.0
            
            if relationship_type != "NONE" and confidence > 0:
                return ChunkRelationship(chunk1_id, chunk2_id, confidence, relationship_type)
                
        except Exception as e:
            logger.warning(f"Error parsing response: {e}")
        
        return None

    def assign_to_doc(self, doc: Doc, relationships: List[ChunkRelationship]) -> None:
        """Assign relationships to the spaCy doc"""
        if not Doc.has_extension("chunk_relationships"):
            Doc.set_extension("chunk_relationships", default=[])
        
        doc._.chunk_relationships = relationships

def merge_related_chunks(chunks: List[Dict[str, Any]], relationships: List[ChunkRelationship]) -> List[Dict[str, Any]]:
    """Merge chunks that are identified as related"""
    if not relationships:
        return chunks
    
    # Build a graph of relationships
    chunk_graph = {i: set() for i in range(len(chunks))}
    for rel in relationships:
        chunk_graph[rel.chunk1_id].add(rel.chunk2_id)
        chunk_graph[rel.chunk2_id].add(rel.chunk1_id)
    
    # Find connected components (groups of related chunks)
    visited = set()
    merged_groups = []
    
    for i in range(len(chunks)):
        if i not in visited:
            # DFS to find all connected chunks
            group = set()
            stack = [i]
            
            while stack:
                node = stack.pop()
                if node not in visited:
                    visited.add(node)
                    group.add(node)
                    for neighbor in chunk_graph[node]:
                        if neighbor not in visited:
                            stack.append(neighbor)
            
            merged_groups.append(sorted(group))
    
    # Create merged chunks
    merged_chunks = []
    
    for group in merged_groups:
        if len(group) == 1:
            # Single chunk, no merging needed
            merged_chunks.append(chunks[group[0]])
        else:
            # Merge multiple chunks
            merged_text_parts = []
            merged_keywords = set()
            total_confidence = 0
            min_start_char = float('inf')
            max_end_char = 0
            
            for chunk_id in group:
                chunk = chunks[chunk_id]
                merged_text_parts.append(chunk['text'])
                merged_keywords.update(chunk.get('topic_keywords', []))
                total_confidence += chunk.get('confidence', 0)
                min_start_char = min(min_start_char, chunk.get('start_char', 0))
                max_end_char = max(max_end_char, chunk.get('end_char', 0))
            
            # Create merged chunk
            merged_chunk = {
                'id': min(group),  # Use the ID of the first chunk
                'text': ' ... '.join(merged_text_parts),
                'confidence': total_confidence / len(group),
                'start_char': min_start_char,
                'end_char': max_end_char,
                'topic_keywords': list(merged_keywords),
                'sentiment': chunks[group[0]].get('sentiment', 'neutral'),
                'merged_from': group,  # Track which chunks were merged
                'relationship_count': len([r for r in relationships if r.chunk1_id in group or r.chunk2_id in group])
            }
            
            merged_chunks.append(merged_chunk)
    
    return merged_chunks

# Register the task with spacy-llm
@registry.llm_tasks("thoughtrambler.chunk_relationship.v1")
def make_chunk_relationship_task(
    confidence_threshold: float = 0.7,
    max_chunk_distance: int = 3,
    template: str = "",
    examples: Optional[List[Dict[str, str]]] = None,
) -> ChunkRelationshipTask:
    """Factory function to create ChunkRelationshipTask"""
    return ChunkRelationshipTask(
        confidence_threshold=confidence_threshold,
        max_chunk_distance=max_chunk_distance,
        template=template,
        examples=examples or []
    )