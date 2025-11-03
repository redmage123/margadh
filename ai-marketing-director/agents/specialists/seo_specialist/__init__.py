"""
SEO Specialist Agent - Search engine optimization and content optimization (Specialist Layer).

WHY: Provides specialized SEO expertise for improving organic search visibility
     and rankings.

HOW: Conducts keyword research, optimizes content, analyzes SERP competition,
     generates meta descriptions, tracks rankings using external SEO tools
     and AI-powered analysis.

Usage:
    from agents.specialists.seo_specialist import SEOSpecialistAgent

    agent = SEOSpecialistAgent(config=config)
"""

from agents.specialists.seo_specialist.seo_specialist_agent import SEOSpecialistAgent

__all__ = ["SEOSpecialistAgent"]
