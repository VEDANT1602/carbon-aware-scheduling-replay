"""Compare two result tables by scenario key, checking every field."""
import argparse
import csv
import math

KEY = ("fill", "day", "grid", "phase_h", "horizon_min", "policy")
FLOAT_FIELDS = ("job_g", "overhead_g", "g_per_lookup_j", "idle_g", "total_g")


def load(path):
    with open(path, newline="") as stream:
        rows = list(csv.DictReader(stream))
    table = {tuple(row[k] for k in KEY): row for row in rows}
    if len(table) != 1008 or len(table) != len(rows):
        raise ValueError(f"Unexpected or duplicated scenarios in {path}")
    return table


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("distributed")
    parser.add_argument("regenerated")
    args = parser.parse_args()
    before, after = load(args.distributed), load(args.regenerated)
    if before.keys() != after.keys():
        raise ValueError("Scenario keys differ")
    max_delta = 0
    changed = 0
    for key, first in before.items():
        second = after[key]
        if first.keys() != second.keys():
            raise ValueError("Table schema differs")
        changed += first != second
        for field, orig in first.items():
            new = second[field]
            if field in FLOAT_FIELDS:
                a, b = float(orig), float(new)
                if not math.isclose(a, b, rel_tol=0, abs_tol=1e-9):
                    raise ValueError(f"Mismatch in {key}, {field}: {orig}, {new}")
                max_delta = max(abs(a-b), max_delta)
            elif orig != new:
                raise ValueError(f"Discrete field mismatch in {key}, {field}: {orig}, {new}")
    print(f"Compared {len(before)} rows; {changed} differ as strings. Largest float-field delta: {max_delta:.3g}")

if __name__ == "__main__":
    main()
