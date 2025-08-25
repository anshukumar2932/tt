import json
from pathlib import Path

# Inputs
names_path = Path("/home/anshu/tt/name.json")
ratings_path = Path("/home/anshu/tt/converted.json")  # ratings extracted from Supabase
output_path = Path("/home/anshu/tt/teacher_reviews.json")

def compute_rating(row):
    # Average of the 4 numeric fields, rounded to 2 decimals
    vals = [
        float(row.get("teaching", 0) or 0),
        float(row.get("evaluation", 0) or 0),
        float(row.get("behaviour", 0) or 0),
        float(row.get("internals", 0) or 0),
    ]
    return round(sum(vals) / 4.0, 2)

def final_remark_from_rating(rating, class_avg: str | None):
    # Produce the exact phrases requested
    # Thresholds can be adjusted; this follows earlier logic
    if rating >= 4.0:
        return "Highly Recommended🔥"
    if rating >= 3.0:
        return "Moderately Recommended🔥"
    return "Not Recommended🚫"

def make_review(row, class_avg: str, final_remark: str):
    # Render numeric parts as floats like 4.0
    t = float(row.get("teaching", 0) or 0)
    e = float(row.get("evaluation", 0) or 0)
    b = float(row.get("behaviour", 0) or 0)
    i = float(row.get("internals", 0) or 0)
    # Capitalize class average exactly as in the example: High/Medium/Low
    class_avg_fmt = (class_avg or "").strip().capitalize()
    return (
        f"Teaching: {t}, Evaluation: {e}, Behaviour: {b}, "
        f"Internals: {i}, Class Average : {class_avg_fmt}, "
        f"Final Remark: {final_remark}"
    )

def main():
    # Load data
    names = json.loads(names_path.read_text(encoding="utf-8"))
    ratings = json.loads(ratings_path.read_text(encoding="utf-8"))

    # Build index from teacher_id -> list of rating rows (in case multiple ratings per teacher)
    by_teacher = {}
    for r in ratings:
        tid = r.get("teacher_id")
        if not tid:
            continue
        by_teacher.setdefault(tid, []).append(r)

    # Join on names.id == ratings.teacher_id
    out = []
    for n in names:
        tid = n.get("id")
        full_name = n.get("full_name")
        rows = by_teacher.get(tid, [])

        if not rows:
            # Skip teachers with no ratings; or include with rating 0 per preference
            continue

        # If multiple ratings exist for a teacher_id, average their computed ratings
        # and use the most recent row’s components for the review, or average components.
        # Here, compute average of the 4 fields across all rows, then build one review.
        if len(rows) == 1:
            row = rows[0]
            rating = compute_rating(row)
            class_avg = row.get("class_average", "")
            final_remark = final_remark_from_rating(rating, class_avg)
            review = make_review(row, class_avg, final_remark)
        else:
            # Average each field across rows
            def avg_field(field):
                vals = [float(r.get(field, 0) or 0) for r in rows]
                return sum(vals) / len(vals) if vals else 0.0

            teaching = avg_field("teaching")
            evaluation = avg_field("evaluation")
            behaviour = avg_field("behaviour")
            internals = avg_field("internals")

            rating = round((teaching + evaluation + behaviour + internals) / 4.0, 2)

            # For class_average, pick the most frequent value; fallback to first
            class_values = [str((r.get("class_average") or "")).strip() for r in rows if r.get("class_average") is not None]
            if class_values:
                from collections import Counter
                class_avg = Counter(class_values).most_common(1)[0][0]
            else:
                class_avg = ""

            final_remark = final_remark_from_rating(rating, class_avg)
            row_for_review = {
                "teaching": teaching,
                "evaluation": evaluation,
                "behaviour": behaviour,
                "internals": internals
            }
            review = make_review(row_for_review, class_avg, final_remark)

        out.append({
            "name": full_name,
            "rating": rating,
            "review": review
        })

    # Optionally sort by name
    out.sort(key=lambda x: x["name"].lower())

    # Write output
    output_path.write_text(json.dumps(out, indent=4, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(out)} entries to {output_path}")

if __name__ == "__main__":
    main()
