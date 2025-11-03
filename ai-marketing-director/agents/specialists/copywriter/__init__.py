"""
Copywriter Specialist Agent - Content creation and writing (Specialist Layer).

WHY: Provides specialized writing expertise for all marketing content with
     consistent brand voice and quality standards.

HOW: Uses LLM (Claude) with brand voice guidelines to generate high-quality
     content across multiple formats (blog, social media, email, case study).

Usage:
    from agents.specialists.copywriter import CopywriterSpecialistAgent

    agent = CopywriterSpecialistAgent(
        config=config,
        brand_voice=BrandVoiceGuidelines(...)
    )
"""

from agents.specialists.copywriter.copywriter_specialist_agent import (
    BrandVoiceGuidelines,
    CopywriterSpecialistAgent,
)

__all__ = ["CopywriterSpecialistAgent", "BrandVoiceGuidelines"]
