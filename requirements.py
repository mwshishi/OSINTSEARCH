import subprocess

def generate_requirements():
    """Creates a requirements.txt file with all installed packages."""
    try:
        with open("requirements.txt", "w") as f:
            subprocess.run(["pip", "freeze"], stdout=f, text=True)
        print("[✅] requirements.txt created successfully!")
    except Exception as e:
        print(f"[❌] Error creating requirements.txt: {e}")

generate_requirements()
