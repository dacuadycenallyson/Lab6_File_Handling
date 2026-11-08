import csv
import json
import shutil
from pathlib import Path

# Student-specific values
SEED_DIGIT = 1
TARGET_YEAR = 2015 + SEED_DIGIT

# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "Global_Cybersecurity_Threats_2015-2024.csv"
OUTPUT_DIR = BASE_DIR / "output"
BACKUP_DIR = BASE_DIR / "backup"

FILTERED_CSV = OUTPUT_DIR / "cybersecurity_2016_filtered.csv"
SUMMARY_JSON = OUTPUT_DIR / "cybersecurity_2016_summary.json"
BACKUP_JSON = BACKUP_DIR / "cybersecurity_2016_summary_backup.json"
REPORT_TXT = OUTPUT_DIR / "cybersecurity_2016_report.txt"

# Dataset column names
YEAR_FIELD = "Year"
ATTACK_FIELD = "Attack Type"
LOSS_FIELD = "Financial Loss (in Million $)"


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    BACKUP_DIR.mkdir(exist_ok=True)

    total_records = 0
    valid_records = 0
    invalid_records = 0
    filtered_records = 0

    attack_counts = {}
    total_loss = 0.0
    incidents = []

    print("=" * 60)
    print("CYBERSECURITY INCIDENT REPORT")
    print("=" * 60)
    print(f"Student Seed Digit: {SEED_DIGIT}")
    print(f"Target Year: {TARGET_YEAR}")

    # Read dataset one row at a time
    with open(DATA_FILE, "r", newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)

        required_fields = [YEAR_FIELD, ATTACK_FIELD, LOSS_FIELD]

        if not reader.fieldnames or not all(
            field in reader.fieldnames for field in required_fields
        ):
            raise ValueError("The dataset is missing required columns.")

        with open(FILTERED_CSV, "w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=reader.fieldnames)
            writer.writeheader()

            for row in reader:
                total_records += 1

                try:
                    if not all(row.get(field) for field in required_fields):
                        raise ValueError("Missing required field")

                    year = int(row[YEAR_FIELD])

                    if year == TARGET_YEAR:
                        loss_text = row[LOSS_FIELD].replace(",", "").strip()
                        loss = float(loss_text)

                        if loss < 0:
                            raise ValueError("Negative financial loss")

                        attack_type = row[ATTACK_FIELD].strip()

                        writer.writerow(row)

                        attack_counts[attack_type] = (
                            attack_counts.get(attack_type, 0) + 1
                        )

                        total_loss += loss

                        incidents.append({
                            "attack_type": attack_type,
                            "financial_loss": loss,
                            "original_order": filtered_records + 1
                        })

                        filtered_records += 1

                    valid_records += 1

                except (ValueError, TypeError):
                    invalid_records += 1

    # Calculate financial statistics
    if filtered_records > 0:
        average_loss = total_loss / filtered_records
    else:
        average_loss = None

    # Sort by financial loss, preserving original order for ties
    costliest_incidents = sorted(
        incidents,
        key=lambda item: (-item["financial_loss"], item["original_order"])
    )[:5]

    # Create JSON summary
    summary = {
        "student_seed_digit": SEED_DIGIT,
        "target_year": TARGET_YEAR,
        "total_records_processed": total_records,
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "filtered_incidents": filtered_records,
        "attack_type_counts": attack_counts,
        "total_financial_loss_million": total_loss,
        "average_financial_loss_million": average_loss,
        "five_costliest_incidents": [
            {
                "attack_type": item["attack_type"],
                "financial_loss_million": item["financial_loss"]
            }
            for item in costliest_incidents
        ]
    }

    with open(SUMMARY_JSON, "w", encoding="utf-8") as json_file:
        json.dump(summary, json_file, indent=4)

    # Back up JSON summary
    shutil.copy2(SUMMARY_JSON, BACKUP_JSON)

    # Verify JSON backup contents
    with open(SUMMARY_JSON, "r", encoding="utf-8") as original:
        original_data = json.load(original)

    with open(BACKUP_JSON, "r", encoding="utf-8") as backup:
        backup_data = json.load(backup)

    backup_verified = original_data == backup_data

    # Generate text report
    report_lines = [
        "=" * 60,
        "CYBERSECURITY INCIDENT REPORT",
        "=" * 60,
        f"Student Seed Digit: {SEED_DIGIT}",
        f"Target Year: {TARGET_YEAR}",
        "",
        f"Total Records Processed: {total_records}",
        f"Valid Records: {valid_records}",
        f"Invalid Records: {invalid_records}",
        f"Filtered Incidents: {filtered_records}",
        "",
        "ATTACK TYPE COUNTS:"
    ]

    for attack_type, count in sorted(attack_counts.items()):
        report_lines.append(f"{attack_type}: {count}")

    report_lines.extend([
        "",
        f"Total Financial Loss: ${total_loss:.2f} million"
    ])

    if average_loss is not None:
        report_lines.append(
            f"Average Financial Loss: ${average_loss:.2f} million"
        )
    else:
        report_lines.append("Average Financial Loss: Not available")

    report_lines.extend([
        "",
        "FIVE COSTLIEST INCIDENTS:"
    ])

    if costliest_incidents:
        for index, incident in enumerate(costliest_incidents, start=1):
            report_lines.append(
                f"{index}. {incident['attack_type']} - "
                f"${incident['financial_loss']:.2f} million"
            )
    else:
        report_lines.append("No matching incidents found.")

    report_lines.extend([
        "",
        "OUTPUT FILE INFORMATION:",
        f"Filtered CSV: {FILTERED_CSV}",
        f"JSON Summary: {SUMMARY_JSON}",
        f"JSON Backup: {BACKUP_JSON}",
        f"Text Report: {REPORT_TXT}",
        f"Backup File Size: {BACKUP_JSON.stat().st_size} bytes",
        f"Backup Verification: {'SUCCESS' if backup_verified else 'FAILED'}",
        "=" * 60
    ])

    with open(REPORT_TXT, "w", encoding="utf-8") as report:
        report.write("\n".join(report_lines) + "\n")

    # Display results
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    print(f"Total Records Processed: {total_records}")
    print(f"Valid Records: {valid_records}")
    print(f"Invalid Records: {invalid_records}")
    print(f"Target Year: {TARGET_YEAR}")
    print(f"Filtered Incidents: {filtered_records}")

    print("\nATTACK TYPE COUNTS:")
    for attack_type, count in sorted(attack_counts.items()):
        print(f"{attack_type}: {count}")

    print(f"\nTotal Financial Loss: ${total_loss:.2f} million")

    if average_loss is not None:
        print(f"Average Financial Loss: ${average_loss:.2f} million")
    else:
        print("Average Financial Loss: Not available")

    print("\nFIVE COSTLIEST INCIDENTS:")
    if costliest_incidents:
        for index, incident in enumerate(costliest_incidents, start=1):
            print(
                f"{index}. {incident['attack_type']} - "
                f"${incident['financial_loss']:.2f} million"
            )
    else:
        print("No matching incidents found.")

    print("\nOUTPUT FILES:")
    print(f"Filtered CSV: {FILTERED_CSV}")
    print(f"JSON Summary: {SUMMARY_JSON}")
    print(f"JSON Backup: {BACKUP_JSON}")
    print(f"Text Report: {REPORT_TXT}")

    print(f"\nBackup Verification: {'SUCCESS' if backup_verified else 'FAILED'}")
    print(f"Backup File Size: {BACKUP_JSON.stat().st_size} bytes")

    print("\n" + "=" * 60)
    print("CYBERSECURITY INCIDENT REPORT COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()