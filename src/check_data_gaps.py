"""
Check for date coverage gaps across raw statement exports.
A gap means no export ever captured that period - those transactions
are permanently missing, unlike a day with zero transactions (which is
just a quiet day, not missing data).
"""
import pandas as pd
from pathlib import Path


def get_file_ranges(int_dir):
    """Return (start, end) date range for each preprocessed file."""
    ranges = []
    for filepath in sorted(int_dir.glob('*.csv')):
        df = pd.read_csv(filepath, parse_dates=['Date'])
        ranges.append((df['Date'].min(), df['Date'].max(), filepath.name))
    return sorted(ranges, key=lambda r: r[0])


def find_gaps(ranges):
    """Merge overlapping/touching ranges and report any gaps between them."""
    gaps = []
    current_start, current_end, _ = ranges[0]

    for start, end, name in ranges[1:]:
        if start > current_end + pd.Timedelta(days=1):
            gaps.append((current_end, start, (start - current_end).days - 1))
        current_end = max(current_end, end)

    return gaps


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    int_dir = project_root / 'data' / '02_intermediate'

    print("🔍 Checking date coverage across statement exports...\n")
    ranges = get_file_ranges(int_dir)

    for start, end, name in ranges:
        print(f"   {name}: {start.date()} to {end.date()}")

    gaps = find_gaps(ranges)

    if not gaps:
        print("\n✅ No gaps - full continuous coverage")
        return

    print(f"\n⚠️  Found {len(gaps)} coverage gap(s) - these days have NO source data:")
    for gap_start, gap_end, days in gaps:
        print(f"   {gap_start.date()} to {gap_end.date()} ({days} missing day{'s' if days != 1 else ''})")


if __name__ == "__main__":
    main()
