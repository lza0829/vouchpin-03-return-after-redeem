from __future__ import annotations
from typing import Any
from app.db import connect
from app.repositories import settings as settings_repo
from app.repositories import facts as fact_repo
from app.repositories import batches as batch_repo
from app.repositories import events as event_repo


def dashboard() -> dict[str, Any]:
    conn = connect()
    try:
        day = settings_repo.get(conn, "business_day")
        facts = fact_repo.list_facts(conn, day)
        # 合计只认在效事实（open+sealed）；voided 已冲销、不再计入任何合计
        live = [f for f in facts if f["status"] != "voided"]
        open_n = sum(1 for f in live if f["status"] == "open")
        sealed_n = sum(1 for f in live if f["status"] == "sealed")
        total = round(sum(float(f["amount"]) for f in live), 2)
        events = event_repo.list_events(conn, day)
        batches = batch_repo.list_batches(conn)
        sealed_today = fact_repo.day_is_sealed(conn, day)
        return {
            "business_day": day,
            "event_count": len(events),
            "fact_count": len(live),
            "open_fact_count": open_n,
            "sealed_fact_count": sealed_n,
            "voided_fact_count": len(facts) - len(live),
            "redeem_total_today": total,
            "batch_count": len(batches),
            "day_sealed": sealed_today,
        }
    finally:
        conn.close()
