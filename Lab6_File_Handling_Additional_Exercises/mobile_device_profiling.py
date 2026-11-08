import csv
import json
import shutil
from pathlib import Path

# Student-specific values
SEED_DIGIT = 1
TARGET_OS = "iOS"
TARGET_BEHAVIOR_CLASS = (SEED_DIGIT % 5) + 1

# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "user_behavior_dataset.csv"
OUTPUT_DIR = BASE_DIR / "output"
BACKUP_DIR = BASE_DIR / "backup"

FILTERED_CSV = OUTPUT_DIR / "mobile_usage_filtered.csv"
SUMMARY_JSON = OUTPUT_DIR / "mobile_usage_summary.json"
BACKUP_CSV = BACKUP_DIR / "mobile_usage_filtered_backup.csv"

# Required exported columns
EXPORT_FIELDS = [
    "User ID",
    "Device Model",
    "Operating System",
    "Battery Drain (mAh/day)",
    "Data Usage (MB/day)"
]


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    BACKUP_DIR.mkdir(exist_ok=True)

    total_records = 0
    valid_records = 0
    invalid_records = 0
    exported_records = 0

    battery_total = 0.0
    data_total = 0.0

    print("=" * 55)
    print("MOBILE DEVICE USAGE PROFILING")
    print("=" * 55)
    print(f"Student Seed Digit: {SEED_DIGIT}")
    print(f"Target Operating System: {TARGET_OS}")
    print(f"Target Behavior Class: {TARGET_BEHAVIOR_CLASS}")

    # Read the source CSV one row at a time
    with open(DATA_FILE, "r", newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)

        required_fields = EXPORT_FIELDS + ["User Behavior Class"]

        if not reader.fieldnames or not all(
            field in reader.fieldnames for field in required_fields
        ):
            raise ValueError("The dataset is missing one or more required columns.")

        with open(FILTERED_CSV, "w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=EXPORT_FIELDS)
            writer.writeheader()

            for row in reader:
                total_records += 1

                try:
                    if not all(row.get(field) for field in required_fields):
                        raise ValueError("Missing required field")

                    behavior_class = int(row["User Behavior Class"])

                    if (
                        row["Operating System"].strip() == TARGET_OS
                        and behavior_class == TARGET_BEHAVIOR_CLASS
                    ):
                        battery = float(row["Battery Drain (mAh/day)"])
                        data_usage = float(row["Data Usage (MB/day)"])

                        if battery < 0 or data_usage < 0:
                            raise ValueError("Negative usage value")

                        writer.writerow({
                            field: row[field] for field in EXPORT_FIELDS
                        })

                        battery_total += battery
                        data_total += data_usage
                        exported_records += 1

                    valid_records += 1

                except (ValueError, TypeError):
                    invalid_records += 1

    # Calculate averages
    if exported_records > 0:
        average_battery = battery_total / exported_records
        average_data = data_total / exported_records
    else:
        average_battery = None
        average_data = None

    # Verify exported CSV record count
    verified_count = 0
    with open(FILTERED_CSV, "r", newline="", encoding="utf-8") as filtered:
        exported_reader = csv.DictReader(filtered)
        for _ in exported_reader:
            verified_count += 1

    verification_success = verified_count == exported_records

    # Create JSON summary
    summary = {
        "student_seed_digit": SEED_DIGIT,
        "target_operating_system": TARGET_OS,
        "target_behavior_class": TARGET_BEHAVIOR_CLASS,
        "total_records_processed": total_records,
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "exported_records": exported_records,
        "average_battery_drain_mAh_per_day": average_battery,
        "average_data_usage_MB_per_day": average_data,
        "verified_exported_count": verified_count,
        "export_verification": verification_success
    }

    with open(SUMMARY_JSON, "w", encoding="utf-8") as json_file:
        json.dump(summary, json_file, indent=4)

    # Back up the filtered CSV
    shutil.copy2(FILTERED_CSV, BACKUP_CSV)

    backup_success = (
        BACKUP_CSV.exists()
        and BACKUP_CSV.stat().st_size == FILTERED_CSV.stat().st_size
    )

    print("\n" + "=" * 55)
    print("ANALYSIS RESULTS")
    print("=" * 55)
    print(f"Total Records Processed: {total_records}")
    print(f"Valid Records: {valid_records}")
    print(f"Invalid Records: {invalid_records}")
    print(f"Target Operating System: {TARGET_OS}")
    print(f"Target Behavior Class: {TARGET_BEHAVIOR_CLASS}")
    print(f"Matching Records Exported: {exported_records}")

    if exported_records > 0:
        print(f"Average Battery Drain: {average_battery:.2f} mAh/day")
        print(f"Average Data Usage: {average_data:.2f} MB/day")
    else:
        print("No matching records found. Averages are unavailable.")

    print("\nOUTPUT FILES:")
    print(f"Filtered CSV: {FILTERED_CSV}")
    print(f"JSON Summary: {SUMMARY_JSON}")
    print(f"Backup CSV: {BACKUP_CSV}")

    print(f"\nExport Verification: {'SUCCESS' if verification_success else 'FAILED'}")
    print(f"Backup Verification: {'SUCCESS' if backup_success else 'FAILED'}")
    print(f"Backup File Size: {BACKUP_CSV.stat().st_size} bytes")

    print("\n" + "=" * 55)
    print("MOBILE DEVICE PROFILING COMPLETED")
    print("=" * 55)


if __name__ == "__main__":
    main()