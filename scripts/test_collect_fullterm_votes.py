"""Quick sanity check for the full-term vote collector."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data_collection.collect_fullterm_votes import collect


def main() -> None:
    output_dir = Path("bronmateriaal-onbewerkt/stemming_enriched_test")
    stored_files = list(
        collect(output_dir=output_dir, max_pages=1, pause_s=0.0)
    )
    print(f"Stored {len(stored_files)} files under {output_dir}")
    for path in stored_files:
        print(f"- {path.name}")


if __name__ == "__main__":
    main()
