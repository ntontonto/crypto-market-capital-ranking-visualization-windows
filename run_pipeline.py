
import subprocess
import sys
import os

def run():
    print("🚀 Starting Automated Crypto Video Pipeline...")
    
    # Check if we are in the correct directory (naive check)
    if not os.path.exists("main.py"):
        print("❌ Error: main.py not found. Please run this script from the project root.")
        return

    # Construct command
    # python main.py --fetch --upload --privacy public
    # We append any arguments passed to this script (e.g. --dry-run)
    cmd = [sys.executable, "main.py", "--fetch", "--upload", "--privacy", "public"] + sys.argv[1:]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        # Run the command and wait for it to complete
        # check=True will raise CalledProcessError if return code is non-zero
        subprocess.run(cmd, check=True)
        print("✅ Pipeline Completed Successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Pipeline Failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\n⚠️ Pipeline cancelled by user.")
        sys.exit(1)

if __name__ == "__main__":
    run()
