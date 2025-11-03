#!/usr/bin/env python3
"""
AI Marketing Director - Main CLI Interface
Enterprise marketing automation with AI agents
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich import print as rprint

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

from agents.strategy_agent import StrategyAgent
from agents.orchestrator import OrchestratorAgent, TaskType, TaskPriority
from config.settings import settings

# Initialize console for rich output
console = Console() if RICH_AVAILABLE else None


def print_header():
    """Print application header"""
    header = """
╔═══════════════════════════════════════════════════╗
║      AI MARKETING DIRECTOR - AI ELEVATE           ║
║      Intelligent Marketing Automation System      ║
╚═══════════════════════════════════════════════════╝
"""
    if console:
        console.print(header, style="bold cyan")
    else:
        print(header)


def cmd_market_trends(args):
    """Analyze market trends"""
    if console:
        console.print("\n🔍 [bold cyan]Analyzing Market Trends...[/bold cyan]\n")
    else:
        print("\n🔍 Analyzing Market Trends...\n")

    agent = StrategyAgent()
    result = agent.analyze_market_trends(industry=args.industry or "enterprise AI training")

    if args.output:
        # Save to file
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n✅ Results saved to: {args.output}")
    else:
        # Display in terminal
        if console:
            console.print(Panel(result["analysis"], title="Market Trends Analysis", border_style="cyan"))
        else:
            print(result["analysis"])


def cmd_competitor_analysis(args):
    """Analyze a competitor"""
    if not args.competitor:
        print("❌ Error: --competitor required")
        sys.exit(1)

    if console:
        console.print(f"\n🎯 [bold cyan]Analyzing Competitor: {args.competitor}[/bold cyan]\n")
    else:
        print(f"\n🎯 Analyzing Competitor: {args.competitor}\n")

    agent = StrategyAgent()
    result = agent.analyze_competitor(args.competitor, competitor_url=args.url)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n✅ Results saved to: {args.output}")
    else:
        if console:
            console.print(
                Panel(result["analysis"], title=f"Competitor Analysis: {args.competitor}", border_style="cyan")
            )
        else:
            print(result["analysis"])


def cmd_suggest_topics(args):
    """Suggest content topics"""
    if console:
        console.print(f"\n💡 [bold cyan]Suggesting {args.content_type} Topics...[/bold cyan]\n")
    else:
        print(f"\n💡 Suggesting {args.content_type} Topics...\n")

    agent = StrategyAgent()
    result = agent.suggest_content_topics(content_type=args.content_type, count=args.count, based_on=args.based_on)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n✅ Results saved to: {args.output}")
    else:
        if console:
            console.print(Panel(result["topics"], title=f"{args.content_type.title()} Topic Suggestions", border_style="cyan"))
        else:
            print(result["topics"])


def cmd_plan_initiative(args):
    """Plan a marketing initiative"""
    if not args.objective:
        print("❌ Error: --objective required")
        sys.exit(1)

    if console:
        console.print(f"\n📋 [bold cyan]Planning Initiative...[/bold cyan]\n")
        console.print(f"Objective: {args.objective}")
        console.print(f"Timeframe: {args.timeframe}\n")
    else:
        print(f"\n📋 Planning Initiative...")
        print(f"Objective: {args.objective}")
        print(f"Timeframe: {args.timeframe}\n")

    orchestrator = OrchestratorAgent()
    plan = orchestrator.plan_marketing_initiative(args.objective, timeframe=args.timeframe)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(plan, f, indent=2)
        print(f"\n✅ Plan saved to: {args.output}")
    else:
        if console:
            console.print(Panel(plan["plan"], title="Marketing Initiative Plan", border_style="green"))
        else:
            print(plan["plan"])


def cmd_interactive(args):
    """Start interactive mode"""
    print_header()

    if console:
        console.print("\n[bold green]Interactive Mode[/bold green] - Type 'help' for commands, 'exit' to quit\n")
    else:
        print("\nInteractive Mode - Type 'help' for commands, 'exit' to quit\n")

    orchestrator = OrchestratorAgent()
    strategy_agent = StrategyAgent()

    while True:
        try:
            if console:
                console.print("[bold cyan]marketing-director>[/bold cyan] ", end="")
            else:
                print("marketing-director> ", end="")

            command = input().strip()

            if not command:
                continue

            if command.lower() in ["exit", "quit", "q"]:
                print("\n👋 Goodbye!")
                break

            elif command.lower() == "help":
                show_help()

            elif command.lower().startswith("trends"):
                result = strategy_agent.analyze_market_trends()
                if console:
                    console.print(Panel(result["analysis"], title="Market Trends", border_style="cyan"))
                else:
                    print("\n" + result["analysis"])

            elif command.lower().startswith("topics"):
                parts = command.split()
                content_type = parts[1] if len(parts) > 1 else "blog"
                result = strategy_agent.suggest_content_topics(content_type=content_type, count=3)
                if console:
                    console.print(Panel(result["topics"], title=f"{content_type.title()} Topics", border_style="cyan"))
                else:
                    print("\n" + result["topics"])

            elif command.lower().startswith("suggest"):
                context = command[8:].strip() if len(command) > 8 else "current market conditions"
                result = orchestrator.suggest_next_actions(context)
                if console:
                    console.print(Panel(result["suggestions"], title="Suggested Actions", border_style="green"))
                else:
                    print("\n" + result["suggestions"])

            elif command.lower() == "status":
                status = orchestrator.get_status_summary()
                if console:
                    console.print(Panel(json.dumps(status, indent=2), title="System Status", border_style="yellow"))
                else:
                    print("\n" + json.dumps(status, indent=2))

            else:
                # Treat as general strategic question
                result = strategy_agent.strategic_recommendation(command)
                if console:
                    console.print(Panel(result["recommendations"], title="Strategic Recommendation", border_style="magenta"))
                else:
                    print("\n" + result["recommendations"])

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def show_help():
    """Display help information"""
    help_text = """
Available Commands:
──────────────────────────────────────────
  trends              Analyze market trends
  topics [type]       Suggest content topics (blog, linkedin, email)
  suggest [context]   Get strategic recommendations
  status              Show system status
  help                Show this help message
  exit                Exit interactive mode

You can also ask any strategic marketing question directly!

Examples:
  > trends
  > topics linkedin
  > suggest launching a new product training
  > What's the best way to increase LinkedIn engagement?
"""
    if console:
        console.print(help_text, style="cyan")
    else:
        print(help_text)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI Marketing Director for AI Elevate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Market trends command
    trends_parser = subparsers.add_parser("trends", help="Analyze market trends")
    trends_parser.add_argument("--industry", type=str, help="Industry to analyze")
    trends_parser.add_argument("--output", "-o", type=str, help="Output file for results (JSON)")

    # Competitor analysis command
    competitor_parser = subparsers.add_parser("competitor", help="Analyze a competitor")
    competitor_parser.add_argument("--competitor", "-c", type=str, required=True, help="Competitor name")
    competitor_parser.add_argument("--url", type=str, help="Competitor website URL")
    competitor_parser.add_argument("--output", "-o", type=str, help="Output file for results (JSON)")

    # Topic suggestions command
    topics_parser = subparsers.add_parser("topics", help="Suggest content topics")
    topics_parser.add_argument(
        "--content-type", "-t", type=str, default="blog", choices=["blog", "linkedin", "email", "case_study"], help="Content type"
    )
    topics_parser.add_argument("--count", "-n", type=int, default=5, help="Number of topics")
    topics_parser.add_argument("--based-on", type=str, help="Context for suggestions")
    topics_parser.add_argument("--output", "-o", type=str, help="Output file for results (JSON)")

    # Plan initiative command
    plan_parser = subparsers.add_parser("plan", help="Plan a marketing initiative")
    plan_parser.add_argument("--objective", type=str, required=True, help="Marketing objective")
    plan_parser.add_argument("--timeframe", type=str, default="1 month", help="Timeframe (e.g., '1 month', '3 months')")
    plan_parser.add_argument("--output", "-o", type=str, help="Output file for plan (JSON)")

    # Interactive mode
    subparsers.add_parser("interactive", help="Start interactive mode")

    args = parser.parse_args()

    # If no command, show help
    if not args.command:
        print_header()
        parser.print_help()
        print("\n💡 Tip: Use 'interactive' mode for an easy-to-use interface!")
        sys.exit(0)

    # Route to appropriate command handler
    if args.command == "trends":
        cmd_market_trends(args)
    elif args.command == "competitor":
        cmd_competitor_analysis(args)
    elif args.command == "topics":
        cmd_suggest_topics(args)
    elif args.command == "plan":
        cmd_plan_initiative(args)
    elif args.command == "interactive":
        cmd_interactive(args)


if __name__ == "__main__":
    main()
