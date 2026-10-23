"""Regenerate TSLA and AMZN sample CSVs in this directory."""

from pathlib import Path

from optionsview.data import View, download_options_view


def main() -> None:
    output_folder = str(Path(__file__).resolve().parent)

    for symbol in ("TSLA", "AMZN"):
        result = download_options_view(
            symbol=symbol,
            view_type=View.ALL,
            folder=output_folder,
        )
        result.print_summary()

        if not result.is_complete:
            raise RuntimeError(f"Sample export failed for {symbol}")


if __name__ == "__main__":
    main()