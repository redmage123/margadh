# ADR-011: Designer Specialist Agent Architecture

**Status:** Accepted
**Date:** 2025-11-03
**Decision Makers:** Architecture Team
**Related ADRs:** ADR-001 (Multi-agent Architecture), ADR-002 (TDD Methodology), ADR-007 (Content Manager Agent), ADR-009 (Copywriter Specialist Agent)

## Context

The AI Marketing Director system currently has:
- **Executive Layer:** CMO Agent (strategic oversight)
- **Management Layer:** Campaign Manager, Social Media Manager, Content Manager
- **Specialist Layer:** LinkedIn Manager, Twitter Manager, Bluesky Manager, Analytics Specialist, Copywriter Specialist, SEO Specialist

The Content Manager, Copywriter, and Campaign Manager require visual design capabilities to:
1. Create visual assets for blog posts (featured images, infographics)
2. Generate social media graphics optimized for each platform
3. Design campaign-specific marketing assets
4. Create design variations for A/B testing
5. Ensure brand consistency across all visual content
6. Generate product mockups and promotional graphics
7. Create data visualizations and charts
8. Design email templates and headers

Without a Designer Specialist:
- Content is published without compelling visual elements
- No automated visual asset generation
- Manual design work required for all graphics
- Inconsistent visual brand identity
- Social media posts lack optimized imagery
- Content Manager has no design capabilities for content strategy

## Decision

We will implement a **Designer Specialist Agent** as a specialist-layer agent that:

1. **Generates visual assets** using AI image generation tools (DALL-E, Midjourney, Stable Diffusion)
2. **Creates platform-specific graphics** optimized for social media (LinkedIn, Twitter, Instagram)
3. **Designs marketing materials** (infographics, banners, ads, email headers)
4. **Ensures brand consistency** with configurable brand guidelines and style standards
5. **Generates design variations** for A/B testing and optimization
6. **Creates data visualizations** from analytics data and reports
7. **Provides design recommendations** based on best practices and trends
8. **Optimizes images** for web performance (compression, formats, dimensions)

### Architecture Design

```
┌─────────────────────────────────────────────────┐
│      Designer Specialist (Specialist Layer)     │
│  - Visual asset generation                      │
│  - Platform-specific graphics                   │
│  - Brand consistency enforcement                │
│  - Design variations & A/B testing              │
└─────────────────────────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      ▼               ▼               ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│AI Image  │   │  Brand   │   │  Design  │
│Generator │   │Guidelines│   │Templates │
│(DALL-E)  │   │          │   │          │
└──────────┘   └──────────┘   └──────────┘
```

### Coordination Pattern

```
Content Manager
   ↓ (requests blog featured image)
Designer Specialist → [AI Image Gen, Brand Guidelines]

Copywriter Specialist
   ↓ (requests infographic for article)
Designer Specialist → [Generate data visualization]

Social Media Manager
   ↓ (requests social graphics)
Designer Specialist → [Platform-specific graphics]

Campaign Manager
   ↓ (requests campaign assets)
Designer Specialist → [Campaign-themed designs]
```

### Supported Task Types

1. **generate_social_graphic**: Create platform-specific social media graphics
2. **generate_blog_image**: Generate featured images for blog posts
3. **create_infographic**: Design data-driven infographics
4. **generate_ad_creative**: Create advertising graphics and banners
5. **design_email_header**: Generate email marketing headers
6. **create_thumbnail**: Generate video/content thumbnails
7. **generate_design_variations**: Create A/B test variations
8. **optimize_image**: Optimize images for web performance

### Key Characteristics

- **AI Image Generation:** Integrates with DALL-E, Midjourney, or Stable Diffusion APIs
- **Brand Guidelines Engine:** Enforces brand colors, fonts, logo usage, visual style
- **Template Library:** Pre-configured templates for common design needs
- **Multi-Format Export:** Generates assets in multiple formats (PNG, JPG, SVG, WebP)
- **Dimension Optimization:** Creates platform-specific dimensions automatically
- **Design Quality Scoring:** Evaluates designs for brand compliance and aesthetics
- **Variation Generation:** Creates multiple design options for testing
- **Strategy Pattern:** Uses dictionary dispatch for task routing (zero if/elif chains)
- **Exception Wrapping:** All external API calls wrapped with `AgentExecutionError`

## Consequences

### Positive

1. **Automated visual content:** Generates professional graphics at scale
2. **Brand consistency:** Ensures all visuals follow brand guidelines
3. **Platform optimization:** Creates properly sized graphics for each platform
4. **Fast iteration:** Quickly generates design variations for testing
5. **Cost effective:** Reduces need for manual design work
6. **Integration ready:** Works seamlessly with Content Manager and Social Media Manager
7. **Standards compliance:** Follows all coding directives (Strategy Pattern, guard clauses, full type hints, WHY/HOW documentation)

### Negative

1. **AI generation limitations:** Image quality may vary, requires review
2. **API costs:** Image generation APIs can be expensive
3. **Creative constraints:** AI may not match human designer creativity
4. **Brand nuance:** Subtle brand elements may require manual adjustment
5. **Rate limiting:** Image generation APIs have rate limits

### Mitigation Strategies

1. **Quality thresholds:** Set minimum quality scores for generated images
2. **Human review workflow:** Flag designs for human approval when needed
3. **Template fallbacks:** Use pre-designed templates when AI generation fails
4. **Caching:** Cache generated images to reduce API calls
5. **Cost controls:** Set daily/monthly generation limits

## Implementation Notes

### Task Delegation Pattern

```python
# Designer generates social media graphic
async def _generate_social_graphic(self, task: Task) -> dict[str, Any]:
    """
    Generate platform-specific social media graphic.

    WHY: Creates optimized visuals for social media engagement.
    HOW: Uses AI image generation with brand guidelines and platform specs.
    """
    platform = task.parameters["platform"]
    content_topic = task.parameters["content_topic"]
    style = task.parameters.get("style", "professional")

    # Get platform-specific dimensions
    dimensions = self._get_platform_dimensions(platform)

    # Guard clause: Check if AI image generator is available
    if not self._image_generator:
        return {"error": "Image generator not configured", "image_url": None}

    # Build prompt with brand guidelines
    prompt = self._build_image_prompt(
        topic=content_topic,
        style=style,
        brand_guidelines=self._brand_guidelines
    )

    try:
        # Generate image with AI
        image = await self._image_generator.generate(
            prompt=prompt,
            width=dimensions["width"],
            height=dimensions["height"],
            style=style
        )

        # Validate brand compliance
        brand_score = await self._validate_brand_compliance(image)

        # Optimize for web
        optimized_image = await self._optimize_image(
            image=image,
            format="webp",
            quality=85
        )

        return {
            "image_url": optimized_image.url,
            "image_path": optimized_image.path,
            "dimensions": dimensions,
            "platform": platform,
            "brand_compliance_score": brand_score,
            "file_size": optimized_image.size_kb,
            "format": "webp"
        }

    except Exception as e:
        raise AgentExecutionError(
            agent_id=self.agent_id,
            task_id=task.task_id,
            message=f"Failed to generate social graphic: {str(e)}",
            original_exception=e
        )
```

### Platform Specifications

```python
PLATFORM_SPECS = {
    "linkedin": {
        "post": {"width": 1200, "height": 627},
        "profile_banner": {"width": 1584, "height": 396},
        "company_logo": {"width": 300, "height": 300}
    },
    "twitter": {
        "post": {"width": 1200, "height": 675},
        "header": {"width": 1500, "height": 500},
        "profile": {"width": 400, "height": 400}
    },
    "instagram": {
        "post": {"width": 1080, "height": 1080},
        "story": {"width": 1080, "height": 1920},
        "carousel": {"width": 1080, "height": 1080}
    },
    "facebook": {
        "post": {"width": 1200, "height": 630},
        "cover": {"width": 820, "height": 312},
        "profile": {"width": 180, "height": 180}
    },
    "blog": {
        "featured_image": {"width": 1200, "height": 630},
        "inline_image": {"width": 800, "height": 450},
        "thumbnail": {"width": 400, "height": 225}
    }
}
```

### Brand Guidelines Structure

```python
class BrandGuidelines:
    """Brand guidelines for consistent visual design."""

    def __init__(
        self,
        primary_colors: list[str],
        secondary_colors: list[str],
        fonts: dict[str, str],
        logo_usage: dict[str, Any],
        visual_style: str,
        imagery_style: str
    ):
        self.primary_colors = primary_colors  # ["#1E40AF", "#3B82F6"]
        self.secondary_colors = secondary_colors  # ["#F59E0B", "#10B981"]
        self.fonts = fonts  # {"heading": "Montserrat", "body": "Open Sans"}
        self.logo_usage = logo_usage  # Placement, size, clearspace rules
        self.visual_style = visual_style  # "modern", "minimal", "bold"
        self.imagery_style = imagery_style  # "photography", "illustration", "mixed"

    def to_prompt_context(self) -> str:
        """Convert guidelines to AI prompt context."""
        return f"""
        Brand Visual Guidelines:
        - Primary colors: {', '.join(self.primary_colors)}
        - Secondary colors: {', '.join(self.secondary_colors)}
        - Visual style: {self.visual_style}
        - Imagery style: {self.imagery_style}
        - Mood: professional, modern, trustworthy
        """
```

### Integration with Content Manager

```python
# Content Manager requests featured image for blog post
content_manager -> designer.generate_blog_image(
    content_topic="AI Marketing Trends 2025",
    content_summary="Article about emerging AI trends...",
    style="professional"
)

# Copywriter requests infographic for data
copywriter -> designer.create_infographic(
    data={"ROI": 150, "Efficiency": 200, "Time Saved": 40},
    title="Marketing Automation ROI",
    chart_type="bar"
)

# Social Media Manager requests platform graphics
social_media_manager -> designer.generate_social_graphic(
    platform="linkedin",
    content_topic="Product Launch Announcement",
    include_text=True,
    text_overlay="New Product Launch"
)

# Campaign Manager requests ad creative
campaign_manager -> designer.generate_ad_creative(
    campaign_id="campaign_001",
    ad_type="banner",
    size="leaderboard",  # 728x90
    message="Transform Your Marketing"
)
```

### Image Quality Validation

```python
async def _validate_brand_compliance(self, image: Image) -> float:
    """
    Validate image compliance with brand guidelines.

    WHY: Ensures generated images match brand standards.
    HOW: Analyzes color palette, composition, style.

    Returns:
        Brand compliance score (0-100)
    """
    score = 0.0

    # Analyze color palette (40 points)
    color_score = await self._analyze_color_compliance(image)
    score += color_score * 0.40

    # Check composition quality (30 points)
    composition_score = self._analyze_composition(image)
    score += composition_score * 0.30

    # Validate style consistency (30 points)
    style_score = self._analyze_style_consistency(image)
    score += style_score * 0.30

    return score

def _analyze_composition(self, image: Image) -> float:
    """
    Analyze image composition quality.

    WHY: Good composition improves visual appeal and engagement.
    HOW: Checks rule of thirds, balance, focal points.
    """
    # Simplified composition analysis
    # In production, would use computer vision

    # Check image dimensions are appropriate
    aspect_ratio = image.width / image.height
    ideal_ratios = [1.0, 1.91, 0.8, 16/9]  # Square, LinkedIn, Portrait, Widescreen

    closest_ratio = min(ideal_ratios, key=lambda x: abs(x - aspect_ratio))
    ratio_score = 100.0 if abs(closest_ratio - aspect_ratio) < 0.1 else 70.0

    return ratio_score
```

### Design Variation Generation

```python
async def _generate_design_variations(self, task: Task) -> dict[str, Any]:
    """
    Generate multiple design variations for A/B testing.

    WHY: Enables testing different design approaches.
    HOW: Creates variations with different styles, colors, layouts.
    """
    base_design = task.parameters["base_design"]
    variation_count = task.parameters.get("count", 3)
    variation_types = task.parameters.get("types", ["color", "layout", "style"])

    variations = []

    for i in range(variation_count):
        # Generate variation based on type
        variation_type = variation_types[i % len(variation_types)]

        if variation_type == "color":
            # Variation with different color scheme
            variation = await self._create_color_variation(base_design, i)
        elif variation_type == "layout":
            # Variation with different layout
            variation = await self._create_layout_variation(base_design, i)
        elif variation_type == "style":
            # Variation with different visual style
            variation = await self._create_style_variation(base_design, i)

        variations.append({
            "variation_id": f"var_{i+1}",
            "type": variation_type,
            "image_url": variation.url,
            "description": f"{variation_type.title()} variation {i+1}"
        })

    return {
        "base_design": base_design,
        "variations": variations,
        "total_variations": len(variations),
        "ready_for_testing": True
    }
```

### Testing Strategy

1. **Unit tests:** 14+ tests covering all task types with mocked image generation
2. **Integration tests:** Full workflows with real image API integration (or mocked)
3. **Brand compliance tests:** Verify brand guideline enforcement
4. **Platform optimization tests:** Validate correct dimensions for each platform
5. **Quality tests:** Check image optimization and compression
6. **Error handling tests:** API failures, invalid parameters, rate limiting
7. **Variation tests:** Verify design variation generation

## Alternatives Considered

### Alternative 1: Content Manager Handles Design Directly
Content Manager directly calls image generation APIs.

**Rejected because:**
- Violates single responsibility principle
- Content Manager is for coordination, not specialized design
- No dedicated design expertise and brand enforcement
- Difficult to reuse design capabilities across other agents
- Can't independently improve design without affecting management logic

### Alternative 2: External Design Service (No Agent)
Use external design API service without agent wrapper.

**Rejected because:**
- No integration with multi-agent workflows
- No brand consistency enforcement
- No design quality validation
- Doesn't fit multi-agent architecture
- No context awareness of content strategy

### Alternative 3: Template-Only Approach
Use pre-designed templates without AI generation.

**Rejected because:**
- Limited flexibility and variety
- Requires extensive template library maintenance
- Cannot adapt to new content types easily
- Less dynamic and engaging visuals
- Doesn't leverage AI capabilities

### Alternative 4: Manual Design Process
Rely on human designers for all visual content.

**Rejected because:**
- Doesn't scale for high-volume content
- Slow turnaround time
- Human bottleneck for content workflow
- Contradicts autonomous department vision
- Expensive for routine graphics

## References

- ADR-001: Multi-agent Department Architecture
- ADR-002: TDD Methodology
- ADR-005: Exception Wrapping Standard
- ADR-007: Content Manager Agent
- ADR-009: Copywriter Specialist Agent
- MULTIAGENT_ARCHITECTURE.md: System architecture document
- DEVELOPMENT_STANDARDS.md: Coding standards

## Notes

This ADR establishes Designer Specialist as a key visual content creation agent. Future enhancements may include:
- Video thumbnail generation
- Animated graphics and GIFs
- Custom illustration styles
- 3D rendering capabilities
- Advanced photo editing and manipulation
- AI-powered design trend analysis
- Accessibility compliance (color contrast, alt text suggestions)
- Multi-language text overlay support
- Brand asset management integration
