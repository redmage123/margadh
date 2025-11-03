"""
Market Research Agent for competitive intelligence and market analysis.

WHY: Provides specialized market research, competitive analysis, industry insights,
     trend identification, and strategic intelligence for marketing decisions.

HOW: Integrates with research APIs (Crunchbase, SimilarWeb, Google Trends) using Strategy
     Pattern for task routing, implements caching for expensive research operations, and
     leverages LLM for insights generation.
"""

from datetime import datetime, timedelta
from typing import Any, Callable, Coroutine, Optional
from urllib.parse import urlparse

from agents.base.agent_protocol import Task, TaskStatus
from agents.base.base_agent import AgentConfig, BaseAgent
from core.exceptions import AgentExecutionError


class CompetitorProfile:
    """
    Competitor profile with key business metrics.

    WHY: Enables structured storage and comparison of competitor data.
    HOW: Stores competitor information from multiple data sources.
    """

    def __init__(
        self,
        company_name: str,
        domain: str,
        industry: str,
        description: str,
        founding_year: Optional[int],
        employee_count: Optional[int],
        funding_total: Optional[float],
        monthly_traffic: Optional[int],
        market_share: Optional[float],
        key_products: list[str],
        strengths: list[str],
        weaknesses: list[str],
    ):
        self.company_name = company_name
        self.domain = domain
        self.industry = industry
        self.description = description
        self.founding_year = founding_year
        self.employee_count = employee_count
        self.funding_total = funding_total
        self.monthly_traffic = monthly_traffic
        self.market_share = market_share
        self.key_products = key_products
        self.strengths = strengths
        self.weaknesses = weaknesses
        self.last_updated = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """
        Convert profile to dictionary.

        WHY: Enables serialization for caching and API responses.
        HOW: Returns all profile data as dictionary.

        Returns:
            Dictionary representation of competitor profile
        """
        return {
            "company_name": self.company_name,
            "domain": self.domain,
            "industry": self.industry,
            "description": self.description,
            "founding_year": self.founding_year,
            "employee_count": self.employee_count,
            "funding_total": self.funding_total,
            "monthly_traffic": self.monthly_traffic,
            "market_share": self.market_share,
            "key_products": self.key_products,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "last_updated": self.last_updated.isoformat(),
        }


class MarketResearchAgent(BaseAgent):
    """
    Specialist-layer agent for market research and competitive intelligence.

    WHY: Provides specialized market analysis, competitor tracking, trend identification,
         and strategic insights for data-driven marketing decisions.
    HOW: Uses research APIs (Crunchbase, SimilarWeb, Google Trends, News API) with
         LLM-powered analysis, caching for performance, and structured data extraction.
    """

    def __init__(
        self,
        config: AgentConfig,
        crunchbase_client: Optional[Any] = None,
        similarweb_client: Optional[Any] = None,
        google_trends_client: Optional[Any] = None,
        llm_client: Optional[Any] = None,
        news_api_client: Optional[Any] = None,
    ):
        super().__init__(config)

        # Research API clients
        self._crunchbase_client = crunchbase_client
        self._similarweb_client = similarweb_client
        self._google_trends_client = google_trends_client
        self._llm_client = llm_client
        self._news_api_client = news_api_client

        # Research cache with 24-hour TTL
        self._research_cache: dict[str, tuple[dict[str, Any], datetime]] = {}
        self._cache_ttl = timedelta(hours=24)

        # Competitor tracking state
        self._competitor_tracking: dict[str, list[dict[str, Any]]] = {}

        # Strategy Pattern: Dictionary dispatch for task routing
        self._task_handlers: dict[
            str, Callable[[Task], Coroutine[Any, Any, dict[str, Any]]]
        ] = {
            "analyze_competitor": self._analyze_competitor,
            "identify_market_trends": self._identify_market_trends,
            "analyze_sentiment": self._analyze_sentiment,
            "research_industry": self._research_industry,
            "perform_swot_analysis": self._perform_swot_analysis,
            "track_competitor_activity": self._track_competitor_activity,
            "identify_opportunities": self._identify_opportunities,
            "generate_market_insights": self._generate_market_insights,
        }

    async def _execute_task(self, task: Task) -> dict[str, Any]:
        """
        Execute market research task using Strategy Pattern.

        WHY: Routes tasks to appropriate handlers without if/elif chains.
        HOW: Uses dictionary dispatch for clean task delegation.
        """
        # Guard clause: Check if task type is supported
        handler = self._task_handlers.get(task.task_type)
        if not handler:
            raise ValueError(f"Unsupported task type: {task.task_type}")

        # Guard clause: Validate task before execution
        if not await self.validate_task(task):
            raise ValueError(f"Task validation failed for {task.task_id}")

        try:
            # Execute task handler
            result = await handler(task)
            return result

        except Exception as e:
            raise AgentExecutionError(
                message=f"Market research task execution failed: {str(e)}",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            )

    async def validate_task(self, task: Task) -> bool:
        """
        Validate task parameters before execution.

        WHY: Ensures tasks have required parameters for successful execution.
        HOW: Checks for required fields based on task type.
        """
        required_params = {
            "analyze_competitor": ["competitor_name"],
            "identify_market_trends": ["industry", "timeframe"],
            "analyze_sentiment": ["target", "data_sources"],
            "research_industry": ["industry"],
            "perform_swot_analysis": ["company_name"],
            "track_competitor_activity": ["competitor_name"],
            "identify_opportunities": ["industry", "context"],
            "generate_market_insights": ["industry", "focus_areas"],
        }

        # Guard clause: Check if task type is known
        if task.task_type not in required_params:
            return False

        # Check required parameters
        for param in required_params[task.task_type]:
            if param not in task.parameters:
                return False

        return True

    async def _analyze_competitor(self, task: Task) -> dict[str, Any]:
        """
        Analyze competitor with multi-source data integration.

        WHY: Provides comprehensive competitor intelligence for strategic planning.
        HOW: Fetches data from Crunchbase (financials), SimilarWeb (traffic),
             performs LLM analysis, and caches results for 24 hours.
        """
        competitor_name = task.parameters["competitor_name"]
        competitor_domain = task.parameters.get("competitor_domain")
        include_financials = task.parameters.get("include_financials", True)
        include_traffic = task.parameters.get("include_traffic", True)

        # Check cache first (24-hour TTL)
        cache_key = f"competitor_{competitor_name.lower()}"
        if cache_key in self._research_cache:
            cached_data, cached_time = self._research_cache[cache_key]
            if datetime.now() - cached_time < self._cache_ttl:
                cached_data["cached"] = True
                return cached_data

        # Guard clause: Validate at least one data source is available
        if not self._crunchbase_client and not self._similarweb_client:
            return {
                "error": "No research data sources configured",
                "competitor_name": competitor_name,
            }

        try:
            competitor_data: dict[str, Any] = {
                "competitor_name": competitor_name,
                "domain": competitor_domain,
                "analysis_date": datetime.now().isoformat(),
            }

            # Fetch Crunchbase data (company financials, funding, team size)
            if include_financials and self._crunchbase_client:
                try:
                    crunchbase_data = await self._crunchbase_client.get_company(
                        competitor_name
                    )
                    competitor_data["financials"] = {
                        "funding_total": crunchbase_data.get("funding_total"),
                        "funding_rounds": crunchbase_data.get("funding_rounds"),
                        "last_funding_date": crunchbase_data.get("last_funding_date"),
                        "employee_count": crunchbase_data.get("employee_count"),
                        "founding_year": crunchbase_data.get("founded_year"),
                        "headquarters": crunchbase_data.get("headquarters"),
                        "investors": crunchbase_data.get("investors", []),
                    }
                    competitor_data["description"] = crunchbase_data.get(
                        "short_description", ""
                    )
                    competitor_data["industry"] = crunchbase_data.get("industry", "")

                    # Extract domain if not provided
                    if not competitor_domain and crunchbase_data.get("website"):
                        competitor_domain = self._extract_domain(
                            crunchbase_data.get("website", "")
                        )
                        competitor_data["domain"] = competitor_domain
                except Exception as e:
                    competitor_data["financials_error"] = str(e)

            # Fetch SimilarWeb data (traffic, engagement, sources)
            if include_traffic and competitor_domain and self._similarweb_client:
                try:
                    traffic_data = await self._similarweb_client.get_website_stats(
                        competitor_domain
                    )
                    competitor_data["traffic"] = {
                        "monthly_visits": traffic_data.get("monthly_visits"),
                        "avg_visit_duration": traffic_data.get("avg_visit_duration"),
                        "pages_per_visit": traffic_data.get("pages_per_visit"),
                        "bounce_rate": traffic_data.get("bounce_rate"),
                        "traffic_sources": traffic_data.get("traffic_sources", {}),
                        "top_countries": traffic_data.get("top_countries", []),
                        "desktop_vs_mobile": traffic_data.get(
                            "device_distribution", {}
                        ),
                    }
                    competitor_data["global_rank"] = traffic_data.get("global_rank")
                    competitor_data["category_rank"] = traffic_data.get("category_rank")
                except Exception as e:
                    competitor_data["traffic_error"] = str(e)

            # LLM-powered competitive analysis
            if self._llm_client:
                try:
                    analysis_prompt = f"""Analyze the following competitor data and provide strategic insights:

Competitor: {competitor_name}
Industry: {competitor_data.get('industry', 'Unknown')}
Description: {competitor_data.get('description', 'N/A')}

Financial Data:
{competitor_data.get('financials', 'Not available')}

Traffic Data:
{competitor_data.get('traffic', 'Not available')}

Provide:
1. Key Strengths (3-5 points)
2. Potential Weaknesses (3-5 points)
3. Market Position Assessment
4. Competitive Threats
5. Strategic Recommendations

Be specific and actionable."""

                    analysis_result = await self._llm_client.generate(
                        prompt=analysis_prompt
                    )

                    competitor_data["llm_analysis"] = {
                        "insights": analysis_result.text,
                        "generated_at": datetime.now().isoformat(),
                    }
                except Exception as e:
                    competitor_data["analysis_error"] = str(e)

            # Create competitor profile
            profile = CompetitorProfile(
                company_name=competitor_name,
                domain=competitor_domain or "",
                industry=competitor_data.get("industry", "Unknown"),
                description=competitor_data.get("description", ""),
                founding_year=competitor_data.get("financials", {}).get(
                    "founding_year"
                ),
                employee_count=competitor_data.get("financials", {}).get(
                    "employee_count"
                ),
                funding_total=competitor_data.get("financials", {}).get(
                    "funding_total"
                ),
                monthly_traffic=competitor_data.get("traffic", {}).get(
                    "monthly_visits"
                ),
                market_share=None,
                key_products=[],
                strengths=[],
                weaknesses=[],
            )

            result = {
                "competitor_name": competitor_name,
                "profile": profile.to_dict(),
                "raw_data": competitor_data,
                "cached": False,
            }

            # Cache result
            self._research_cache[cache_key] = (result, datetime.now())

            return result

        except Exception as e:
            raise AgentExecutionError(
                message=f"Failed to analyze competitor: {str(e)}",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            )

    async def _identify_market_trends(self, task: Task) -> dict[str, Any]:
        """
        Identify market trends using Google Trends and news analysis.

        WHY: Enables proactive marketing by identifying emerging trends and patterns.
        HOW: Fetches Google Trends data, analyzes news articles, extracts trends.
        """
        industry = task.parameters["industry"]
        timeframe = task.parameters["timeframe"]
        keywords = task.parameters.get("keywords", [])
        geographic_scope = task.parameters.get("geographic_scope", "US")

        # Guard clause: Validate Google Trends client
        if not self._google_trends_client:
            return {"error": "Google Trends API not configured"}

        try:
            trends_data: dict[str, Any] = {
                "industry": industry,
                "timeframe": timeframe,
                "geographic_scope": geographic_scope,
                "analysis_date": datetime.now().isoformat(),
            }

            # Get market keywords if not provided
            if not keywords:
                keywords = self._get_market_keywords(industry)

            # Fetch Google Trends data for keywords
            trends_list = []
            for keyword in keywords:
                try:
                    trend_data = await self._google_trends_client.get_trend_data(
                        keyword=keyword,
                        timeframe=timeframe,
                        geo=geographic_scope,
                    )

                    trends_list.append(
                        {
                            "keyword": keyword,
                            "interest_over_time": trend_data.get(
                                "interest_over_time", []
                            ),
                            "related_queries": trend_data.get("related_queries", []),
                            "rising_queries": trend_data.get("rising_queries", []),
                            "average_interest": trend_data.get("average_interest", 0),
                            "trend_direction": trend_data.get(
                                "trend_direction", "stable"
                            ),
                        }
                    )
                except Exception as e:
                    trends_list.append({"keyword": keyword, "error": str(e)})

            trends_data["trends"] = trends_list

            # Get trending topics from news if available
            if self._news_api_client:
                try:
                    news_trends = await self._news_api_client.get_trending_topics(
                        industry=industry, timeframe=timeframe
                    )
                    trends_data["news_trends"] = news_trends.get("topics", [])
                except Exception as e:
                    trends_data["news_trends_error"] = str(e)

            # LLM-powered trend analysis
            if self._llm_client:
                try:
                    trend_prompt = f"""Analyze the following market trend data and identify key insights:

Industry: {industry}
Timeframe: {timeframe}

Trend Data:
{trends_list}

Provide:
1. Top 5 emerging trends
2. Declining trends to avoid
3. Seasonal patterns observed
4. Strategic opportunities from trends
5. Recommended actions

Be specific and actionable."""

                    trend_analysis = await self._llm_client.generate(
                        prompt=trend_prompt
                    )

                    trends_data["analysis"] = {
                        "insights": trend_analysis.text,
                        "generated_at": datetime.now().isoformat(),
                    }
                except Exception as e:
                    trends_data["analysis_error"] = str(e)

            return trends_data

        except Exception as e:
            raise AgentExecutionError(
                message=f"Failed to identify market trends: {str(e)}",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            )

    async def _analyze_sentiment(self, task: Task) -> dict[str, Any]:
        """
        Analyze sentiment from reviews, social media, and news.

        WHY: Provides market perception insights for brand positioning.
        HOW: Fetches data from multiple sources, performs sentiment analysis.
        """
        target = task.parameters["target"]
        data_sources = task.parameters["data_sources"]
        timeframe = task.parameters.get("timeframe", "30d")

        try:
            sentiment_data: dict[str, Any] = {
                "target": target,
                "data_sources": data_sources,
                "timeframe": timeframe,
                "analysis_date": datetime.now().isoformat(),
                "sentiment_scores": {},
            }

            # Analyze each data source
            for source in data_sources:
                if source == "reviews":
                    # Placeholder for review sentiment analysis
                    sentiment_data["sentiment_scores"]["reviews"] = {
                        "average_score": 0.5,
                        "positive_count": 0,
                        "negative_count": 0,
                        "neutral_count": 0,
                        "sample_reviews": [],
                    }
                elif source == "social_media":
                    # Placeholder for social media sentiment
                    sentiment_data["sentiment_scores"]["social_media"] = {
                        "average_score": 0.5,
                        "mention_count": 0,
                        "positive_mentions": 0,
                        "negative_mentions": 0,
                        "trending_hashtags": [],
                    }
                elif source == "news":
                    # Fetch news sentiment if available
                    if self._news_api_client:
                        try:
                            news_data = await self._news_api_client.get_articles(
                                query=target, timeframe=timeframe
                            )

                            articles = news_data.get("articles", [])
                            sentiment_scores = [
                                self._analyze_text_sentiment(article.get("content", ""))
                                for article in articles
                            ]

                            avg_sentiment = (
                                sum(sentiment_scores) / len(sentiment_scores)
                                if sentiment_scores
                                else 0.5
                            )

                            sentiment_data["sentiment_scores"]["news"] = {
                                "average_score": avg_sentiment,
                                "article_count": len(articles),
                                "positive_articles": len(
                                    [s for s in sentiment_scores if s > 0.6]
                                ),
                                "negative_articles": len(
                                    [s for s in sentiment_scores if s < 0.4]
                                ),
                                "top_articles": articles[:5],
                            }
                        except Exception as e:
                            sentiment_data["sentiment_scores"]["news"] = {
                                "error": str(e)
                            }

            # Calculate overall sentiment
            valid_scores = [
                scores.get("average_score", 0.5)
                for scores in sentiment_data["sentiment_scores"].values()
                if isinstance(scores, dict) and "average_score" in scores
            ]

            sentiment_data["overall_sentiment"] = {
                "score": sum(valid_scores) / len(valid_scores) if valid_scores else 0.5,
                "classification": self._classify_sentiment(
                    sum(valid_scores) / len(valid_scores) if valid_scores else 0.5
                ),
            }

            return sentiment_data

        except Exception as e:
            raise AgentExecutionError(
                message=f"Failed to analyze sentiment: {str(e)}",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            )

    async def _research_industry(self, task: Task) -> dict[str, Any]:
        """
        Research industry landscape, market size, and growth projections.

        WHY: Provides strategic context for marketing decisions and planning.
        HOW: Aggregates data from multiple sources, LLM analysis for insights.
        """
        industry = task.parameters["industry"]
        include_competitors = task.parameters.get("include_competitors", True)
        include_forecasts = task.parameters.get("include_forecasts", True)

        try:
            industry_data: dict[str, Any] = {
                "industry": industry,
                "analysis_date": datetime.now().isoformat(),
            }

            # Fetch industry data from Crunchbase if available
            if self._crunchbase_client:
                try:
                    cb_industry_data = await self._crunchbase_client.get_industry_data(
                        industry
                    )
                    industry_data["market_overview"] = {
                        "total_companies": cb_industry_data.get("total_companies"),
                        "total_funding": cb_industry_data.get("total_funding"),
                        "active_investors": cb_industry_data.get("active_investors"),
                        "recent_ipos": cb_industry_data.get("recent_ipos", []),
                        "top_funded_companies": cb_industry_data.get(
                            "top_companies", []
                        ),
                    }
                except Exception as e:
                    industry_data["market_overview_error"] = str(e)

            # Get competitor list if requested
            if include_competitors and self._crunchbase_client:
                try:
                    competitors = await self._crunchbase_client.search_companies(
                        industry=industry, limit=10
                    )
                    industry_data["key_players"] = [
                        {
                            "name": comp.get("name"),
                            "description": comp.get("short_description"),
                            "funding": comp.get("funding_total"),
                            "employees": comp.get("employee_count"),
                        }
                        for comp in competitors
                    ]
                except Exception as e:
                    industry_data["competitors_error"] = str(e)

            # LLM-powered industry analysis
            if self._llm_client:
                try:
                    industry_prompt = f"""Provide comprehensive industry analysis for: {industry}

Available Data:
{industry_data.get('market_overview', 'Limited data available')}

Provide:
1. Industry Overview and Current State
2. Market Size and Growth Rate Estimates
3. Key Market Drivers
4. Major Challenges and Barriers
5. Future Outlook (3-5 years)
6. Strategic Recommendations

Be specific and data-driven where possible."""

                    industry_analysis = await self._llm_client.generate(
                        prompt=industry_prompt
                    )

                    industry_data["industry_research"] = {
                        "analysis": industry_analysis.text,
                        "generated_at": datetime.now().isoformat(),
                    }
                except Exception as e:
                    industry_data["analysis_error"] = str(e)

            return industry_data

        except Exception as e:
            raise AgentExecutionError(
                message=f"Failed to research industry: {str(e)}",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            )

    async def _perform_swot_analysis(self, task: Task) -> dict[str, Any]:
        """
        Perform SWOT analysis for company or product.

        WHY: Provides structured strategic analysis for decision-making.
        HOW: Gathers multi-source data, uses LLM for SWOT framework analysis.
        """
        company_name = task.parameters["company_name"]
        include_market_context = task.parameters.get("include_market_context", True)
        focus_area = task.parameters.get("focus_area", "overall")

        # Guard clause: Validate LLM client for analysis
        if not self._llm_client:
            return {"error": "LLM client required for SWOT analysis"}

        try:
            # Gather company data for context
            company_context = {}

            if self._crunchbase_client:
                try:
                    company_data = await self._crunchbase_client.get_company(
                        company_name
                    )
                    company_context["financials"] = {
                        "funding_total": company_data.get("funding_total"),
                        "employee_count": company_data.get("employee_count"),
                        "founding_year": company_data.get("founded_year"),
                    }
                    company_context["description"] = company_data.get(
                        "short_description", ""
                    )
                    company_context["industry"] = company_data.get("industry", "")
                except Exception as e:
                    company_context["data_error"] = str(e)

            # Perform SWOT analysis with LLM
            swot_prompt = f"""Perform comprehensive SWOT analysis for: {company_name}

Focus Area: {focus_area}

Company Context:
{company_context}

Provide detailed SWOT analysis in the following format:

STRENGTHS (Internal, Positive):
- List 4-6 key strengths with brief explanations

WEAKNESSES (Internal, Negative):
- List 4-6 key weaknesses with brief explanations

OPPORTUNITIES (External, Positive):
- List 4-6 market opportunities with brief explanations

THREATS (External, Negative):
- List 4-6 market threats with brief explanations

After the SWOT, provide:
STRATEGIC RECOMMENDATIONS:
- 3-5 actionable recommendations based on the SWOT analysis

Be specific, realistic, and actionable."""

            swot_result = await self._llm_client.generate(prompt=swot_prompt)

            # Parse SWOT result (simplified parsing)
            swot_analysis = {
                "company_name": company_name,
                "focus_area": focus_area,
                "analysis_date": datetime.now().isoformat(),
                "context": company_context,
                "swot": {
                    "strengths": [],
                    "weaknesses": [],
                    "opportunities": [],
                    "threats": [],
                },
                "raw_analysis": swot_result.text,
                "recommendations": [],
            }

            # Extract structured data from LLM response (basic extraction)
            lines = swot_result.text.split("\n")
            current_section = None

            for line in lines:
                line = line.strip()
                if "STRENGTHS" in line.upper():
                    current_section = "strengths"
                elif "WEAKNESSES" in line.upper():
                    current_section = "weaknesses"
                elif "OPPORTUNITIES" in line.upper():
                    current_section = "opportunities"
                elif "THREATS" in line.upper():
                    current_section = "threats"
                elif "RECOMMENDATIONS" in line.upper():
                    current_section = "recommendations"
                elif line.startswith("-") or line.startswith("•"):
                    item = line.lstrip("-•").strip()
                    if current_section and item:
                        if current_section == "recommendations":
                            swot_analysis["recommendations"].append(item)
                        else:
                            swot_analysis["swot"][current_section].append(item)

            return swot_analysis

        except Exception as e:
            raise AgentExecutionError(
                message=f"Failed to perform SWOT analysis: {str(e)}",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            )

    async def _track_competitor_activity(self, task: Task) -> dict[str, Any]:
        """
        Track competitor activities, launches, and announcements.

        WHY: Enables proactive competitive response and market awareness.
        HOW: Monitors news, social media, website changes, and funding events.
        """
        competitor_name = task.parameters["competitor_name"]
        activity_types = task.parameters.get(
            "activity_types",
            ["product_launches", "funding", "partnerships", "news"],
        )
        lookback_days = task.parameters.get("lookback_days", 30)

        try:
            activities_data: dict[str, Any] = {
                "competitor_name": competitor_name,
                "lookback_days": lookback_days,
                "tracking_date": datetime.now().isoformat(),
                "activities": [],
            }

            # Track news and announcements
            if "news" in activity_types and self._news_api_client:
                try:
                    news_data = await self._news_api_client.get_articles(
                        query=competitor_name,
                        timeframe=f"{lookback_days}d",
                    )

                    for article in news_data.get("articles", []):
                        activities_data["activities"].append(
                            {
                                "type": "news",
                                "title": article.get("title"),
                                "description": article.get("description"),
                                "url": article.get("url"),
                                "published_date": article.get("published_at"),
                                "source": article.get("source", {}).get("name"),
                            }
                        )
                except Exception as e:
                    activities_data["news_error"] = str(e)

            # Track funding events
            if "funding" in activity_types and self._crunchbase_client:
                try:
                    funding_data = await self._crunchbase_client.get_funding_rounds(
                        company_name=competitor_name, limit=5
                    )

                    for funding in funding_data.get("funding_rounds", []):
                        # Only include recent funding within lookback period
                        funding_date = datetime.fromisoformat(
                            funding.get("announced_on", "")
                        )
                        if (datetime.now() - funding_date).days <= lookback_days:
                            activities_data["activities"].append(
                                {
                                    "type": "funding",
                                    "funding_type": funding.get("funding_type"),
                                    "amount": funding.get("money_raised"),
                                    "announced_date": funding.get("announced_on"),
                                    "investors": funding.get("investors", []),
                                }
                            )
                except Exception as e:
                    activities_data["funding_error"] = str(e)

            # Store activities in tracking history
            if competitor_name not in self._competitor_tracking:
                self._competitor_tracking[competitor_name] = []

            self._competitor_tracking[competitor_name].extend(
                activities_data["activities"]
            )

            # Summarize activities by type
            activities_data["summary"] = {
                "total_activities": len(activities_data["activities"]),
                "by_type": {},
            }

            for activity in activities_data["activities"]:
                activity_type = activity.get("type", "unknown")
                activities_data["summary"]["by_type"][activity_type] = (
                    activities_data["summary"]["by_type"].get(activity_type, 0) + 1
                )

            return activities_data

        except Exception as e:
            raise AgentExecutionError(
                message=f"Failed to track competitor activity: {str(e)}",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            )

    async def _identify_opportunities(self, task: Task) -> dict[str, Any]:
        """
        Identify market opportunities and gaps.

        WHY: Enables proactive market positioning and product development.
        HOW: Analyzes market trends, competitor gaps, customer needs with LLM.
        """
        industry = task.parameters["industry"]
        context = task.parameters["context"]
        focus_areas = task.parameters.get(
            "focus_areas", ["market_gaps", "customer_needs"]
        )

        # Guard clause: Validate LLM client
        if not self._llm_client:
            return {"error": "LLM client required for opportunity identification"}

        try:
            # Gather market context
            market_context = {"industry": industry, "provided_context": context}

            # Get trend data if available
            if self._google_trends_client:
                try:
                    keywords = self._get_market_keywords(industry)
                    trend_summary = []

                    for keyword in keywords[:3]:
                        trend_data = await self._google_trends_client.get_trend_data(
                            keyword=keyword, timeframe="12m", geo="US"
                        )
                        trend_summary.append(
                            {
                                "keyword": keyword,
                                "trend": trend_data.get("trend_direction", "stable"),
                                "interest": trend_data.get("average_interest", 0),
                            }
                        )

                    market_context["trends"] = trend_summary
                except Exception as e:
                    market_context["trends_error"] = str(e)

            # LLM-powered opportunity identification
            opportunity_prompt = f"""Identify strategic market opportunities for the {industry} industry.

Context:
{context}

Market Trends:
{market_context.get('trends', 'Not available')}

Focus Areas: {', '.join(focus_areas)}

Provide:
1. TOP MARKET OPPORTUNITIES (5-7 opportunities)
   - For each opportunity, describe:
     * The opportunity
     * Target market segment
     * Estimated market size/potential
     * Key requirements to capture
     * Competitive advantage needed

2. UNDERSERVED CUSTOMER SEGMENTS
   - Identify 3-5 customer segments with unmet needs

3. EMERGING TECHNOLOGY OPPORTUNITIES
   - Identify 3-5 technology trends that create opportunities

4. STRATEGIC RECOMMENDATIONS
   - 3-5 actionable recommendations to pursue opportunities

Be specific, data-driven, and actionable."""

            opportunities_result = await self._llm_client.generate(
                prompt=opportunity_prompt
            )

            opportunities_data = {
                "industry": industry,
                "focus_areas": focus_areas,
                "analysis_date": datetime.now().isoformat(),
                "market_context": market_context,
                "opportunities": [],
                "raw_analysis": opportunities_result.text,
            }

            # Parse opportunities (simplified parsing)
            lines = opportunities_result.text.split("\n")
            current_opportunity = {}

            for line in lines:
                line = line.strip()
                if line.startswith("-") or line.startswith("•"):
                    item = line.lstrip("-•").strip()
                    if item and ":" in item:
                        key, value = item.split(":", 1)
                        current_opportunity[key.strip().lower()] = value.strip()
                    elif item and current_opportunity:
                        if "description" not in current_opportunity:
                            current_opportunity["description"] = item
                elif current_opportunity and not line:
                    opportunities_data["opportunities"].append(current_opportunity)
                    current_opportunity = {}

            # Add last opportunity if exists
            if current_opportunity:
                opportunities_data["opportunities"].append(current_opportunity)

            return opportunities_data

        except Exception as e:
            raise AgentExecutionError(
                message=f"Failed to identify opportunities: {str(e)}",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            )

    async def _generate_market_insights(self, task: Task) -> dict[str, Any]:
        """
        Generate comprehensive market insights and recommendations.

        WHY: Provides strategic intelligence for executive decision-making.
        HOW: Synthesizes multi-source data with LLM-powered analysis.
        """
        industry = task.parameters["industry"]
        focus_areas = task.parameters["focus_areas"]
        include_forecasts = task.parameters.get("include_forecasts", True)
        time_horizon = task.parameters.get("time_horizon", "12_months")

        # Guard clause: Validate LLM client
        if not self._llm_client:
            return {"error": "LLM client required for market insights generation"}

        try:
            # Gather comprehensive market data
            market_data = {
                "industry": industry,
                "focus_areas": focus_areas,
                "time_horizon": time_horizon,
            }

            # Get industry overview
            if self._crunchbase_client:
                try:
                    industry_overview = await self._crunchbase_client.get_industry_data(
                        industry
                    )
                    market_data["industry_metrics"] = {
                        "total_companies": industry_overview.get("total_companies"),
                        "total_funding": industry_overview.get("total_funding"),
                        "growth_rate": industry_overview.get("growth_rate"),
                    }
                except Exception as e:
                    market_data["industry_metrics_error"] = str(e)

            # Get trend data
            if self._google_trends_client:
                try:
                    keywords = self._get_market_keywords(industry)
                    trends = []

                    for keyword in keywords[:5]:
                        trend_data = await self._google_trends_client.get_trend_data(
                            keyword=keyword, timeframe="12m", geo="US"
                        )
                        trends.append(
                            {
                                "keyword": keyword,
                                "direction": trend_data.get(
                                    "trend_direction", "stable"
                                ),
                                "interest": trend_data.get("average_interest", 0),
                                "related_queries": trend_data.get(
                                    "related_queries", []
                                )[:3],
                            }
                        )

                    market_data["trends"] = trends
                except Exception as e:
                    market_data["trends_error"] = str(e)

            # Generate comprehensive insights with LLM
            insights_prompt = f"""Generate comprehensive market insights for the {industry} industry.

Time Horizon: {time_horizon}
Focus Areas: {', '.join(focus_areas)}

Available Market Data:
{market_data}

Provide a comprehensive analysis with:

1. EXECUTIVE SUMMARY
   - 2-3 paragraph overview of market state and key findings

2. KEY INSIGHTS (5-7 insights)
   - Each insight should include:
     * The insight
     * Supporting evidence
     * Strategic implications

3. MARKET DYNAMICS
   - Growth drivers
   - Inhibiting factors
   - Competitive landscape changes

4. CUSTOMER INSIGHTS
   - Evolving customer needs
   - Behavioral shifts
   - Segment opportunities

5. FUTURE OUTLOOK ({time_horizon})
   - Market projections
   - Emerging trends to watch
   - Potential disruptions

6. STRATEGIC RECOMMENDATIONS
   - 5-7 prioritized recommendations
   - For each: objective, actions, expected impact

Be specific, data-driven, and actionable. Provide executive-level insights."""

            insights_result = await self._llm_client.generate(prompt=insights_prompt)

            insights_data = {
                "industry": industry,
                "focus_areas": focus_areas,
                "time_horizon": time_horizon,
                "generated_at": datetime.now().isoformat(),
                "market_data": market_data,
                "insights": insights_result.text,
                "recommendations": [],
            }

            # Extract recommendations (simplified parsing)
            lines = insights_result.text.split("\n")
            in_recommendations = False

            for line in lines:
                line = line.strip()
                if "RECOMMENDATIONS" in line.upper():
                    in_recommendations = True
                elif in_recommendations and (
                    line.startswith("-") or line.startswith("•")
                ):
                    recommendation = line.lstrip("-•").strip()
                    if recommendation:
                        insights_data["recommendations"].append(recommendation)

            return insights_data

        except Exception as e:
            raise AgentExecutionError(
                message=f"Failed to generate market insights: {str(e)}",
                original_exception=e,
                context={"agent_id": self.agent_id, "task_id": task.task_id},
            )

    # Helper methods

    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.

        WHY: Normalizes URLs for consistent API calls.
        HOW: Uses urlparse to extract domain component.

        Args:
            url: Full URL string

        Returns:
            Domain name without protocol or path
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            # Remove www. prefix if present
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return url

    def _get_market_keywords(self, industry: str) -> list[str]:
        """
        Get relevant keywords for market research.

        WHY: Provides industry-specific keywords for trend analysis.
        HOW: Maps industries to relevant search keywords.

        Args:
            industry: Industry name

        Returns:
            List of relevant keywords for research
        """
        # Industry keyword mapping (simplified)
        keyword_map = {
            "saas": [
                "saas",
                "software as a service",
                "cloud software",
                "enterprise software",
                "b2b software",
            ],
            "ecommerce": [
                "ecommerce",
                "online shopping",
                "retail technology",
                "direct to consumer",
                "marketplace",
            ],
            "fintech": [
                "fintech",
                "digital banking",
                "payment technology",
                "financial services",
                "cryptocurrency",
            ],
            "healthcare": [
                "healthcare technology",
                "telemedicine",
                "digital health",
                "medical devices",
                "health tech",
            ],
            "edtech": [
                "edtech",
                "online education",
                "learning platforms",
                "educational software",
                "e-learning",
            ],
        }

        # Try to find matching industry
        industry_lower = industry.lower()
        for key, keywords in keyword_map.items():
            if key in industry_lower:
                return keywords

        # Default: use industry name as keyword
        return [industry, f"{industry} technology", f"{industry} market"]

    def _analyze_text_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text (simplified implementation).

        WHY: Provides basic sentiment scoring for content analysis.
        HOW: Simple rule-based sentiment analysis (stub for ML model).

        Args:
            text: Text to analyze

        Returns:
            Sentiment score between 0.0 (negative) and 1.0 (positive)
        """
        # Simplified sentiment analysis
        # In production, would use proper NLP/ML sentiment model

        if not text:
            return 0.5

        text_lower = text.lower()

        # Positive words
        positive_words = [
            "good",
            "great",
            "excellent",
            "amazing",
            "outstanding",
            "positive",
            "success",
            "growth",
            "increase",
            "improve",
            "innovative",
            "leading",
        ]

        # Negative words
        negative_words = [
            "bad",
            "poor",
            "terrible",
            "awful",
            "negative",
            "failure",
            "decline",
            "decrease",
            "problem",
            "issue",
            "concern",
            "risk",
        ]

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        # Calculate sentiment score
        total_count = positive_count + negative_count
        if total_count == 0:
            return 0.5

        sentiment = positive_count / total_count
        return sentiment

    def _classify_sentiment(self, score: float) -> str:
        """
        Classify sentiment score into category.

        WHY: Provides human-readable sentiment classification.
        HOW: Maps numeric score to category labels.

        Args:
            score: Sentiment score (0.0 to 1.0)

        Returns:
            Sentiment classification string
        """
        if score >= 0.7:
            return "very_positive"
        elif score >= 0.6:
            return "positive"
        elif score >= 0.4:
            return "neutral"
        elif score >= 0.3:
            return "negative"
        else:
            return "very_negative"
