# Crypto Market Summary Video Generator

Automatically generates a 60-second YouTube Short (9:16) visualizing:
1.  **Price Growth Race** (Top Gainers/Losers 7-Day)
2.  **Top Movers & "Unusual" Activity** (24h)
3.  **Market Signals** (Heatmap, Mood, Momentum)

## Requirements

*   **System**: macOS (tested on Apple Silicon)
*   **Tools**:
    *   Python 3.9+
    *   [Homebrew](https://brew.sh/)
    *   FFmpeg (installed via brew)
    *   Manim (installed via brew)

## Installation

1.  **Install System Dependencies**:
    ```bash
    brew install manim ffmpeg
    ```

2.  **Setup Python Environment**:
    
    > [!IMPORTANT]
    > We use a **Virtual Environment (venv)** to manage Python dependencies (`requests`, etc.) while relying on the **System Manim** (installed via Brew) for video rendering.

    ```bash
    # Create virtual environment
    python3 -m venv venv

    # Activate it
    source venv/bin/activate

    # Install Python dependencies
    pip install -r requirements.txt
    ```

## Usage

1.  **Activate Environment** (if not active):
    ```bash
    source venv/bin/activate
    ```

2.  **Run Generator**:
    
    **Option A: Fetch Fresh Data (Default)**
    Fetches latest data from CoinGecko (Top 10 ranking history, movers, dominance) and generates video.
    ```bash
    python3 main.py --fetch
    ```
    
    **Option B: Use Specific Input File**
    Generates video from a provided JSON file (skips fetching).
    ```bash
    python3 main.py --input input.sample.json
    ```

    **Output**: Saved to `./out/crypto_summary_YYYY-MM-DD.mp4`.

    **Other Options**:
    *   `--dry-run`: Fetch data only, skip video generation.

## Input JSON Specification

The generator accepts a JSON file with the following structure:

```json
{
  "asOf": "2026-01-02T00:00:00Z",
  "currency": "usd",
  "top10_7d": [
    {
      "date": "2025-12-27",
      "items": [
        {"id":"bitcoin","symbol":"BTC","name":"Bitcoin","market_cap": 123456789},
        ... (10 items)
      ]
    },
    ... (7 days)
  ],
  "today_top_movers": {
    "gainers": [ {"id":"sol","symbol":"SOL","change_24h_pct": 9.87, "price": 123.45, ...} ],
    "losers": [ ... ]
  },
  "dominance": {
    "series": [
      {"date":"2025-12-27","btc_pct": 49.1, "eth_pct": 17.2, "stable_pct": 8.4},
      ...
    ]
  }
}
```

3.  **Clean Up**:
    Remove temporary files, cache, or generated videos.

3.  **Clean Up**:
    Remove temporary files, cache, or generated videos.
    *   **Default**: Removes `media/`, `out_temp/`, `videos/`, `__pycache__`, and intermediate files.
    *   **--cache**: Also removes `./cache/`.
    *   **--output**: Also removes `./out/`.
    *   **--all**: Removes everything.

    ```bash
    # Clean temporary files (default)
    python3 cleanup.py

    # Clean cache and output videos too
    python3 cleanup.py --all
    ```

## Troubleshooting

*   **Manim/FFmpeg errors**: Ensure you installed `manim` via `brew install manim`. Pip-installed manim often has conflicts with system FFmpeg on macOS.
*   **Timeouts**: CoinGecko API has rate limits. If it fails, the script will try to use the latest cached data.

## Dependency Implementation Notes

**Why usage of Homebrew Manim + Python Venv?**

During development, we encountered a known compatibility issue on macOS (Apple Silicon):
1.  **Pip-installed Manim** (`pip install manim`) depends on the `av` library.
2.  The `av` library often fails to build against the latest **System FFmpeg** (v7.x) installed via Homebrew.
3.  Manim requires an older version of `av` (<14.0.0), which is completely incompatible with modern FFmpeg headers.

**Solution**:
We use the **System Manim** (`brew install manim`). Homebrew manages the binary compatibility between Manim, its dependencies (Cairo, Pango), and FFmpeg.
We still use a **Python Venv** for our own logic (`requests`, independent scripts), but we carefully exclude `manim` from `requirements.txt` to avoid reinstalling the broken Pip version.

## License
MIT