"""A parser for converting HTML conversations to structured markdown format.

This module provides tools for parsing HTML conversations and converting them
to a clean, structured markdown format while preserving the conversation flow
and formatting.
"""

from .parser import ConversationsParser, Message

__version__ = "0.1.0"
__author__ = "Lovable Experiments"
__all__ = ["ConversationsParser", "Message"]
