import os
import sys
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent

# Add the src directory to Python path for test discovery
sys.path.insert(0, str(project_root / "src"))


# Configure pytest
def pytest_configure(config):
  """Configure pytest for the project."""
  # Add markers here if needed
  config.addinivalue_line("markers", "integration: mark test as an integration test")


def pytest_collection_modifyitems(config, items):
  """Modify test collection if needed."""
  # You can add custom test collection logic here
  pass
