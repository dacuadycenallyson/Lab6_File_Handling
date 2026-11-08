import csv
import json
import shutil
from pathlib import Path
from collections import Counter

# ==========================================
# STUDENT-SPECIFIC INFORMATION
# ==========================================

SEED_DIGIT = 1
ID_SUM = 25

RECORDS_TO_PROCESS = 1000 + ID_SUM
TARGET_STATUS_CLASS = (SEED_DIGIT % 4) + 2

# ==========================================
# FILE LOCATIONS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "weblog.csv"

OUTPUT_DIR = BASE_DIR / "output"
BACKUP_DIR = BASE_DIR / "backup"

FILTERED_CSV = OUTPUT_DIR / "web_log_filtered.csv"
SUMMARY_JSON = OUTPUT_DIR / "web_log_summary.json"
BACKUP_JSON = BACKUP_DIR / "web_log_summary_backup.json"

# Create folders if they do not exist
OUTPUT_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)


def analyze_web_logs():

    status_counts = Counter()
    url_counts = Counter()

    records_processed = 0
    target_records = 0
    invalid_records = 0

    print("=" * 50)
    print("WEB SERVER ACCESS LOG ANALYSIS")
    print("=" * 50)

    print(f"Student Seed Digit: {SEED_DIGIT}")
    print(f"Student ID Sum: {ID_SUM}")
    print(f"Records to Process: {RECORDS_TO_PROCESS}")
    print(f"Target HTTP Status Class: {TARGET_STATUS_CLASS}xx")

    try:
        with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as infile:

            reader = csv.reader(infile)

            with open(FILTERED_CSV, "w", encoding="utf-8", newline="") as outfile:

                writer = csv.writer(outfile)

                writer.writerow(["IP", "Time", "URL", "Status"])

                for row in reader:

                    # Skip empty rows
                    if not row or all(not field.strip() for field in row):
                        continue

                    # Skip a possible header row
                    if records_processed == 0:
                        joined = " ".join(row).lower()
                        if "ip" in joined and (
                            "status" in joined or "staus" in joined
                        ):
                            continue

                    # Process only the first 1,025 data records
                    if records_processed >= RECORDS_TO_PROCESS:
                        break

                    records_processed += 1

                    try:
                        # Expected columns:
                        # IP, Time, Request URL, HTTP Status

                        if len(row) < 4:
                            raise ValueError("Missing fields")

                        ip_address = row[0].strip()
                        timestamp = row[1].strip().lstrip("[")
                        request = row[2].strip()
                        status = int(row[-1].strip())

                        if not ip_address or not timestamp or not request:
                            raise ValueError("Empty field")

                        # Extract requested URL from HTTP request
                        request_parts = request.split()

                        if len(request_parts) < 2:
                            raise ValueError("Invalid request URL")

                        requested_url = request_parts[1]

                        # Count all valid HTTP status codes
                        status_counts[status] += 1

                        # Select records belonging to target class
                        if status // 100 == TARGET_STATUS_CLASS:

                            target_records += 1

                            url_counts[requested_url] += 1

                            writer.writerow([
                                ip_address,
                                timestamp,
                                requested_url,
                                status
                            ])

                    except (ValueError, IndexError):
                        invalid_records += 1
                        continue

    except FileNotFoundError:
        print("\nERROR: weblog.csv was not found.")
        print(f"Expected location: {INPUT_FILE}")
        return

    # ==========================================
    # CREATE JSON SUMMARY
    # ==========================================

    top_five_urls = [
        {"url": url, "requests": count}
        for url, count in url_counts.most_common(5)
    ]

    summary = {
        "student_seed_digit": SEED_DIGIT,
        "student_id_sum": ID_SUM,
        "records_processed": records_processed,
        "target_status_class": f"{TARGET_STATUS_CLASS}xx",
        "valid_records": records_processed - invalid_records,
        "invalid_records": invalid_records,
        "records_in_target_class": target_records,
        "count_per_status_code": {
            str(code): count
            for code, count in sorted(status_counts.items())
        },
        "five_most_requested_urls": top_five_urls,
        "filtered_csv_file": str(FILTERED_CSV),
        "json_summary_file": str(SUMMARY_JSON)
    }

    with open(SUMMARY_JSON, "w", encoding="utf-8") as json_file:
        json.dump(summary, json_file, indent=4)

    # ==========================================
    # BACKUP JSON FILE
    # ==========================================

    shutil.copy2(SUMMARY_JSON, BACKUP_JSON)

    backup_verified = (
        BACKUP_JSON.exists()
        and BACKUP_JSON.stat().st_size == SUMMARY_JSON.stat().st_size
    )

    # ==========================================
    # DISPLAY RESULTS
    # ==========================================

    print("\n" + "=" * 50)
    print("ANALYSIS RESULTS")
    print("=" * 50)

    print(f"Records Processed: {records_processed}")
    print(f"Valid Records: {records_processed - invalid_records}")
    print(f"Invalid Records: {invalid_records}")
    print(f"Target Status Class: {TARGET_STATUS_CLASS}xx")
    print(f"Records in Target Class: {target_records}")

    print("\nCOUNT PER STATUS CODE:")

    for code, count in sorted(status_counts.items()):
        print(f"HTTP {code}: {count}")

    print("\nFIVE MOST REQUESTED URLs IN TARGET CLASS:")

    if top_five_urls:
        for item in top_five_urls:
            print(f"{item['url']} - {item['requests']} requests")
    else:
        print("No matching URLs found.")

    print("\nOUTPUT FILES:")
    print(f"Filtered CSV: {FILTERED_CSV}")
    print(f"JSON Summary: {SUMMARY_JSON}")
    print(f"JSON Backup: {BACKUP_JSON}")

    print(f"\nBackup Verification: {'SUCCESS' if backup_verified else 'FAILED'}")

    print("\n" + "=" * 50)
    print("WEB LOG ANALYSIS COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    analyze_web_logs()