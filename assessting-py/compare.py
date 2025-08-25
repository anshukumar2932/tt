import json
from pathlib import Path

converted_path = Path("/home/anshu/tt/teacher_reviews.json")
faculty_path = Path("/home/anshu/tt/faculty.json")
output_path = Path("/home/anshu/tt/merged_faculty.json")

def to_index(items):
    """
    Normalize a list[dict] with keys: name, rating, review -> dict by lowercase name.
    If faculty.json is a dict keyed by name, it will be converted to this common form.
    """
    idx = {}
    if isinstance(items, list):
        for obj in items:
            if not isinstance(obj, dict):
                continue
            name = str(obj.get("name", "")).strip()
            if not name:
                continue
            idx[name.lower()] = {
                "name": name,
                "rating": float(obj.get("rating", 0.0)) if obj.get("rating") is not None else 0.0,
                "review": obj.get("review", "")
            }
    elif isinstance(items, dict):
        for name, obj in items.items():
            if not isinstance(obj, dict):
                continue
            name_str = str(name).strip()
            if not name_str:
                continue
            rating = obj.get("rating")
            # Try common alternative keys
            if rating is None:
                rating = obj.get("score", obj.get("avg", obj.get("Average", 0.0)))
            try:
                rating = float(rating)
            except Exception:
                rating = 0.0
            review = obj.get("review") or obj.get("comment") or ""
            idx[name_str.lower()] = {
                "name": name_str,
                "rating": rating,
                "review": review
            }
    return idx

def load_json_any(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def main():
    converted = load_json_any(converted_path)
    faculty = load_json_any(faculty_path)

    idx_conv = to_index(converted)
    idx_fac = to_index(faculty)

    merged_keys = set(idx_conv.keys()) | set(idx_fac.keys())
    merged = []

    for key in sorted(merged_keys):
        a = idx_conv.get(key)
        b = idx_fac.get(key)

        if a and b:
            # Average ratings if both exist
            avg_rating = round((float(a.get("rating", 0.0)) + float(b.get("rating", 0.0))) / 2.0, 2)
            # Prefer the more detailed review from converted, else fallback
            review = a.get("review") or b.get("review") or ""
            # Preserve original name casing from converted if present, else from faculty
            name = a.get("name") or b.get("name")
            merged.append({
                "name": name,
                "rating": avg_rating,
                "review": review
            })
        elif a:
            merged.append(a)
        elif b:
            merged.append(b)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(merged, f, indent=4, ensure_ascii=False)

    print(f"Merged file written to {output_path}")

if __name__ == "__main__":
    main()
