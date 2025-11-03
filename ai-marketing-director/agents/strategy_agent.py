"""Strategy Agent for market research and competitor analysis"""
from openai import OpenAI
from typing import Dict, List, Optional
from datetime import datetime
from config.settings import settings
from core.brand_voice import brand_voice


class StrategyAgent:
    """
    Strategy Agent responsible for:
    - Market research and trend identification
    - Competitor analysis
    - Strategic positioning recommendations
    - Content topic suggestions based on market insights
    """

    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or settings.openai_api_key)
        self.model = settings.default_model
        self.brand_prompt = brand_voice.get_system_prompt("general")

    def analyze_market_trends(self, industry: str = "enterprise AI training") -> Dict:
        """
        Analyze current market trends in the specified industry

        Args:
            industry: Industry to analyze (default: enterprise AI training)

        Returns:
            Dict containing trends, opportunities, and recommendations
        """
        system_prompt = f"""{self.brand_prompt}

You are the Strategy Agent for AI Elevate. Your role is to analyze market trends,
identify opportunities, and provide strategic recommendations for marketing and positioning.

Focus on actionable insights that can inform content strategy and marketing campaigns."""

        user_prompt = f"""Analyze the current market trends in {industry} for {datetime.now().year}.

Provide analysis covering:
1. **Key Trends**: Top 3-5 trends shaping the industry
2. **Opportunities**: Specific opportunities for AI Elevate based on these trends
3. **Content Angles**: Recommended content topics and angles to capitalize on trends
4. **Competitive Landscape**: Key competitors and their positioning
5. **Target Audience Insights**: What enterprise decision-makers care about right now

Format your response as structured JSON with these sections."""

        response = self.client.chat.completions.create(
            model=self.model,
            max_completion_tokens=settings.max_tokens,
            # GPT-5 only supports default temperature=1
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )

        return {
            "analysis": response.choices[0].message.content,
            "timestamp": datetime.now().isoformat(),
            "agent": "strategy_agent",
            "task": "market_trends",
        }

    def analyze_competitor(self, competitor_name: str, competitor_url: Optional[str] = None) -> Dict:
        """
        Analyze a specific competitor

        Args:
            competitor_name: Name of the competitor
            competitor_url: Optional URL to competitor's website

        Returns:
            Dict containing competitor analysis
        """
        system_prompt = f"""{self.brand_prompt}

You are analyzing competitors to identify:
- Their value propositions and positioning
- Content strategy and messaging
- Strengths and weaknesses
- Opportunities for differentiation"""

        user_prompt = f"""Analyze competitor: {competitor_name}
{f'Website: {competitor_url}' if competitor_url else ''}

Provide analysis covering:
1. **Positioning**: How they position themselves in the market
2. **Value Propositions**: Their main selling points
3. **Content Strategy**: Types of content and messaging they use
4. **Strengths**: What they do well
5. **Weaknesses**: Gaps or areas where they're weaker
6. **Differentiation Opportunities**: How AI Elevate can differentiate from them

Keep in mind AI Elevate's strengths:
- 5000+ professionals trained across 25+ countries
- 100+ years collective experience
- Proven frameworks (A-C-E, ReAct)
- Focus on both technical teams AND business leaders
- Enterprise focus (Fortune 500s)"""

        response = self.client.chat.completions.create(
            model=self.model,
            max_completion_tokens=settings.max_tokens,
            # GPT-5 only supports default temperature=1
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )

        return {
            "competitor": competitor_name,
            "analysis": response.choices[0].message.content,
            "timestamp": datetime.now().isoformat(),
            "agent": "strategy_agent",
            "task": "competitor_analysis",
        }

    def suggest_content_topics(
        self, content_type: str = "blog", count: int = 5, based_on: Optional[str] = None
    ) -> Dict:
        """
        Suggest content topics based on market trends and AI Elevate's positioning

        Args:
            content_type: Type of content (blog, linkedin, email, case_study)
            count: Number of topics to suggest
            based_on: Optional context (e.g., "recent trends", "competitor gap analysis")

        Returns:
            Dict containing topic suggestions with rationale
        """
        system_prompt = f"""{self.brand_prompt}

You are suggesting content topics that:
- Align with AI Elevate's expertise and positioning
- Address current market trends and pain points
- Differentiate AI Elevate from competitors
- Drive engagement with target audience (enterprise decision-makers and technical teams)"""

        context_clause = f"\nBase your suggestions on: {based_on}" if based_on else ""

        user_prompt = f"""Suggest {count} compelling {content_type} topics for AI Elevate.{context_clause}

For each topic provide:
1. **Topic Title**: Compelling, specific title
2. **Why Now**: Why this topic is timely and relevant
3. **Target Audience**: Primary audience segment
4. **Key Angles**: Main points to cover
5. **Differentiation**: How this showcases AI Elevate's unique value
6. **SEO Keywords**: Relevant search terms

Format as JSON array."""

        response = self.client.chat.completions.create(
            model=self.model,
            max_completion_tokens=settings.max_tokens,
            # GPT-5 only supports default temperature=1
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )

        return {
            "content_type": content_type,
            "count": count,
            "topics": response.choices[0].message.content,
            "timestamp": datetime.now().isoformat(),
            "agent": "strategy_agent",
            "task": "topic_suggestions",
        }

    def strategic_recommendation(self, context: str) -> Dict:
        """
        Provide strategic marketing recommendations for a given context

        Args:
            context: The situation or question requiring strategic input

        Returns:
            Dict containing strategic recommendations
        """
        system_prompt = f"""{self.brand_prompt}

You are providing high-level strategic recommendations for AI Elevate's marketing.
Your recommendations should be:
- Actionable and specific
- Data-informed where possible
- Aligned with AI Elevate's positioning
- Focused on ROI and business outcomes"""

        user_prompt = f"""Context/Question: {context}

Provide strategic recommendations covering:
1. **Recommended Approach**: What strategy to pursue and why
2. **Expected Outcomes**: What results to expect
3. **Implementation Steps**: How to execute (high-level)
4. **Metrics to Track**: How to measure success
5. **Risks & Mitigations**: Potential challenges and how to address them"""

        response = self.client.chat.completions.create(
            model=self.model,
            max_completion_tokens=settings.max_tokens,
            # GPT-5 only supports default temperature=1
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )

        return {
            "context": context,
            "recommendations": response.choices[0].message.content,
            "timestamp": datetime.now().isoformat(),
            "agent": "strategy_agent",
            "task": "strategic_recommendation",
        }


# CLI interface for testing
if __name__ == "__main__":
    import json
    import sys

    agent = StrategyAgent()

    print("🎯 AI Elevate Strategy Agent")
    print("=" * 50)

    # Example: Market trends analysis
    print("\n📊 Analyzing market trends...")
    trends = agent.analyze_market_trends()
    print(json.dumps(trends, indent=2))

    # Example: Content topic suggestions
    print("\n💡 Suggesting LinkedIn post topics...")
    topics = agent.suggest_content_topics(content_type="linkedin", count=3)
    print(json.dumps(topics, indent=2))
