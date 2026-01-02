
import os
import json
import argparse
import subprocess
import shutil
from datetime import datetime
from src.data_fetcher import CryptoDataFetcher

def main():
    parser = argparse.ArgumentParser(description="Crypto Ranking Video Generator")
    parser.add_argument("--dry-run", action="store_true", help="Fetch data only, skip video generation")
    parser.add_argument("--input", type=str, help="Path to input JSON file (skips fetching)")
    parser.add_argument("--fetch", action="store_true", help="Force fetch new data even if input provided (overrides input)")
    args = parser.parse_args()

    # 1. Prepare Data
    print("--- 1. Data Preparation ---")
    
    input_data = None
    input_file_path = "current_input.json"

    if args.input and not args.fetch:
        print(f"Using provided input file: {args.input}")
        if not os.path.exists(args.input):
            print(f"Error: Input file {args.input} not found.")
            return
        # Validate JSON
        try:
            with open(args.input, "r") as f:
                input_data = json.load(f)
            # Copy to current_input.json for Manim
            if os.path.abspath(args.input) != os.path.abspath(input_file_path):
                shutil.copy(args.input, input_file_path)
            print("Input validation passed.")
        except json.JSONDecodeError:
            print(f"Error: {args.input} is not valid JSON.")
            return
    else:
        # Fetch Data
        print("Fetching fresh data from DataFetcher...")
        fetcher = CryptoDataFetcher()
        try:
            input_data = fetcher.generate_input_json()
            if not input_data:
                print("Error: Fetched data is empty.")
                return
            
            # Save to file
            with open(input_file_path, "w") as f:
                json.dump(input_data, f, indent=2)
            print(f"Data saved to {input_file_path}")
            
        except Exception as e:
            print(f"Error during data fetching: {str(e)}")
            return

    # 2. Generate Video
    if args.dry_run:
        print("Dry run enabled. Skipping video generation.")
        return

    print("--- 2. Generating Video (Manim) ---")
    
    # Check Manim availability
    if not shutil.which("manim"):
        print("Error: 'manim' command not found. Please install Manim (brew install manim).")
        return

    # Derive output filename from data date
    as_of = input_data.get("asOf", "").split("T")[0] or datetime.now().strftime("%Y-%m-%d")
    output_filename = f"crypto_summary_{as_of}.mp4"
    
    cmd = [
        "manim",
        "-qh", # High quality (1080p)
        "--resolution", "1080,1920", # Vertical
        "--media_dir", "./out_temp",
        "--disable_caching",
        "src/video_generator.py",
        "CryptoRankingShorts"
    ]
    
    print(f"Running Manim command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Manim failed with exit code {e.returncode}")
        # Sometimes Manim errors but produces output? Be careful.
        # We'll check for output anyway.

    # 3. Finalize Output
    print("--- 3. Finalizing Output ---")
    
    # Path where Manim dumps the video
    # Usually: media_dir/videos/scene_file/quality/SceneName.mp4
    # Here: ./out_temp/videos/video_generator/1080p60/CryptoRankingShorts.mp4
    # Or strict resolution folder? Manim Community changes this sometimes.
    # We search for it.
    
    expected_name = "CryptoRankingShorts.mp4"
    found_file = None
    
    search_dir = "./out_temp/videos"
    if os.path.exists(search_dir):
        for root, dirs, files in os.walk(search_dir):
            if expected_name in files:
                found_file = os.path.join(root, expected_name)
                break
    
    if found_file:
        final_dest_dir = "./out"
        if not os.path.exists(final_dest_dir):
            os.makedirs(final_dest_dir)
        final_dest_path = os.path.join(final_dest_dir, output_filename)
        
        shutil.move(found_file, final_dest_path)
        print(f"SUCCESS: Video generated at {final_dest_path}")
    else:
        print("Error: Could not find generated video file.")
        
    # Cleanup
    if os.path.exists("./out_temp"):
        shutil.rmtree("./out_temp")
        
if __name__ == "__main__":
    main()
