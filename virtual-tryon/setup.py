"""Setup script for Virtual Try-On application."""

import os
import shutil

def setup_environment():
    """Set up the environment file."""
    env_example = ".env.example"
    env_file = ".env"
    
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            shutil.copy(env_example, env_file)
            print(f"✅ Created {env_file} from {env_example}")
            print("📝 Please edit the .env file with your Google API key")
        else:
            # Create a basic .env file
            with open(env_file, 'w') as f:
                f.write("# Google AI Configuration\n")
                f.write("GOOGLE_API_KEY=your_google_api_key_here\n")
                f.write("GOOGLE_CLOUD_PROJECT=your_project_id\n")
                f.write("GOOGLE_CLOUD_LOCATION=us-central1\n")
                f.write("\n# Logging\n")
                f.write("LOGGING_LEVEL=INFO\n")
            print(f"✅ Created {env_file}")
            print("📝 Please edit the .env file with your Google API key")
    else:
        print(f"✅ {env_file} already exists")

if __name__ == "__main__":
    setup_environment()