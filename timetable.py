"""
Smart Timetable Clash Detector and Free-Slot Finder
Course : Computational Thinking and Programming (2026CSAE100)

Reads weekly timetables of several members from a CSV file, detects clashes
inside a member's timetable and finds common free slots for a group.
"""

import csv
import os

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
COLLEGE_START = 9 * 60      # 09:00 in minutes
COLLEGE_END = 17 * 60       # 17:00 in minutes
DATA_FILE = "timetable.csv"
REPORT_FILE = "report.txt"


# ---------------------------------------------------------------- time helpers
def to_minutes(text):
    """Convert 'HH:MM' to minutes since midnight. Raises ValueError if invalid."""
    parts = text.strip().split(":")
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        raise ValueError(f"Invalid time '{text}' (use HH:MM)")
    hours, minutes = int(parts[0]), int(parts[1])
    if not (0 <= hours < 24 and 0 <= minutes < 60):
        raise ValueError(f"Time '{text}' is out of range")
    return hours * 60 + minutes


def to_time(minutes):
    """Convert minutes since midnight to 'HH:MM'."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


# ------------------------------------------------------------ data management
def validate_entry(member, day, start, end, subject):
    """Validate one class entry and return it in clean form."""
    member, subject = member.strip(), subject.strip()
    day = day.strip().capitalize()
    if not member:
        raise ValueError("Member name is empty")
    if day not in DAYS:
        raise ValueError(f"Invalid day '{day}'")
    start_min, end_min = to_minutes(start), to_minutes(end)
    if end_min <= start_min:
        raise ValueError("End time must be after start time")
    if not subject:
        raise ValueError("Subject is empty")
    return member, day, start_min, end_min, subject


def add_class(timetable, member, day, start, end, subject):
    """Add a validated class to the timetable dictionary."""
    member, day, start_min, end_min, subject = validate_entry(
        member, day, start, end, subject)
    timetable.setdefault(member, {}).setdefault(day, []).append(
        (start_min, end_min, subject))


def load_timetable(filename):
    """Load a CSV file. Returns (timetable, list_of_error_messages)."""
    timetable, errors = {}, []
    with open(filename, newline="") as file:
        for line_no, row in enumerate(csv.reader(file), start=1):
            if not row:
                continue
            if line_no == 1 and row[0].strip().lower() == "member":
                continue                      # header line
            if len(row) != 5:
                errors.append(f"Line {line_no}: expected 5 fields")
                continue
            try:
                add_class(timetable, *row)
            except ValueError as err:
                errors.append(f"Line {line_no}: {err}")
    return timetable, errors


# -------------------------------------------------------------- core algorithms
def find_clashes(classes):
    """Find overlapping classes in a list of (start, end, subject) of one day.
    Returns a list of (class1, class2, overlap_start, overlap_end)."""
    ordered = sorted(classes)
    clashes = []
    for i in range(len(ordered)):
        for j in range(i + 1, len(ordered)):
            if ordered[j][0] >= ordered[i][1]:
                break                         # later classes start even later
            clashes.append((ordered[i], ordered[j],
                            ordered[j][0], min(ordered[i][1], ordered[j][1])))
    return clashes


def merge_intervals(intervals):
    """Merge overlapping or touching (start, end) intervals."""
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def find_free_slots(timetable, members, day, min_duration=60):
    """Common free slots of the given members on a day, inside college hours."""
    busy = []
    for member in members:
        for start, end, _ in timetable[member].get(day, []):
            busy.append((start, end))
    free, cursor = [], COLLEGE_START
    for start, end in merge_intervals(busy):
        if end <= COLLEGE_START:
            continue
        if start >= COLLEGE_END:
            break
        if start - cursor >= min_duration:
            free.append((cursor, start))
        cursor = max(cursor, end)
    if COLLEGE_END - cursor >= min_duration:
        free.append((cursor, COLLEGE_END))
    return free


# ---------------------------------------------------------------- report lines
def timetable_lines(timetable, member):
    lines = [f"Timetable of {member}:"]
    for day in DAYS:
        for start, end, subject in sorted(timetable[member].get(day, [])):
            lines.append(f"  {day:<10} {to_time(start)}-{to_time(end)}  {subject}")
    if len(lines) == 1:
        lines.append("  (no classes)")
    return lines


def clash_lines(timetable, member):
    lines, found = [], False
    for day in DAYS:
        for c1, c2, o_start, o_end in find_clashes(timetable[member].get(day, [])):
            found = True
            lines.append(f"{member}: clash on {day} - {c1[2]} vs {c2[2]} "
                         f"({to_time(o_start)}-{to_time(o_end)})")
    if not found:
        lines.append(f"{member}: no clashes")
    return lines


def free_slot_lines(timetable, members, days, min_duration):
    lines = [f"Common free slots for {', '.join(members)} "
             f"(min {min_duration} min):"]
    for day in days:
        slots = find_free_slots(timetable, members, day, min_duration)
        if slots:
            text = ", ".join(f"{to_time(s)}-{to_time(e)}" for s, e in slots)
        else:
            text = "no common free slot"
        lines.append(f"  {day:<10} {text}")
    return lines


def save_report(lines, filename=REPORT_FILE):
    with open(filename, "w") as file:
        file.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- user interface
def choose_members(timetable):
    print("Members:", ", ".join(timetable))
    text = input("Enter member names separated by comma (or 'all'): ").strip()
    if text.lower() == "all":
        return list(timetable)
    names = [n.strip() for n in text.split(",") if n.strip()]
    unknown = [n for n in names if n not in timetable]
    if unknown or not names:
        print("Unknown or empty member list:", ", ".join(unknown) or "(none)")
        return []
    return names


def show(lines, log):
    for line in lines:
        print(line)
    log.extend(lines)
    log.append("")


def menu_load(timetable):
    name = input(f"File name [{DATA_FILE}]: ").strip() or DATA_FILE
    if not os.path.exists(name):
        print("File not found.")
        return
    loaded, errors = load_timetable(name)
    timetable.clear()
    timetable.update(loaded)
    print(f"Loaded {len(timetable)} member(s).")
    for err in errors:
        print("  Skipped ->", err)


def menu_add(timetable):
    try:
        add_class(timetable,
                  input("Member: "), input("Day: "),
                  input("Start (HH:MM): "), input("End (HH:MM): "),
                  input("Subject: "))
        print("Class added.")
    except ValueError as err:
        print("Error:", err)


def menu_free_slots(timetable, log):
    members = choose_members(timetable)
    if not members:
        return
    day = input("Day (or 'all'): ").strip().capitalize()
    days = DAYS if day == "All" else [day]
    if days[0] not in DAYS:
        print("Invalid day.")
        return
    text = input("Minimum duration in minutes [60]: ").strip() or "60"
    if not text.isdigit() or int(text) == 0:
        print("Duration must be a positive number.")
        return
    show(free_slot_lines(timetable, members, days, int(text)), log)


def main():
    timetable, log = {}, []
    if os.path.exists(DATA_FILE):
        timetable, errors = load_timetable(DATA_FILE)
        print(f"Loaded {len(timetable)} member(s) from {DATA_FILE}.")
        for err in errors:
            print("  Skipped ->", err)
    while True:
        print("\n===== Timetable Clash Detector and Free-Slot Finder =====")
        print("1. Load timetable file     2. Add a class")
        print("3. View timetable          4. Check clashes")
        print("5. Find common free slots  6. Save report")
        print("7. Exit")
        choice = input("Enter choice: ").strip()
        if choice == "7":
            print("Goodbye!")
            break
        if choice == "1":
            menu_load(timetable)
        elif choice == "2":
            menu_add(timetable)
        elif choice in ("3", "4", "5", "6") and not timetable:
            print("No data loaded. Use option 1 or 2 first.")
        elif choice == "3":
            for member in choose_members(timetable):
                show(timetable_lines(timetable, member), log)
        elif choice == "4":
            for member in choose_members(timetable):
                show(clash_lines(timetable, member), log)
        elif choice == "5":
            menu_free_slots(timetable, log)
        elif choice == "6":
            save_report(log)
            print(f"Report saved to {REPORT_FILE}.")
        else:
            print("Invalid choice. Enter a number from 1 to 7.")


if __name__ == "__main__":
    main()
