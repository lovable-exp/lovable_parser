import pytest
from lovable_parser import ConversationsParser

SAMPLE_HTML = """
<div class="ChatMessageContainer" data-message-id="umsg_01">
  <div class="break-anywhere">
    <div class="prose-markdown">
      <p>I'll create a modern SignatureSecure app with a focus on document signing and management.</p>
      <ul>
        <li>Clean interface</li>
        <li>Professional design</li>
      </ul>
    </div>
    <pre>
      const config = {
        theme: 'light'
      }
    </pre>
  </div>
  <span class="text-muted-foreground">17:05 on Apr 27, 2025</span>
</div>
<div class="ChatMessageContainer" data-message-id="aimsg_02">
  <div class="break-anywhere">
    <div class="prose-markdown">
      <p>Please implement the database schema</p>
    </div>
  </div>
  <span class="text-muted-foreground">17:06 on Apr 27, 2025</span>
</div>
"""

EXPECTED_MARKDOWN = """## Apr 27, 2025

### User
I'll create a modern SignatureSecure app with a focus on document signing and management.

* Clean interface
* Professional design

```
const config = {
  theme: 'light'
}
```

---

### Assistant
Please implement the database schema

---"""


def test_conversation_parser():
  # Create parser instance with HTML content
  parser = ConversationsParser(SAMPLE_HTML)

  # Get markdown output
  markdown_content = parser.format_markdown()

  # Compare with expected output
  assert markdown_content.strip() == EXPECTED_MARKDOWN.strip()


def test_empty_conversation():
  parser = ConversationsParser("")
  markdown_content = parser.format_markdown()
  assert markdown_content.strip() == ""


def test_invalid_message_structure():
  parser = ConversationsParser('<div class="ChatMessageContainer"><div>Invalid structure</div></div>')
  markdown_content = parser.format_markdown()
  assert markdown_content.strip() == ""


COMPLEX_HTML = """
<div class="ChatMessageContainer" data-message-id="aimsg_03">
  <div class="mb-2">
    <span class="text-muted-foreground">17:05 on Apr 27, 2025</span>
  </div>
  <div class="pl-0">
    <div class="flex flex-col space-y-4">
      <div class="prose prose-markdown">
        <p>I'll create a modern SignatureSecure app with a focus on document signing and management.</p>
        <p>For this first version, I'll implement:</p>
        <ol>
          <li>A beautiful landing page that communicates trust and security</li>
          <li>User authentication flow (signup/login)</li>
          <li>User dashboard showing document status</li>
        </ol>
        <p>Color Palette &amp; Design:</p>
        <ul>
          <li>Primary: Deep purple (#6E59A5) for trust and professionalism</li>
          <li>Secondary: Light purple (#E5DEFF) for subtle accents</li>
        </ul>
      </div>
    </div>
  </div>
</div>
"""

EXPECTED_COMPLEX_MARKDOWN = """## Apr 27, 2025

### Assistant
I'll create a modern SignatureSecure app with a focus on document signing and management.

For this first version, I'll implement:

1. A beautiful landing page that communicates trust and security
2. User authentication flow (signup/login)
3. User dashboard showing document status

Color Palette & Design:

* Primary: Deep purple (#6E59A5) for trust and professionalism
* Secondary: Light purple (#E5DEFF) for subtle accents

---"""


def test_complex_message_structure():
  # Create parser instance with complex HTML content
  parser = ConversationsParser(COMPLEX_HTML)

  # Get markdown output
  markdown_content = parser.format_markdown()

  # Compare with expected output
  assert markdown_content.strip() == EXPECTED_COMPLEX_MARKDOWN.strip()


def test_modern_chat_structure():
  MODERN_HTML = """
    <div style="position: absolute; width: 100%; left: 0px;">
      <div class="ChatMessageContainer group flex flex-col pr-2 pb-4" data-message-id="umsg_01jswxm4cxfew9wnph8bt484kd">
        <div class="">
          <div class="flex flex-col items-end">
            <div class="break-anywhere overflow-auto whitespace-pre-wrap rounded-xl text-base leading-[22px] max-w-[80%] bg-secondary px-3 py-3">
              <div>For the code present, I get the error below.

Please think step-by-step in order to resolve it.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div style="position: absolute; width: 100%; left: 0px;">
      <div class="ChatMessageContainer group flex flex-col pr-2 pb-4" data-message-id="aimsg_01jsx1ewvqfhe9kc0c7wpk5jbz">
        <div class="break-anywhere">
          <div class="prose-markdown">
            <p>I'll help you resolve the error.</p>
          </div>
        </div>
      </div>
    </div>
    """

  EXPECTED_MODERN_MARKDOWN = """### User
For the code present, I get the error below.

Please think step-by-step in order to resolve it.

---

### Assistant
I'll help you resolve the error.

---"""

  parser = ConversationsParser(MODERN_HTML)
  markdown_content = parser.format_markdown()
  assert markdown_content.strip() == EXPECTED_MODERN_MARKDOWN.strip()


if __name__ == "__main__":
  pytest.main([__file__])
