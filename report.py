#part2-imports & loading data
import csv
from collections import defaultdict
from datetime import date

import config


def load_rows(path=config.DATA_FILE):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["units"] = int(r["units"])
        r["revenue"] = float(r["revenue"])
    return rows

#part2-summarizing one day
def summarize(rows, report_date=None):
    report_date = report_date or max(r["date"] for r in rows)
    day_rows = [r for r in rows if r["date"] == report_date]
    if not day_rows:
        raise ValueError(f"No data found for {report_date}")

    by_product = defaultdict(lambda: {"units": 0, "revenue": 0.0})
    for r in day_rows:
        by_product[r["product"]]["units"] += r["units"]
        by_product[r["product"]]["revenue"] += r["revenue"]

    products = sorted(by_product.items(), key=lambda kv: kv[1]["revenue"], reverse=True)
    return {
        "date": report_date,
        "total_revenue": sum(r["revenue"] for r in day_rows),
        "total_units": sum(r["units"] for r in day_rows),
        "top_product": products[0][0],
        "products": products,
    }

#part3-plain-text version
def build_text(s):
    lines = [
        f"Daily Sales Report - {s['date']}",
        "=" * 36,
        f"Total revenue : ${s['total_revenue']:,.2f}",
        f"Units sold    : {s['total_units']}",
        f"Top product   : {s['top_product']}",
        "",
        "By product:",
    ]
    for name, v in s["products"]:
        lines.append(f"  {name:<12} {v['units']:>4} units  ${v['revenue']:>10,.2f}")
    return "\n".join(lines)

#part4-HTML version

def build_html(s):
    rows = "".join(
        f"<tr><td>{name}</td><td align='right'>{v['units']}</td>"
        f"<td align='right'>${v['revenue']:,.2f}</td></tr>"
        for name, v in s["products"]
    )
    return f"""\
<html><body style="font-family:Arial,sans-serif;color:#222">
<h2>Daily Sales Report &mdash; {s['date']}</h2>
<p><b>Total revenue:</b> ${s['total_revenue']:,.2f}<br>
<b>Units sold:</b> {s['total_units']}<br>
<b>Top product:</b> {s['top_product']}</p>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse">
<tr style="background:#f0f0f0"><th>Product</th><th>Units</th><th>Revenue</th></tr>
{rows}
</table>
<p style="color:#888;font-size:12px">Generated automatically on {date.today()}.</p>
</body></html>"""

#part5-CSV attachment
def save_csv(s):
    config.OUTPUT_DIR.mkdir(exist_ok=True)
    path = config.OUTPUT_DIR / f"report_{s['date']}.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["product", "units", "revenue"])
        for name, v in s["products"]:
            w.writerow([name, v["units"], f"{v['revenue']:.2f}"])
    return path