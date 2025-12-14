from collections import Counter
from datetime import datetime

# ========= CONFIG =========
INPUT_FILE = "messages_text.txt"   
TIME_FORMAT = "%b %d, %Y %I:%M %p"      # e.g. "Jul 04, 2025 6:25 pm"


# ========= HELPERS =========
def parse_timestamp_from_line(line: str):
    """
    Expected line format:
      'Jul 04, 2025 6:25 pm - Michael: hello'

    Returns datetime or None if it can't parse.
    """
    line = line.strip()
    if not line or " - " not in line:
        return None

    ts_str, _ = line.split(" - ", 1)

    try:
        return datetime.strptime(ts_str, TIME_FORMAT)
    except ValueError:
        return None


def main():
    day_counts = Counter()     # key: date() -> message count
    week_counts = Counter()    # key: (iso_year, iso_week) -> message count
    month_counts = Counter()   # key: (year, month) -> message count

    dates = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            dt = parse_timestamp_from_line(line)
            if dt is None:
                continue

            d = dt.date()
            iso_year, iso_week, _ = dt.isocalendar()
            ym = (dt.year, dt.month)

            day_counts[d] += 1
            week_counts[(iso_year, iso_week)] += 1
            month_counts[ym] += 1
            dates.append(d)

    if not dates:
        print("No valid timestamps found. Check INPUT_FILE and TIME_FORMAT.")
        return

    total_messages = sum(day_counts.values())
    first_day = min(dates)
    last_day = max(dates)
    calendar_span_days = (last_day - first_day).days + 1

    active_days = len(day_counts)
    active_weeks = len(week_counts)
    active_months = len(month_counts)

    avg_per_calendar_day = total_messages / calendar_span_days
    avg_per_active_day = total_messages / active_days if active_days else 0
    avg_per_active_week = total_messages / active_weeks if active_weeks else 0
    avg_per_active_month = total_messages / active_months if active_months else 0

    print("===== RANGE =====")
    print(f"First day:              {first_day}")
    print(f"Last day:               {last_day}")
    print(f"Calendar span:          {calendar_span_days} days")
    print()

    print("===== TOTALS =====")
    print(f"Total messages:         {total_messages}")
    print(f"Active days:            {active_days}")
    print(f"Active weeks:           {active_weeks}")
    print(f"Active months:          {active_months}")
    print()

    print("===== AVERAGES =====")
    print(f"Avg msgs / calendar day: {avg_per_calendar_day:.2f}")
    print(f"Avg msgs / active day:   {avg_per_active_day:.2f}")
    print(f"Avg msgs / active week:  {avg_per_active_week:.2f}")
    print(f"Avg msgs / active month: {avg_per_active_month:.2f}")
    print()

    print("===== TOP 10 BUSIEST DAYS =====")
    for d, c in day_counts.most_common(10):
        print(f"{d}: {c}")
    print()

    print("===== TOP 10 BUSIEST WEEKS (ISO YEAR-WEEK) =====")
    for (y, w), c in week_counts.most_common(10):
        print(f"{y}-W{w:02d}: {c}")
    print()

    print("===== TOP 10 BUSIEST MONTHS (YYYY-MM) =====")
    top_months = sorted(month_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for (y, m), c in top_months:
        print(f"{y}-{m:02d}: {c}")


if __name__ == "__main__":
    main()
