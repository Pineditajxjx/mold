#!/usr/bin/env python3
import argparse, csv, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import termux_guest_gen as g

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=5)
    p.add_argument("--name", default="US")
    p.add_argument("--region", default="US")
    p.add_argument("--max-tries", type=int, default=3)
    a = p.parse_args()

    accounts = g.load_accounts()
    proxies = g.load_proxies()
    print(f"Base: {len(accounts)} cuentas | Proxies US: {len(proxies)}")

    start = g.find_next_superscript_number(accounts, a.name)
    made, tries, i = [], 0, 0
    limite = max(a.count * a.max_tries, a.count)

    while i < a.count and tries < limite:
        tries += 1
        nick = g.format_nickname(a.name, start + i)
        pwd = g.generate_gohar_branded_password()
        proxy = proxies[(tries - 1) % len(proxies)] if proxies else None
        print(f"[{tries}] {nick} -> {proxy or 'directo'}", flush=True)
        acc = g.create_complete_guest_account(
            nickname=nick, password=pwd, region=a.region, proxy=proxy
        )
        if acc:
            acc["region"] = a.region.upper()
            made.append(acc)
            i += 1
            print(f"    OK uid={acc['uid']}", flush=True)
        else:
            print("    FAIL (rate limit o proxy muerto)", flush=True)
        time.sleep(2)

    with open("accounts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Nickname", "UID", "Password", "Region"])
        for acc in made:
            w.writerow([acc.get("nickname"), acc.get("uid"),
                        acc.get("password"), acc.get("region")])

    print(f"\nCreadas: {len(made)}/{a.count}")
    return 0 if made else 1

if __name__ == "__main__":
    sys.exit(main())
