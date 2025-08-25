import json
from pathlib import Path

input_path = Path("/home/anshu/tt/merged_faculty.json")  # change if needed
output_path = Path("/home/anshu/tt/faculty.json")

def main():
    data = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Input JSON must be a list of objects.")
    data.sort(key=lambda x: str(x.get("name", "")).lower())
    output_path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
    print(f"Sorted {len(data)} records by name -> {output_path}")

if __name__ == "__main__":
    main()
