# Lovable Parser

A Python package for converting HTML chat conversations to markdown format. Specifically designed to handle modern chat UI structures with user and assistant messages.

## Installation

```bash
pip install lovable-parser
```

## Usage

```python
from lovable_parser import ConversationsParser

# Read your HTML content
with open("chat.html", "r") as f:
    html_content = f.read()

# Create parser instance
parser = ConversationsParser(html_content)

# Convert to markdown
markdown_content = parser.format_markdown()

# Save to file
with open("chat.md", "w") as f:
    f.write(markdown_content)
```

## Features

- Converts HTML chat conversations to clean markdown format
- Handles both user and assistant messages
- Preserves message structure and formatting
- Supports code blocks and lists
- Maintains proper indentation and spacing

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/lovable-exp/lovable-parser.git
cd lovable-parser

# Install with development dependencies
pip install -e ".[test]"

# Run tests
pytest
```

## License

MIT License 