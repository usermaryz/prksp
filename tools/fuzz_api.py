#!/usr/bin/env python3
"""
Фуззинг-тестирование HTTP API (PRKSP FastAPI).

Проверяем устойчивость: случайные строки, поля, query/path/body.
Критерий успеха: ни одного ответа 5xx (ожидаемы 4xx/401/422 при мусоре).

Для пояснительной записки: сохраните вывод в файл или используйте --json-log.
Повторный прогон с тем же --seed даёт те же случайные параметры.
"""

from __future__ import annotations

import argparse
import json
import random
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from typing import Any


def rand_str(n: int = 12) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits + " \n\t\"'\\<>/%", k=n))


def rand_jsonish() -> str:
    """Иногда валидный JSON, иногда мусор — сервер не должен падать 500."""
    if random.random() < 0.4:
        return json.dumps({"x": rand_str(8), "n": random.choice([None, True, -1e9, [], {}])})
    return rand_str(random.randint(1, 80))


def request_json(
    method: str,
    url: str,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 10,
    truncate: int | None = 800,
) -> tuple[int, str]:
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            if truncate is not None:
                body = body[:truncate]
            return resp.getcode(), body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if truncate is not None:
            body = body[:truncate]
        return int(e.code), body


def main() -> int:
    p = argparse.ArgumentParser(
        description="Фуззинг API (только stdlib): случайные запросы, проверка на отсутствие 5xx.",
    )
    p.add_argument("--base", default="http://127.0.0.1:8000", help="База URL без финального /")
    p.add_argument("--token", default="", help="JWT access (если пусто — логин admin/admin)")
    p.add_argument("--rounds", type=int, default=60, help="Число случайных GET-запросов")
    p.add_argument("--seed", type=int, default=None, help="Seed RNG для воспроизводимости")
    p.add_argument("--json-log", default="", help="Путь: записать сводку JSON в файл")
    args = p.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    base = args.base.rstrip("/")
    token = args.token.strip()
    status_hist: Counter[int] = Counter()
    fails: list[tuple[str, int, str]] = []
    t0 = time.perf_counter()

    def check(name: str, code: int, body: str) -> None:
        status_hist[code] += 1
        if code >= 500:
            fails.append((name, code, body))
        print(f"{name}\t{code}")

    def ping() -> bool:
        try:
            c, b = request_json("GET", f"{base}/health")
            check("health", c, b)
            return c == 200
        except urllib.error.URLError as e:
            print(f"health\tERR\t{e.reason}", file=sys.stderr)
            return False

    if not ping():
        print("Сервер недоступен. Запустите API, например: cd backend_fastapi && uvicorn app.main:app --host 127.0.0.1 --port 8000", file=sys.stderr)
        return 2

    if not token:
        login_data = urllib.parse.urlencode({"username": "admin", "password": "admin"}).encode()
        code, body = request_json(
            "POST",
            f"{base}/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            truncate=None,
        )
        check("login", code, body)
        if code == 200:
            try:
                token = json.loads(body).get("access_token", "")
            except json.JSONDecodeError:
                token = ""

    hdr: dict[str, str] = {}
    if token:
        hdr["Authorization"] = f"Bearer {token}"
    else:
        print("Предупреждение: нет токена, защищённые маршруты дадут 401.", file=sys.stderr)

    # --- Зафиксированные GET с «шумными» query (не должны давать 500) ---
    static_gets = [
        "/api/dashboard/metrics",
        "/api/inventory/zones",
        "/api/picking/tasks",
        "/api/picking/stats",
        "/api/logistics/shipments",
        "/api/logistics/carriers",
        "/api/logistics/stats",
    ]
    for path in static_gets:
        c, b = request_json("GET", base + path, headers=hdr)
        check(f"get_{path.replace('/', '_')}", c, b)

    c, b = request_json("GET", f"{base}/api/auth/me", headers=hdr)
    check("get_auth_me", c, b)

    # --- Случайные GET с query/path ---
    for i in range(args.rounds):
        ready = random.choice(["", "true", "false", "1", "0", rand_str(4), "maybe"])
        q_orders = urllib.parse.urlencode(
            {
                "status": rand_str(8),
                "page": str(random.randint(-5, 9999)),
                "limit": str(random.randint(-1, 999)),
                "ready_for_shipping": ready,
            }
        )
        oid = random.randint(-10, 10_000)
        tid = random.randint(-10, 10_000)
        path = random.choice(
            [
                f"/api/orders?{q_orders}",
                f"/api/products?search={urllib.parse.quote(rand_str(24))}&page={random.randint(0, 5)}&limit={random.randint(1, 600)}",
                f"/api/picking/tasks",
                f"/api/orders/{oid}/status?status={urllib.parse.quote(rand_str(6))}",
                f"/api/products/{tid}",
                f"/api/picking/tasks/{tid}/start",
                f"/api/picking/tasks/{tid}/complete",
            ]
        )
        # PATCH /status — иногда GET (405), иногда PATCH с мусорным status (422/400)
        method = "PATCH" if "/status?" in path and random.random() < 0.5 else "GET"
        c, b = request_json(method, base + path, headers=hdr)
        check(f"rand_{i}_{method.lower()}", c, b)

    # --- Регистрация: заведомо невалидные данные ---
    for i in range(max(8, args.rounds // 5)):
        payload: dict[str, Any] = {
            "username": rand_str(6),
            "email": f"{rand_str(4)}@{rand_str(3)}.ru",
            "password": rand_str(8),
            "full_name": rand_str(10),
            "role": random.choice(["admin", "manager", "picker", "driver", rand_str(4), ""]),
        }
        raw = json.dumps(payload).encode()
        c, b = request_json(
            "POST",
            f"{base}/api/auth/register",
            data=raw,
            headers={"Content-Type": "application/json"},
        )
        check(f"register_fuzz_{i}", c, b)

    # --- Refresh / logout с мусором ---
    for i in range(6):
        c, b = request_json(
            "POST",
            f"{base}/api/auth/refresh",
            data=json.dumps({"refresh_token": rand_str(40)}).encode(),
            headers={"Content-Type": "application/json"},
        )
        check(f"refresh_fuzz_{i}", c, b)
    c, b = request_json(
        "POST",
        f"{base}/api/auth/logout",
        data=rand_jsonish().encode(),
        headers={"Content-Type": "application/json"},
    )
    check("logout_garbage_body", c, b)

    # --- POST с невалидным JSON (часть байт не JSON) ---
    for i in range(5):
        garbage = (b'{"a": ' + rand_str(30).encode("utf-8", errors="replace"))[: random.randint(5, 40)]
        c, b = request_json(
            "POST",
            f"{base}/api/auth/login",
            data=garbage,
            headers={"Content-Type": "application/json"},
        )
        check(f"login_bad_json_{i}", c, b)

    # --- С токеном admin: создание сущностей с «ломаными» полями ---
    if token:
        for i in range(max(10, args.rounds // 6)):
            kind = random.choice(["order", "product", "shipment"])
            if kind == "order":
                body_d: dict[str, Any] = {
                    "customer_name": rand_str(random.randint(0, 400)),
                    "customer_phone": rand_str(100),
                    "customer_address": rand_str(600),
                }
                url = f"{base}/api/orders"
            elif kind == "product":
                body_d = {
                    "sku": rand_str(random.randint(0, 80)),
                    "name": rand_str(random.randint(0, 300)),
                    "price": random.choice([-1, 0, 1e9, "x", None, True]),
                    "stock": random.choice([-5, 0, 1e12, "n"]),
                    "description": rand_str(50),
                }
                url = f"{base}/api/products"
            else:
                body_d = {
                    "order_id": random.choice([-1, 0, 999999, "bad"]),
                    "carrier_id": random.choice([-1, 0, 99999]),
                    "delivery_method": random.choice(["courier", "pickup", "post", rand_str(6), ""]),
                }
                url = f"{base}/api/logistics/shipments"
            raw = json.dumps(body_d, default=str).encode()
            c, b = request_json("POST", url, data=raw, headers={**hdr, "Content-Type": "application/json"})
            check(f"post_{kind}_fuzz_{i}", c, b)

    elapsed = time.perf_counter() - t0
    summary = {
        "base": base,
        "seed": args.seed,
        "elapsed_sec": round(elapsed, 3),
        "status_histogram": dict(sorted(status_hist.items())),
        "failures_5xx": [{"name": n, "code": c, "body_preview": b[:200]} for n, c, b in fails],
    }

    if args.json_log:
        with open(args.json_log, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"\nСводка записана: {args.json_log}")

    if fails:
        print("\nОшибки сервера (ожидалось 0 строк):")
        for name, code, body in fails:
            print(name, code, body)
        return 1

    print(f"\nОк: ни одного ответа 5xx за прогон ({elapsed:.2f} с). Коды: {dict(sorted(status_hist.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
