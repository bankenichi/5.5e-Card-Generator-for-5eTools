import os
import subprocess
import sys

def main():
    print("Setting up 5e Card Generator...")
    
    # Create generators directory if it doesn't exist
    generators_dir = "generators"
    if not os.path.exists(generators_dir):
        os.makedirs(generators_dir)
        print(f"Created directory: {generators_dir}")
    
    # Path where 5etools should be cloned
    etools_dir = os.path.join(generators_dir, "5etools")
    
    if os.path.exists(etools_dir):
        print(f"5etools repository already exists at {etools_dir}")
    else:
        print("Cloning 5etools repository...")
        # Note: Replace with the actual URL of the 5etools repository you wish to use
        repo_url = "https://github.com/5etools-mirror-1/5etools-src.git"
        try:
            subprocess.run(["git", "clone", repo_url, etools_dir], check=True)
            print("Successfully cloned 5etools.")
        except subprocess.CalledProcessError:
            print("Failed to clone 5etools. Please ensure git is installed and the repository URL is accessible.")
            print(f"You can manually place the 5etools repository at: {os.path.abspath(etools_dir)}")
            sys.exit(1)
            
    print("\nSetup complete! You can now run the card generator:")
    print("  python card_controller.py")

if __name__ == "__main__":
    main()
