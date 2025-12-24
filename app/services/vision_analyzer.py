"""
Vision Analyzer Service

Uses Claude Vision to analyze slide images and extract
semantic understanding from charts and graphics.
"""

import base64
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
import anthropic
from dataclasses import dataclass


@dataclass
class ChartAnalysis:
    """Represents analyzed chart data."""
    chart_type: str  # bar, line, pie, etc.
    title: str
    description: str
    data_points: List[Dict[str, Any]]
    trends: List[str]
    key_insights: List[str]


@dataclass
class SlideVisualAnalysis:
    """Complete visual analysis of a slide."""
    slide_number: int
    visual_description: str
    charts: List[ChartAnalysis]
    extracted_data: Dict[str, Any]
    confidence: float


class VisionAnalyzer:
    """Analyzes slide images using Claude Vision."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"

    def analyze_slide_image(self, image_base64: str, slide_context: str = "") -> SlideVisualAnalysis:
        """
        Analyze a slide image to extract visual information.

        Args:
            image_base64: Base64 encoded image
            slide_context: Optional text context from the slide
        """
        prompt = f"""Analyze this presentation slide image.

{f"Context from slide text: {slide_context}" if slide_context else ""}

Please provide:
1. A description of what visual elements are present (charts, diagrams, images)
2. For any charts/graphs:
   - Chart type (bar, line, pie, scatter, etc.)
   - What data it represents
   - Key data points you can extract (approximate values are fine)
   - Trends or patterns visible
3. Key insights or takeaways from the visual content

Respond in a structured format."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        response_text = message.content[0].text

        # Parse the response into structured data
        return self._parse_analysis(response_text, 0)

    def analyze_slide_content(
        self,
        text_content: str,
        has_chart: bool = False,
        has_image: bool = False,
        tables: List[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze slide content without image (text-based analysis).
        Used when slide images aren't available.

        Args:
            text_content: Extracted text from the slide
            has_chart: Whether the slide contains charts
            has_image: Whether the slide contains images
            tables: List of table markdowns
        """
        context_parts = [f"Slide text content:\n{text_content}"]

        if tables:
            context_parts.append("Tables found in slide:")
            context_parts.extend(tables)

        if has_chart:
            context_parts.append("Note: This slide contains one or more charts/graphs.")

        if has_image:
            context_parts.append("Note: This slide contains images/pictures.")

        prompt = f"""Analyze this presentation slide content and provide a structured summary.

{chr(10).join(context_parts)}

Please provide:
1. Main topic/theme of the slide
2. Key points or data presented
3. If tables are present, summarize the key findings
4. Any insights that can be derived from the content

Be concise but thorough."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return {
            "analysis": message.content[0].text,
            "has_chart": has_chart,
            "has_image": has_image,
            "table_count": len(tables) if tables else 0
        }

    def extract_chart_data(self, image_base64: str, chart_description: str = "") -> Dict[str, Any]:
        """
        Attempt to extract numerical data from a chart image.

        Args:
            image_base64: Base64 encoded chart image
            chart_description: Optional description of what the chart shows
        """
        prompt = f"""This image contains a chart/graph.
{f"Description: {chart_description}" if chart_description else ""}

Please extract the data shown in this chart as accurately as possible.
Provide the output as structured data that could be used to recreate the chart:

1. Chart type
2. X-axis label and values
3. Y-axis label and range
4. Data series (name and values)
5. Any legends or categories

Format the data points as a list that could be converted to JSON.
If exact values aren't clear, provide your best estimates with a note about uncertainty."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        return {
            "raw_extraction": message.content[0].text,
            "chart_description": chart_description
        }

    def _parse_analysis(self, response_text: str, slide_number: int) -> SlideVisualAnalysis:
        """Parse Claude's response into structured analysis."""
        # For now, return the raw analysis
        # In production, you'd parse this more carefully
        return SlideVisualAnalysis(
            slide_number=slide_number,
            visual_description=response_text,
            charts=[],
            extracted_data={},
            confidence=0.8
        )

    def describe_for_embedding(self, slide_content: Dict[str, Any]) -> str:
        """
        Create a rich text description of a slide for embedding.
        Combines text content with visual analysis.
        """
        parts = []

        if slide_content.get('title'):
            parts.append(f"Slide Title: {slide_content['title']}")

        if slide_content.get('text_content'):
            parts.append(f"Content: {' '.join(slide_content['text_content'])}")

        if slide_content.get('tables'):
            parts.append("Contains tabular data")

        if slide_content.get('has_chart'):
            parts.append("Contains charts/visualizations")

        if slide_content.get('analysis'):
            parts.append(f"Analysis: {slide_content['analysis']}")

        return " | ".join(parts)
