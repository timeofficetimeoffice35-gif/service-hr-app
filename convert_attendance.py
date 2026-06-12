#!/usr/bin/env python3
"""
AttendanceReport.csv  →  attendance_data.json
Isi folder mein AttendanceReport.csv rakhein aur run karein:
  python3 convert_attendance.py

CSV Column Layout (0-indexed):
  0=SNo, 1=Attendance Date, 2=Emp Index, 3=Emp Id, 4=Employee Name,
  5=Position Name, 6=Department Name, 7=SubDepartment Name, 8=Location Name,
  9=Grade, 10=Roster Code, 11=Roster Description,
  12=Emp In, 13=Date In, 14=Emp Out, 15=Date Out,
  16=Actual Work Hours, 17=Standard Work Hours,
  18=Late Coming, 19=Early Going,
  20=Calculated OverTime, 21=Approved OverTime,
  22=Remarks
"""
import json, sys, csv
from pathlib import Path

ROOT = Path(__file__).parent

# Exact header names to find column indices dynamically
COL_MAP = {
    "date":     ["attendance date"],
    "emp_in":   ["emp in"],
    "emp_out":  ["emp out"],
    "hrs":      ["actual work hours"],
    "ot":       ["calculated overtime", "calculated over time"],
    "remarks":  ["remarks"],
    "emp_id":   ["emp id"],
    "emp_name": ["employee name"],
    "position": ["position name"],
    "dept":     ["department name"],
}

def find_file():
    for name in ["AttendanceReport.csv", "AttendanceReport.htm",
                 "AttendanceReport.html", "AttendanceReport.xls"]:
        p = ROOT / name
        if p.exists():
            return p
    return None

def parse_html_xls(path):
    from bs4 import BeautifulSoup
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    table = soup.find_all("table")[0]
    rows = table.find_all("tr")
    data = {}
    for row in rows:
        cells = [c.get_text(strip=True) for c in row.find_all(["td","th"])]
        if len(cells) >= 23 and cells[3] and cells[3].isdigit():
            eid = cells[3].strip()
            if eid not in data:
                data[eid] = {"n": cells[4], "p": cells[5], "d": cells[6], "r": []}
            data[eid]["r"].append([cells[1], cells[12], cells[14], cells[16], cells[20], cells[22]])
    return data

def parse_csv(path):
    data = {}
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        rows = list(csv.reader(f))

    # Find header row — look for exact "Emp Id" match
    header_idx = None
    for i, row in enumerate(rows):
        joined = [c.strip().lower() for c in row]
        if "emp id" in joined and "attendance date" in joined:
            header_idx = i
            break
    if header_idx is None:
        print("ERROR: Could not find header row in CSV!")
        sys.exit(1)

    headers = [h.strip().lower() for h in rows[header_idx]]

    def find_col(names):
        """Find exact column index for a list of possible header names."""
        for name in names:
            for i, h in enumerate(headers):
                if h == name:
                    return i
        return None

    # Get exact column indices
    idx = {k: find_col(v) for k, v in COL_MAP.items()}

    # Verify critical columns found
    for k in ["emp_id", "date", "emp_in", "emp_out", "hrs"]:
        if idx[k] is None:
            print(f"WARNING: Column '{k}' not found, will use empty string")

    def get(row, key):
        i = idx.get(key)
        if i is None or i >= len(row):
            return ""
        return row[i].strip()

    for row in rows[header_idx + 1:]:
        if not row or len(row) < 5:
            continue
        eid = get(row, "emp_id")
        if not eid or not eid.isdigit():
            continue

        emp_name = get(row, "emp_name")
        position = get(row, "position")
        dept     = get(row, "dept")

        if eid not in data:
            data[eid] = {"n": emp_name, "p": position, "d": dept, "r": []}

        data[eid]["r"].append([
            get(row, "date"),
            get(row, "emp_in"),
            get(row, "emp_out"),
            get(row, "hrs"),
            get(row, "ot"),
            get(row, "remarks"),
        ])
    return data

def main():
    f = find_file()
    if not f:
        print("ERROR: AttendanceReport.csv not found!")
        sys.exit(1)
    print(f"Processing: {f.name}")
    data = parse_html_xls(f) if f.suffix.lower() != ".csv" else parse_csv(f)
    out = ROOT / "attendance_data.json"
    with open(out, "w") as fp:
        json.dump(data, fp, separators=(',', ':'))
    print(f"Done! {len(data)} employees -> attendance_data.json")

if __name__ == "__main__":
    main()
