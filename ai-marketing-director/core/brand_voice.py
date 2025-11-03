"""Brand voice and messaging guidelines for AI Elevate"""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class BrandVoice:
    """AI Elevate brand voice and messaging guidelines"""

    company_name: str = "AI Elevate"
    company_url: str = "https://ai-elevate.ai"

    # Core Value Propositions
    value_props: List[str] = None

    # Brand Personality Traits
    personality_traits: List[str] = None

    # Messaging Guidelines
    messaging_dos: List[str] = None
    messaging_donts: List[str] = None

    # Target Audience
    target_audiences: Dict[str, str] = None

    # Key Topics & Expertise
    key_topics: List[str] = None

    # Tone & Style
    tone: str = "professional, authoritative, yet approachable"

    def __post_init__(self):
        """Initialize brand guidelines based on AI Elevate's positioning"""
        if self.value_props is None:
            self.value_props = [
                "AI doesn't replace people - it amplifies them",
                "26% productivity increase in just 3 hours (Microsoft/MIT Study, 2024)",
                "Enterprise prompt engineering training your competitors are already using",
                "5,000+ professionals trained across 25+ countries",
                "100+ years of collective industry experience",
                "Comprehensive AI training for both technical teams and business leaders",
            ]

        if self.personality_traits is None:
            self.personality_traits = [
                "Expert and authoritative",
                "Results-driven and data-backed",
                "Approachable and educational",
                "Forward-thinking and innovative",
                "Pragmatic and business-focused",
            ]

        if self.messaging_dos is None:
            self.messaging_dos = [
                "Back claims with credible sources (Gartner, McKinsey, Microsoft, MIT)",
                "Emphasize real-world results and case studies",
                "Use specific numbers and metrics (26% productivity increase, 5000+ trained)",
                "Focus on practical, immediately applicable knowledge",
                "Address Fortune 500 and enterprise needs",
                "Highlight both technical and business leader tracks",
                "Mention proven frameworks (A-C-E, ReAct methodologies)",
                "Emphasize 'AI Elevation Movement' community aspect",
            ]

        if self.messaging_donts is None:
            self.messaging_donts = [
                "Don't use hype or exaggerated claims",
                "Don't make unsupported productivity claims",
                "Don't focus only on technology without business context",
                "Don't ignore the human element - emphasize amplification, not replacement",
                "Don't use overly technical jargon for business leader content",
                "Don't promise overnight transformations",
            ]

        if self.target_audiences is None:
            self.target_audiences = {
                "enterprise_leaders": "C-suite, VPs, Directors seeking AI transformation",
                "technical_teams": "Engineers, data scientists, AI practitioners",
                "fortune_500": "Large enterprises in financial services, tech, healthcare, aviation",
                "ai_decision_makers": "Leaders evaluating AI training and implementation",
            }

        if self.key_topics is None:
            self.key_topics = [
                "Prompt engineering frameworks (A-C-E, ReAct)",
                "Enterprise AI training",
                "LLM fine-tuning",
                "AI implementation best practices",
                "Responsible AI practices",
                "Workflow design and automation",
                "ROI from AI investments",
                "Case studies from Fortune 500 companies",
                "Python and data science for AI",
            ]

    def get_system_prompt(self, content_type: str = "general") -> str:
        """Generate system prompt for AI agents to maintain brand voice"""

        base_prompt = f"""You are creating content for {self.company_name} ({self.company_url}),
an enterprise AI training company that has trained 5,000+ professionals across 25+ countries.

BRAND VOICE & TONE:
{self.tone}

CORE VALUES & POSITIONING:
{chr(10).join(f'- {vp}' for vp in self.value_props)}

PERSONALITY TRAITS:
{chr(10).join(f'- {trait}' for trait in self.personality_traits)}

TARGET AUDIENCE:
{chr(10).join(f'- {name}: {desc}' for name, desc in self.target_audiences.items())}

MESSAGING GUIDELINES - DO:
{chr(10).join(f'✓ {do}' for do in self.messaging_dos)}

MESSAGING GUIDELINES - DON'T:
{chr(10).join(f'✗ {dont}' for dont in self.messaging_donts)}

KEY TOPICS TO EMPHASIZE:
{chr(10).join(f'- {topic}' for topic in self.key_topics)}
"""

        # Content-specific additions
        if content_type == "linkedin":
            base_prompt += """

LINKEDIN-SPECIFIC GUIDELINES:
- Keep posts concise (1200-1500 characters ideal)
- Use line breaks for readability
- Include relevant hashtags (#PromptEngineering #EnterpriseAI #AITraining)
- End with clear CTA
- Use 'Join the AI Elevation Movement' as signature phrase
"""
        elif content_type == "blog":
            base_prompt += """

BLOG-SPECIFIC GUIDELINES:
- Use clear structure with headings
- Include real-world examples and case studies
- Back claims with research and data
- Provide actionable takeaways
- Include relevant internal links to AI Elevate resources
"""
        elif content_type == "email":
            base_prompt += """

EMAIL-SPECIFIC GUIDELINES:
- Subject line should be compelling but not clickbait
- Personalize where possible
- Keep paragraphs short
- One clear CTA per email
- Professional but conversational tone
"""

        return base_prompt

    def validate_content(self, content: str) -> Dict[str, any]:
        """Validate content against brand guidelines (basic checks)"""
        warnings = []
        score = 100

        # Check for unsupported claims
        unsupported_patterns = ["guaranteed", "overnight success", "automatic results"]
        for pattern in unsupported_patterns:
            if pattern.lower() in content.lower():
                warnings.append(f"Avoid unsupported claim: '{pattern}'")
                score -= 10

        # Check for brand phrase
        if "elevate" not in content.lower() and len(content) > 500:
            warnings.append("Consider mentioning 'AI Elevate' or 'elevate' theme")
            score -= 5

        # Check for data backing
        has_stats = any(char.isdigit() and '%' in content for char in content)
        has_source = any(source in content for source in ['McKinsey', 'Gartner', 'Microsoft', 'MIT', 'study', 'research'])

        if not has_stats and len(content) > 500:
            warnings.append("Consider adding specific metrics or statistics")
            score -= 5

        return {
            "valid": score >= 70,
            "score": max(0, score),
            "warnings": warnings,
        }


# Global brand voice instance
brand_voice = BrandVoice()
