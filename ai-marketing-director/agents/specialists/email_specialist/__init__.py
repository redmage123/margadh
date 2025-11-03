"""
Email Specialist Agent module.

WHY: Provides email marketing and automation capabilities for campaign delivery.
HOW: Exports EmailSpecialistAgent and EmailTemplate for use by management layer.
"""

from agents.specialists.email_specialist.email_specialist_agent import (
    EmailSpecialistAgent,
    EmailTemplate,
)

__all__ = ["EmailSpecialistAgent", "EmailTemplate"]
