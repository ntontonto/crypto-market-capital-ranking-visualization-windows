# Crypto Top 20 Ranking Video Generator

Automatically generates a YouTube Short (9:16) visualizing the Top 20 Crypto Market Cap.

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
    > We use a **Virtual Environment (venv)** to manage Python dependencies (`requests`, etc.) while relying on the **System Manim** (installed via Brew) for video rendering. This avoids compatibility issues between `pip`-installed Manim and system FFmpeg.

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
    ```bash
    python3 main.py
    ```

    *   Fetches data from CoinGecko (saved to `./cache/`).
    *   Generates video using Manim.
    *   Output saved to `./out/crypto_top20_YYYY-MM-DD.mp4`.

    **Options**:
    *   `--dry-run`: Fetch data only, skip video generation.

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