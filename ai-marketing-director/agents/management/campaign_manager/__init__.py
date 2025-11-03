"""
Campaign Manager Agent - Management layer for campaign orchestration.

WHY: Coordinates multi-channel marketing campaigns across all management agents.

Usage:
    from agents.management.campaign_manager import CampaignManagerAgent
"""

from agents.management.campaign_manager.campaign_manager_agent import (
    CampaignManagerAgent,
)

__all__ = ["CampaignManagerAgent"]
