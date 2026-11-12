"""Run the surfacing skill's own offline tests from the repository test suite."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '.agents/skills/ntop-surfacing/tests/test_surfacing.py'
spec = importlib.util.spec_from_file_location('ntop_surfacing_skill_tests', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

globals().update({name: value for name, value in vars(module).items() if name.startswith('test_')})
