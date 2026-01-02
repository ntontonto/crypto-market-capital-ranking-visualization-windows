
import os
import json
import argparse
import subprocess
import shutil
from datetime import datetime
from src.data_fetcher import CryptoDataFetcher

def main():
    parser = argparse.ArgumentParser(description="Crypto Ranking Video Generator")
    parser.add_argument("--dry-run", action="store_true", help="Skip video generation")
    args = parser.parse_args()

    # 1. Fetch Data
    print("--- 1. Fetching Data ---")
    fetcher = CryptoDataFetcher()
    data = fetcher.fetch_top_20()
    
    if not data:
        print("Error: Could not fetch data.")
        return

    print(f"Successfully fetched {len(data)} items.")
    
    # Save to current_data.json for Manim to pick up
    with open("current_data.json", "w") as f:
        json.dump(data, f)

    # 2. Generate Video
    if args.dry_run:
        print("Dry run enabled. Skipping video generation.")
        return

    print("--- 2. Generating Video (Manim) ---")
    # Output filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_filename = f"crypto_top20_{date_str}.mp4"
    
    # Manim command
    # -p: Preview (we don't need this for auto)
    # -ql: Quality Low (faster for testing), -qh for High
    # --format=mp4
    # --media_dir ./out_manim (temporary)
    
    # For 9:16 Shorts at 1080x1920
    # Manim Community CLI allows --resolution 1080,1920
    
    # Use 'manim' from the current environment (which should be venv)
    # We use sys.executable to find the python path, but manim is a bin.
    # We'll assume the user runs this script FROM the venv, or we call manim directly hoping it's in path.
    # A safer way if called from python is to usage subprocess with 'manim' assuming it's in the PATH of the shell.
    
    cmd = [
        "manim",
        "-qh", # High quality
        "--resolution", "1080,1920",
        "--media_dir", "./out_temp",
        "--disable_caching",
        "src/video_generator.py",
        "CryptoRankingShorts"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Video generation failed: {e}")
        # Continue to check for partials even if it "failed", 
        # because sometimes Manim exits with error on concat but partials are good.
        pass

    # 3. Finalizing Output
    print("--- 3. Finalizing Output ---")
    
    # Check if main file exists
    # Depending on Manim version and vertical resolution, it might be in 1920p60 or 1080p60
    # We search in out_temp/videos/video_generator/
    
    video_dir = "./out_temp/videos/video_generator"
    found_file = None
    
    if os.path.exists(video_dir):
        for root, dirs, files in os.walk(video_dir):
            if "partial_movie_files" in root:
                continue
            for file in files:
                if file == "CryptoRankingShorts.mp4":
                    found_file = os.path.join(root, file)
                    break
            if found_file:
                break
    
    final_dest = os.path.join("./out", output_filename)
    if not os.path.exists("./out"):
        os.makedirs("./out")

    if found_file and os.path.exists(found_file):
        print(f"Moving {found_file} to {final_dest}")
        shutil.move(found_file, final_dest)
        print(f"SUCCESS: Video generated at {final_dest}")
    else:
        print("Final video not found. Attempting manual concatenation...")
        # Find partial list file
        partial_list_path = None
        for root, dirs, files in os.walk(video_dir):
            if "partial_movie_file_list.txt" in files:
                partial_list_path = os.path.join(root, "partial_movie_file_list.txt")
                break
        
        if partial_list_path:
            print(f"Found partial list at {partial_list_path}")
            # Fix content
            with open(partial_list_path, "r") as f:
                lines = f.readlines()
            
            cleaned_lines = []
            for line in lines:
                # Remove 'file:' prefix from paths inside single quotes
                if "file 'file:" in line:
                    line = line.replace("file 'file:", "file '")
                cleaned_lines.append(line)
            
            fixed_list_path = partial_list_path + ".fixed.txt"
            with open(fixed_list_path, "w") as f:
                f.writelines(cleaned_lines)
                
            # Run ffmpeg
            try:
                cmd_ffmpeg = [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", fixed_list_path,
                    "-c", "copy",
                    final_dest
                ]
                print(f"Running manual concatenation: {' '.join(cmd_ffmpeg)}")
                subprocess.run(cmd_ffmpeg, check=True)
                print(f"SUCCESS: Video generated at {final_dest}")
            except subprocess.CalledProcessError as e:
                print(f"Manual concatenation failed: {e}")
        else:
            print("Error: Could not find partial list file to recover.")

    # Cleanup
    if os.path.exists("./out_temp"):
        shutil.rmtree("./out_temp")
    if os.path.exists("current_data.json"):
        os.remove("current_data.json")

if __name__ == "__main__":
    main()
