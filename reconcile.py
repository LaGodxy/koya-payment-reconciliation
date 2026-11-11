#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

data_dir = Path(__file__).resolve().parent
latest = {}

with (data_dir / "payments.jsonl").open("rb") as payments:
    for line in payments:
        try:
            event = json.loads(line, parse_float=Decimal)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue

        if not isinstance(event, dict) or not event.get("txn_id"):
            continue

        txn_id = event["txn_id"]
        timestamp = datetime.fromisoformat(event["ts"].replace("Z", "+00:00"))
        if txn_id not in latest or timestamp >= latest[txn_id][0]:
            latest[txn_id] = (timestamp, event)

total = Decimal(0)
count = 0
for _, event in latest.values():
    if event["status"] == "success":
        amount = event["amount"]
        if isinstance(amount, str):
            amount = amount.replace(",", "")
        total += Decimal(amount)
        count += 1

expected = int((data_dir / "expected.txt").read_text(encoding="utf-8"))

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
