import argparse
import logging
import time

import config
import report
from emailer import send_email


def setup_logging():
    config.LOG_FILE.parent.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(config.LOG_FILE), logging.StreamHandler()],
    )


def send_with_retry(*args, attempts=3, delay=5, **kwargs):
    for i in range(1, attempts + 1):
        try:
            return send_email(*args, **kwargs)
        except Exception as exc:
            logging.warning("Send attempt %d/%d failed: %s", i, attempts, exc)
            if i == attempts:
                raise
            time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(description="Generate and email the daily report.")
    parser.add_argument("--dry-run", action="store_true", help="print the report, don't send")
    parser.add_argument("--date", help="report date YYYY-MM-DD (default: latest in data)")
    args = parser.parse_args()

    setup_logging()
    summary = report.summarize(report.load_rows(), args.date)
    text, html = report.build_text(summary), report.build_html(summary)
    csv_path = report.save_csv(summary)
    logging.info("Report built for %s", summary["date"])

    if args.dry_run:
        print("\n" + text)
        return

    send_with_retry(
        subject=f"Daily Sales Report - {summary['date']}",
        text_body=text,
        html_body=html,
        attachments=[csv_path],
    )


if __name__ == "__main__":
    main()