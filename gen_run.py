#!/usr/bin/env python3
import argparse, csv, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import termux_guest_gen as g

MAXLEN = 12

def normalizar(nombre: str) -> str:
    return nombre.strip()[:MAXLEN]

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=5)
    p.add_argument("--name", default="US")
    p.add_argument("--names", default="")
    p.add_argument("--region", default="US")
    p.add_argument("--max-tries", type=int, default=3)
    a = p.parse_args()

    accounts = g.load_accounts()
    proxies = g.load_proxies()
    existentes = {str(x.get("nickname", "")).lower() for x in accounts}

    # Lista de nombres exactos, si la hay
    lista = [normalizar(n) for n in a.names.split(",") if n.strip()]
    lista = [n for n in lista if len(n) >= 3 and n.lower() not in existentes]
    if a.names.strip() and not lista:
        print("La lista quedó vacía o ya existe toda. Abortando.")
        return 1

    base = normalizar(a.name) or "US"
    start = g.find_next_superscript_number(accounts, base)
    print(f"Base: {len(accounts)} cuentas | Proxies US: {len(proxies)} | Lista exacta: {len(lista)}")

    made, tries, i, usados = [], 0, 0, set()
    limite = max(a.count * a.max_tries, a.count)

    while i < a.count and tries < limite:
        if lista and i < len(lista):
            nick = lista[i]
        else:
            nick = g.format_nickname(base, start + (i - len(lista)))
        if nick.lower() in usados:
            i += 1
            continue

        tries += 1
        pwd = g.generate_gohar_branded_password()
        proxy = proxies[(tries - 1) % len(proxies)] if proxies else None
        print(f"[{tries}] {nick} ({len(nick)} car.) -> {proxy or 'directo'}", flush=True)

        acc = g.create_complete_guest_account(
            nickname=nick, password=pwd, region=a.region, proxy=proxy
        )
        if acc:
            acc["region"] = a.region.upper()
            made.append(acc)
            usados.add(nick.lower())
            i += 1
            print(f"    OK uid={acc['uid']}", flush=True)
        else:
            print("    FAIL (rate limit, proxy muerto o nombre tomado)", flush=True)
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
