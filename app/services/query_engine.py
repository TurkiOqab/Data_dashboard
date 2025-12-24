"""
Query Engine Service

Handles natural language queries over slide content.
Combines semantic search with LLM-powered response generation.
"""

import os
from typing import List, Dict, Any, Optional
import anthropic

from .embeddings import EmbeddingsService


class QueryEngine:
    """
    Fuzzy query engine that interprets user intent and finds relevant slides.
    """

    def __init__(
        self,
        embeddings_service: Optional[EmbeddingsService] = None,
        api_key: Optional[str] = None
    ):
        self.embeddings = embeddings_service or EmbeddingsService()
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None

        self.model = "claude-sonnet-4-20250514"

    def query(
        self,
        question: str,
        n_results: int = 5,
        include_context: bool = True
    ) -> Dict[str, Any]:
        """
        Process a natural language query and return relevant information.

        Args:
            question: User's question in natural language
            n_results: Number of relevant slides to retrieve
            include_context: Whether to include full slide context

        Returns:
            Dict with answer, relevant_slides, and confidence
        """
        # Step 1: Semantic search for relevant slides
        relevant_slides = self.embeddings.search(question, n_results=n_results)

        if not relevant_slides:
            return {
                "answer": "I couldn't find any relevant information in the uploaded slides. Please make sure you've uploaded a presentation.",
                "relevant_slides": [],
                "confidence": 0.0
            }

        # Step 2: Generate response using LLM if available
        if self.client:
            answer = self._generate_response(question, relevant_slides)
        else:
            # Fallback without LLM
            answer = self._generate_simple_response(question, relevant_slides)

        return {
            "answer": answer,
            "relevant_slides": relevant_slides,
            "confidence": self._calculate_confidence(relevant_slides)
        }

    def _generate_response(
        self,
        question: str,
        relevant_slides: List[Dict[str, Any]]
    ) -> str:
        """Generate a response using Claude."""
        # Build context from relevant slides
        context_parts = []
        for slide in relevant_slides:
            metadata = slide.get('metadata', {})
            slide_num = metadata.get('slide_number', '?')
            filename = metadata.get('filename', 'Unknown')

            context_parts.append(
                f"[Slide {slide_num} from {filename}]\n{slide.get('content', '')}"
            )

        context = "\n\n---\n\n".join(context_parts)

        prompt = f"""You are an intelligent assistant helping users find information from presentation slides.

Based on the following slide content, answer the user's question.
- Be concise but thorough
- Reference specific slides when relevant (e.g., "As shown in Slide 3...")
- If the information isn't in the slides, say so
- If you can extract data points, present them clearly
- If the user asks about charts/visualizations, describe what the slides indicate

SLIDE CONTENT:
{context}

USER QUESTION: {question}

ANSWER:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text

    def _generate_simple_response(
        self,
        question: str,
        relevant_slides: List[Dict[str, Any]]
    ) -> str:
        """Generate a simple response without LLM (fallback)."""
        response_parts = [
            f"Found {len(relevant_slides)} relevant slide(s) for your query:\n"
        ]

        for slide in relevant_slides:
            metadata = slide.get('metadata', {})
            slide_num = metadata.get('slide_number', '?')
            title = metadata.get('title', 'Untitled')

            response_parts.append(f"\n**Slide {slide_num}: {title}**")

            # Show preview of content
            content = slide.get('content', '')
            if len(content) > 300:
                content = content[:300] + "..."
            response_parts.append(content)

        return "\n".join(response_parts)

    def _calculate_confidence(self, results: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on search results."""
        if not results:
            return 0.0

        # Use inverse of average distance as confidence
        # ChromaDB returns L2 distance, lower is better
        distances = [r.get('distance', 1.0) for r in results]
        avg_distance = sum(distances) / len(distances)

        # Convert to 0-1 confidence score
        # Typical distances range from 0.5 (very similar) to 2.0 (dissimilar)
        confidence = max(0.0, min(1.0, 1.0 - (avg_distance / 2.0)))

        return round(confidence, 2)

    def expand_query(self, question: str) -> List[str]:
        """
        Expand a query into multiple search terms for better coverage.
        Uses LLM to understand intent and generate variations.
        """
        if not self.client:
            return [question]

        prompt = f"""Given this user question about presentation slides, generate 3 alternative search queries that might help find relevant information.
Return only the queries, one per line.

Question: {question}

Alternative queries:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=200,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        alternatives = message.content[0].text.strip().split('\n')
        return [question] + [q.strip() for q in alternatives if q.strip()]

    def generate_example_questions(self, num_questions: int = 6, lang: str = 'en') -> List[str]:
        """
        Generate contextual example questions based on the indexed slides.

        Args:
            num_questions: Number of questions to generate
            lang: Language code ('en' or 'ar')

        Returns:
            List of example questions
        """
        if not self.client:
            return []

        # Get a sample of slide content to understand the presentation
        sample_results = self.embeddings.search("main topics key points data", n_results=5)

        if not sample_results:
            return []

        # Build context from sample slides
        context_parts = []
        for slide in sample_results:
            content = slide.get('content', '')[:300]
            context_parts.append(content)

        context = "\n---\n".join(context_parts)

        lang_instruction = "in Arabic (العربية)" if lang == 'ar' else "in English"

        prompt = f"""Based on this presentation content, generate {num_questions} natural questions that a user might ask {lang_instruction}.

PRESENTATION CONTENT:
{context}

Generate questions that:
- Are specific to the actual content shown
- Cover different aspects (data, summaries, comparisons, specific slides)
- Sound natural and conversational
- Would help someone explore the presentation

Return ONLY the questions, one per line, no numbering or bullets."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            questions = message.content[0].text.strip().split('\n')
            # Clean up and filter empty lines
            questions = [q.strip() for q in questions if q.strip()]
            return questions[:num_questions]

        except Exception:
            return []

    def chat(
        self,
        message: str,
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Handle a chat message with conversation context.

        Args:
            message: Current user message
            chat_history: List of previous messages [{"role": "user/assistant", "content": "..."}]

        Returns:
            Response with answer and relevant slides
        """
        # Get relevant slides for the current message
        result = self.query(message, n_results=5)

        if not self.client:
            return result

        # Build conversation with context
        context_parts = []
        for slide in result['relevant_slides']:
            metadata = slide.get('metadata', {})
            context_parts.append(
                f"[Slide {metadata.get('slide_number', '?')}] {slide.get('content', '')[:500]}"
            )

        system_prompt = f"""You are an intelligent assistant helping users explore and understand presentation slides.

Available slide content:
{chr(10).join(context_parts)}

Guidelines:
- Answer questions based on the slide content above
- Be conversational and helpful
- Reference specific slides when relevant
- If asked about data/charts, describe what's shown
- If information isn't available, say so politely
- Keep responses concise but informative"""

        # Build messages
        messages = []
        if chat_history:
            for msg in chat_history[-10:]:  # Keep last 10 messages for context
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        messages.append({"role": "user", "content": message})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            system=system_prompt,
            messages=messages
        )

        result['answer'] = response.content[0].text
        return result
