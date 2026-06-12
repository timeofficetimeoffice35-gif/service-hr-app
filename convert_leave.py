#!/usr/bin/env python3
"""
LeaveReport.csv  →  leave_data.json
Isi folder mein LeaveReport.csv rakhein aur run karein:
  python3 convert_leave.py
"""
import json, sys, csv
from pathlib import Path

ROOT = Path(__file__).parent

def find_file():
    for name in ["LeaveReport.csv", "LeaveReport.htm",
                 "LeaveReport.html", "LeaveReport.xls"]:
        p = ROOT / name
        if p.exists():
            return p
    return None

def parse_html_xls(path):
    from bs4 import BeautifulSoup
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    table = soup.find("table")
    rows = table.find_all("tr")
    data = {}
    for row in rows[3:]:
        cells = [c.get_text(strip=True) for c in row.find_all(["td","th"])]
        if len(cells) >= 17 and cells[3] and cells[3].isdigit():
            eid = cells[3].strip()
            data[eid] = {
                "emp_id": eid, "emp_name": cells[2],
                "position_name": cells[4], "doj": cells[5],
                "casual_allowed": cells[6], "casual_availed": cells[7],
                "casual_deducted": cells[8], "casual_closing": cells[9],
                "sick_allowed": cells[10], "sick_availed": cells[11],
                "sick_deducted": cells[12], "sick_closing": cells[13],
                "annual_allowed": cells[14], "annual_availed": cells[15],
                "annual_deducted": cells[16] if len(cells)>16 else "0",
                "annual_closing": cells[17] if len(cells)>17 else "0",
            }
    return data

def parse_csv(path):
    """
    CSV has a 2-row merged header (rows 7-8, 0-indexed).
    Data columns (0-indexed):
      0=S.No, 1=EmpIndex, 2=Name, 3=EmpId, 4=Position, 5=DOJ
      6=CasualAllowed, 7=CasualAvailed, 8=CasualDed, 9=CasualClosing
      10=SickAllowed, 11=SickAvailed, 12=SickDed, 13=SickClosing
      14=AnnualAllowed, 15=AnnualAvailed, 16=AnnualDed, 17=AnnualClosing
    """
    data = {}
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        rows = list(csv.reader(f))

    # Find data start row: first row where col[3] is a numeric emp id
    data_start = None
    for i, row in enumerate(rows):
        if len(row) > 3 and row[3].strip().isdigit():
            data_start = i
            break

    if data_start is None:
        print("ERROR: Could not find data rows in CSV!")
        sys.exit(1)

    for row in rows[data_start:]:
        if len(row) < 10:
            continue
        eid = row[3].strip()
        if not eid or not eid.isdigit():
            continue

        def get(idx):
            try:
                return row[idx].strip()
            except IndexError:
                return "0"

        data[eid] = {
            "emp_id":           eid,
            "emp_name":         get(2),
            "position_name":    get(4),
            "doj":              get(5),
            "casual_allowed":   get(6),
            "casual_availed":   get(7),
            "casual_deducted":  get(8),
            "casual_closing":   get(9),
            "sick_allowed":     get(10),
            "sick_availed":     get(11),
            "sick_deducted":    get(12),
            "sick_closing":     get(13),
            "annual_allowed":   get(14),
            "annual_availed":   get(15),
            "annual_deducted":  get(16),
            "annual_closing":   get(17),
        }
    return data

def main():
    f = find_file()
    if not f:
        print("ERROR: LeaveReport.csv not found!")
        sys.exit(1)
    print(f"Processing: {f.name}")
    data = parse_html_xls(f) if f.suffix.lower() != ".csv" else parse_csv(f)
    out = ROOT / "leave_data.json"
    with open(out, "w") as fp:
        json.dump(data, fp, separators=(',', ':'))
    print(f"Done! {len(data)} employees -> leave_data.json")

if __name__ == "__main__":
    main()
