"""Replay the complete saved construction graph; no source workspace required."""
from pathlib import Path
import sys
REPOSITORY = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPOSITORY / "scripts"))
from replay_recipe import replay
if __name__ == "__main__":
    replay(Path(__file__).resolve().parents[1])
