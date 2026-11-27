# Smart Timetable Clash Detector and Free-Slot Finder

Collaborative Python project for **Computational Thinking and Programming (2026CSAE100)**.

## What it does
- Reads weekly timetables of several students/faculty from a CSV file
- Detects clashing (overlapping) classes in a member's timetable
- Finds common free slots for a group within college hours (09:00-17:00)
- Validates input and saves a readable report

## How to run
```
python timetable.py     # menu-driven program
python tests.py         # automated tests
```
Requires Python 3 only (no external packages).

## Input format (`timetable.csv`)
```
member,day,start,end,subject
Piyush,Monday,09:00,10:00,Maths
```

## Files
| File | Description |
|---|---|
| `timetable.py` | Main program |
| `timetable.csv` | Sample data |
| `tests.py` | 8 automated tests |
| `report.txt` | Sample generated report |

## Team
PIYUSH RAJ, SHAURYA CHAUHAN, ADITYA KUMAR SINGH

