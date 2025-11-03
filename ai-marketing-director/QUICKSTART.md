# Quick Start Guide - AI Marketing Director

## Prerequisites

- Python 3.12+ installed
- Anthropic API key (Claude)
- Virtual environment activated

## Installation

1. **Navigate to the project directory**:
   ```bash
   cd /home/bbrelin/marketing/ai-marketing-director
   ```

2. **Install dependencies**:
   ```bash
   ../.venv/bin/pip install anthropic rich python-dotenv pydantic pydantic-settings
   ```

3. **Configure API keys**:
   Edit `.env` file and add your actual API key:
   ```bash
   ANTHROPIC_API_KEY=your_actual_anthropic_api_key_here
   ```

## Usage

### Interactive Mode (Recommended for Getting Started)

Start the interactive CLI:
```bash
../.venv/bin/python main.py interactive
```

Available commands in interactive mode:
- `trends` - Analyze market trends
- `topics linkedin` - Suggest LinkedIn post topics
- `topics blog` - Suggest blog post topics
- `suggest [context]` - Get strategic recommendations
- `status` - Show system status
- `help` - Show help
- `exit` - Exit

You can also ask questions directly:
```
marketing-director> What's the best way to increase LinkedIn engagement?
marketing-director> How should we position against competitors?
```

### Command-Line Mode

**Analyze market trends**:
```bash
../.venv/bin/python main.py trends --output results.json
```

**Analyze a competitor**:
```bash
../.venv/bin/python main.py competitor --competitor "Coursera" --url "https://coursera.com" --output competitor-analysis.json
```

**Suggest content topics**:
```bash
# Blog topics
../.venv/bin/python main.py topics --content-type blog --count 5

# LinkedIn topics
../.venv/bin/python main.py topics --content-type linkedin --count 10 --output linkedin-topics.json
```

**Plan a marketing initiative**:
```bash
../.venv/bin/python main.py plan --objective "Generate 100 qualified leads in Q1" --timeframe "3 months" --output initiative-plan.json
```

## Example Workflow

1. **Start with market research**:
   ```bash
   ../.venv/bin/python main.py trends --output market-trends.json
   ```

2. **Analyze key competitors**:
   ```bash
   ../.venv/bin/python main.py competitor --competitor "Udemy Business" --output udemy-analysis.json
   ../.venv/bin/python main.py competitor --competitor "Coursera" --output coursera-analysis.json
   ```

3. **Get content topic suggestions**:
   ```bash
   ../.venv/bin/python main.py topics --content-type linkedin --count 10 --based-on "Q1 2025 trends" --output topics.json
   ```

4. **Plan your initiative**:
   ```bash
   ../.venv/bin/python main.py plan --objective "Increase brand awareness and generate 50 SQLs" --timeframe "2 months" --output campaign-plan.json
   ```

## What's Working Now (Phase 1)

✅ **Strategy Agent**:
- Market trend analysis
- Competitor analysis
- Content topic suggestions
- Strategic recommendations

✅ **Orchestrator Agent**:
- Marketing initiative planning
- Task creation and prioritization
- Next action suggestions
- Status tracking

✅ **Brand Voice Management**:
- AI Elevate brand guidelines
- Consistent messaging across all content
- Content validation

✅ **CLI Interface**:
- Interactive mode
- Command-line mode
- Rich terminal output
- JSON export

## Coming in Phase 2

🚧 **Content Agent**:
- Blog post generation
- Case study creation
- Whitepapers
- Thought leadership articles

🚧 **Social Media Agent**:
- LinkedIn post creation
- Twitter/X post creation
- Engagement strategies
- Scheduling

🚧 **Campaign Agent**:
- Email sequence creation
- Audience segmentation
- A/B testing

🚧 **Analytics Agent**:
- Performance tracking
- Insights and recommendations
- ROI analysis

## Tips

- **Use interactive mode** for exploratory work and quick questions
- **Use command-line mode** with `--output` flag to save results for review
- **Start with market trends** before creating content to ensure relevance
- **Analyze competitors regularly** to identify differentiation opportunities
- **Review generated content** before publishing (human-in-the-loop approach)

## Getting Help

Run `../.venv/bin/python main.py --help` to see all available commands.

In interactive mode, type `help` to see available commands.

## Security

⚠️ **IMPORTANT**: Never commit your `.env` file to version control. It contains sensitive API keys.

The `.gitignore` file is configured to exclude `.env` files automatically.
