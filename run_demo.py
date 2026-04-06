import subprocess
import time
import sys
import os

def run_demo():
    print("🚀 Starting ReconFlow-OpenEnv Demo...")
    
    # 1. Start Server
    server_process = subprocess.Popen(
        [sys.executable, "app/main.py"],
        env={**os.environ, "PYTHONPATH": "."},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    print("⏳ Waiting for server to initialize...")
    time.sleep(5)
    
    try:
        # 2. Run Inference
        print("🤖 Running Baseline Inference Agent...")
        result = subprocess.run(
            [sys.executable, "inference.py"],
            capture_output=True,
            text=True,
            env={**os.environ, "API_BASE_URL": "http://localhost:8000"}
        )
        
        if result.returncode == 0:
            print("\n✅ Inference completed successfully!")
            print("-" * 50)
            print(result.stdout)
            print("-" * 50)
        else:
            print("\n❌ Inference failed!")
            print(result.stderr)
            
    finally:
        # 3. Cleanup
        print("\n🧹 Cleaning up server process...")
        server_process.terminate()
        server_process.wait()
        print("Done.")

if __name__ == "__main__":
    run_demo()
