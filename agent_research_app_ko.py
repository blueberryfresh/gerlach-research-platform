"""Korean entry point for the same codebase.

Streamlit Cloud will not deploy two apps with the same repo/branch/main file,
so the Korean app uses this file (main file path: agent_research_app_ko.py).
It forces APP_LANG=ko before anything imports strings.py, then runs the
normal app unchanged.
"""
import os
import runpy
from pathlib import Path

os.environ["APP_LANG"] = "ko"

runpy.run_path(str(Path(__file__).parent / "agent_research_app.py"), run_name="__main__")
