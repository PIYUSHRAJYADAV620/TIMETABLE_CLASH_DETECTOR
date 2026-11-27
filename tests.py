"""Simple automated tests for timetable.py (run: python tests.py)."""
from timetable import (to_minutes, to_time, find_clashes, merge_intervals,
                       find_free_slots, add_class, COLLEGE_START, COLLEGE_END)

def t(h, m=0):
    return h * 60 + m

def test_time_conversion():
    assert to_minutes("09:30") == 570
    assert to_time(570) == "09:30"

def test_partial_overlap_is_clash():
    result = find_clashes([(t(9), t(11), "A"), (t(10), t(12), "B")])
    assert len(result) == 1 and result[0][2:] == (t(10), t(11))

def test_touching_classes_do_not_clash():
    assert find_clashes([(t(9), t(10), "A"), (t(10), t(11), "B")]) == []

def test_merge_intervals():
    assert merge_intervals([(t(9), t(11)), (t(10), t(12)), (t(14), t(15))]) == \
        [(t(9), t(12)), (t(14), t(15))]

def test_common_free_slots():
    tt = {}
    add_class(tt, "A", "Monday", "09:00", "10:00", "x")
    add_class(tt, "A", "Monday", "11:00", "12:00", "x")
    add_class(tt, "B", "Monday", "09:30", "11:30", "y")
    add_class(tt, "B", "Monday", "14:00", "15:00", "y")
    assert find_free_slots(tt, ["A", "B"], "Monday", 60) == \
        [(t(12), t(14)), (t(15), t(17))]

def test_fully_booked_day_has_no_slot():
    tt = {}
    add_class(tt, "A", "Monday", "09:00", "17:00", "x")
    assert find_free_slots(tt, ["A"], "Monday", 30) == []

def test_short_gap_ignored():
    tt = {}
    add_class(tt, "A", "Monday", "09:00", "10:00", "x")
    add_class(tt, "A", "Monday", "10:30", "17:00", "x")
    assert find_free_slots(tt, ["A"], "Monday", 60) == []
    assert find_free_slots(tt, ["A"], "Monday", 30) == [(t(10), t(10, 30))]

def test_invalid_input_rejected():
    for bad in [("A", "Funday", "09:00", "10:00", "x"),
                ("A", "Monday", "25:00", "26:00", "x"),
                ("A", "Monday", "10:00", "09:00", "x"),
                ("A", "Monday", "9-00", "10:00", "x")]:
        try:
            add_class({}, *bad)
        except ValueError:
            continue
        raise AssertionError(f"accepted bad entry {bad}")

if __name__ == "__main__":
    tests = [(n, f) for n, f in globals().items() if n.startswith("test_")]
    for name, func in tests:
        func()
        print(f"PASS  {name}")
    print(f"\nAll {len(tests)} tests passed.")
