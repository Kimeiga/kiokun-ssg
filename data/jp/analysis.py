from pathlib import Path
from jmdict import load_jmdict

# Get the project root directory
project_root = Path(__file__).parents[2]

# Define paths
databases_dir = project_root / "databases"
jmdict_file = databases_dir / "jmdict-eng-3.5.0.json"

# Load JMdict
jmdict = load_jmdict(str(jmdict_file))

# Your main code here
for entry in jmdict.words[:5]:  # Let's just print the first 5 entries as an example
    print(f"ID: {entry.id}")
    print(entry)
    print(entry.to_dict())
    print("---")
