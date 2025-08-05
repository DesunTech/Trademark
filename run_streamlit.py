#!/usr/bin/env python3
"""
Simple script to run the Streamlit Trademark Extraction UI
"""

import os
import sys
import subprocess

def run_streamlit():
    """Run the Streamlit application"""
    try:
        # Change to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        
        # Run streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"]
        
        print("Starting Streamlit Trademark Extraction UI...")
        print(f"Project directory: {project_dir}")
        print(f"Command: {' '.join(cmd)}")
        print("\nOpening http://localhost:8501 in your browser...")
        print("Press Ctrl+C to stop the server\n")
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\nStreamlit server stopped.")
    except Exception as e:
        print(f"Error running Streamlit: {e}")

if __name__ == "__main__":
    run_streamlit()