#!/usr/bin/env python3

from dataclasses import dataclass
from typing import List, Optional
from bs4 import BeautifulSoup, Tag
from markdownify import markdownify as md
import os
import re


@dataclass
class Message:
  """Represents a single message in the conversation."""

  speaker: str
  content: str
  timestamp: Optional[str] = None


class ConversationsParser:
  """Parser for HTML conversations that converts them to a structured format."""

  # Constants
  USER_PREFIX = "umsg_"
  USER_SPEAKER = "User"
  ASSISTANT_SPEAKER = "Assistant"
  MESSAGE_CONTAINER_CLASS = "ChatMessageContainer"
  PROSE_MARKDOWN_CLASS = "prose-markdown"
  BREAK_ANYWHERE_CLASS = "break-anywhere"
  TIMESTAMP_CLASS = "text-muted-foreground"

  def __init__(self, html_content: str) -> None:
    """Initialize the parser with HTML content.

    Args:
        html_content: Raw HTML string containing the conversation.
    """
    self.soup = BeautifulSoup(html_content, "html.parser")
    self.conversation: List[Message] = []
    self._parse_conversations()

  def _parse_conversations(self) -> None:
    """Parse all messages from the HTML content."""
    message_containers = self.soup.find_all("div", class_=self.MESSAGE_CONTAINER_CLASS)
    self.conversation = [msg for container in message_containers if (msg := self._parse_message(container))]

  def _parse_message(self, container: Tag) -> Optional[Message]:
    """Parse a single message container into a Message object.

    Args:
        container: BeautifulSoup Tag containing the message.

    Returns:
        Message object if parsing successful, None otherwise.
    """
    message_id = container.get("data-message-id", "")
    speaker = self.USER_SPEAKER if message_id.startswith(self.USER_PREFIX) else self.ASSISTANT_SPEAKER
    timestamp = self._extract_timestamp(container)

    content_sections = self._extract_content_sections(container, speaker == self.USER_SPEAKER)

    if not content_sections:
      return None

    return Message(speaker=speaker, timestamp=timestamp, content="\n\n".join(content_sections))

  def _extract_timestamp(self, container: Tag) -> Optional[str]:
    """Extract timestamp from the message container.

    Args:
        container: BeautifulSoup Tag containing the message.

    Returns:
        Timestamp string if found, None otherwise.
    """
    timestamp_elem = container.select_one(f".{self.TIMESTAMP_CLASS}")
    if timestamp_elem and "on" in timestamp_elem.text:
      return timestamp_elem.text.strip()

    # Fallback to flex-shrink container
    timestamp_elem = container.select_one(".flex-shrink")
    return timestamp_elem.text.strip() if timestamp_elem else None

  def _extract_content_sections(self, container: Tag, is_user: bool) -> List[str]:
    """Extract all content sections from a message container.

    Args:
        container: BeautifulSoup Tag containing the message.
        is_user: Boolean indicating if the message is from the user.

    Returns:
        List of content sections as strings.
    """
    content_sections = []

    # Try break-anywhere container first
    break_anywhere = container.select_one(f".{self.BREAK_ANYWHERE_CLASS}")
    if break_anywhere:
      content_sections.extend(self._parse_break_anywhere(break_anywhere, is_user))

    # If no content found, try other content structures
    if not content_sections:
      content_sections.extend(self._parse_alternate_content(container))

    return content_sections

  def _parse_break_anywhere(self, container: Tag, is_user: bool) -> List[str]:
    """Parse content from break-anywhere container.

    Args:
        container: BeautifulSoup Tag containing break-anywhere content.
        is_user: Boolean indicating if the message is from the user.

    Returns:
        List of content sections as strings.
    """
    sections = []

    # Parse prose markdown content
    prose_div = container.select_one(f".{self.PROSE_MARKDOWN_CLASS}")
    if prose_div:
      if content := self._parse_message_content(prose_div):
        sections.append(content)
    elif is_user:
      if content := self._clean_user_content(container.get_text()):
        sections.append(content)

    # Parse code blocks
    code_blocks = container.find_all("pre")
    for block in code_blocks:
      if code_content := self._clean_code_block(block.get_text()):
        sections.append(f"```\n{code_content}\n```")

    return sections

  def _parse_alternate_content(self, container: Tag) -> List[str]:
    """Parse content from alternative container structures.

    Args:
        container: BeautifulSoup Tag containing the message.

    Returns:
        List of content sections as strings.
    """
    sections = []

    # Try direct prose markdown divs
    for prose_div in container.select(".prose.prose-markdown"):
      if content := self._parse_message_content(prose_div):
        sections.append(content)

    # Try nested structure with flex-col
    if not sections:
      if flex_col := container.select_one(".flex.flex-col"):
        for prose_div in flex_col.select(".prose.prose-markdown"):
          if content := self._parse_message_content(prose_div):
            sections.append(content)

    return sections

  def _clean_user_content(self, content: str) -> Optional[str]:
    """Clean and format user message content.

    Args:
        content: Raw content string.

    Returns:
        Cleaned content string or None if empty.
    """
    if not content:
      return None

    content = re.sub(r"Show\s+error\s*$", "", content)
    lines = content.splitlines()
    cleaned_lines = []
    prev_line_empty = False

    for line in lines:
      line = line.rstrip()
      if not line.strip():
        if not prev_line_empty:
          cleaned_lines.append("")
          prev_line_empty = True
      else:
        cleaned_lines.append(line.lstrip())
        prev_line_empty = False

    # Remove leading/trailing empty lines
    while cleaned_lines and not cleaned_lines[0]:
      cleaned_lines.pop(0)
    while cleaned_lines and not cleaned_lines[-1]:
      cleaned_lines.pop()

    return "\n".join(cleaned_lines) if cleaned_lines else None

  def _clean_code_block(self, content: str) -> Optional[str]:
    """Clean and format code block content.

    Args:
        content: Raw code block content.

    Returns:
        Cleaned code block content or None if empty.
    """
    if not content:
      return None

    lines = content.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]

    if not non_empty_lines:
      return None

    min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
    cleaned_lines = [line[min_indent:] if line.strip() else "" for line in lines]

    return "\n".join(cleaned_lines).strip()

  def _parse_message_content(self, content_div: Tag) -> Optional[str]:
    """Parse and clean message content from prose markdown div.

    Args:
        content_div: BeautifulSoup Tag containing prose markdown content.

    Returns:
        Cleaned content string or None if empty.
    """
    if not content_div:
      return None

    content = md(str(content_div), heading_style="ATX")
    lines = [line.strip() for line in content.splitlines()]
    content = "\n".join(lines)
    content = re.sub(r"\n{3,}", "\n\n", content)

    return content.strip() or None

  def format_markdown(self) -> str:
    """Format the conversation as a markdown document.

    Returns:
        Formatted markdown string containing the entire conversation.
    """
    markdown_output = []
    current_date = None

    for msg in self.conversation:
      if msg.timestamp:
        if date_match := re.search(r"on ([^,]+(?:, \d{4})?)", msg.timestamp):
          date = date_match.group(1)
          if date != current_date:
            markdown_output.append(f"## {date}")
            current_date = date

      markdown_output.append(f"\n### {msg.speaker}")
      if msg.content:
        markdown_output.append(msg.content)
      markdown_output.append("\n---")

    content = "\n".join(markdown_output)
    content = re.sub(r"\n{3,}", "\n\n", content)
    content = re.sub(r" +\n", "\n", content)

    return content
