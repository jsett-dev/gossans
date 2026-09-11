#!/usr/bin/env python3
"""Publish the mail authentication records for gossans.com at Cloudflare.

The domain sends through Microsoft 365 and already publishes SPF and MX. It
publishes neither DKIM nor DMARC, which means a forger can put gossans.com in
the From line of a message and most receivers have no instruction on what to
do about it. That is the gap this closes.

    set CLOUDFLARE_API_TOKEN, or write it to the token file named below
    python tools/dns.py            # show what would change, change nothing
    python tools/dns.py --apply    # write it
    python tools/dns.py --verify   # read the public DNS back

The token is never printed, never logged, and never written by this script.
It is read from the environment first and from a file outside every
repository second, so it cannot be committed by accident.

Scope the token to exactly one permission, Zone / DNS / Edit, and to the
gossans.com zone alone. A token that can only edit one zone's DNS cannot
touch billing, Pages, Workers, or any other domain.

DKIM is two halves and this script is only the first. Publishing the CNAMEs
does nothing until DKIM signing is switched on for the domain in the Microsoft
Defender portal, and Microsoft refuses to switch it on until the CNAMEs
resolve. So: run this, then enable it there. The targets below are derived
from the tenant name; if Defender shows different ones, pass them with
--selector1 and --selector2 rather than editing this file.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ZONE = "gossans.com"
TENANT = "gossans.onmicrosoft.com"

#: Deliberately outside every repository, so no .gitignore mistake can leak it.
TOKEN_FILE = Path.home() / ".gossans" / "cloudflare-token"

API = "https://api.cloudflare.com/client/v4"

# p=none is the honest starting policy: it asks receivers to report what they
# see and to change nothing. Tighten to quarantine once a fortnight of reports
# shows only Microsoft signing your mail, then to reject.
DMARC = "v=DMARC1; p=none; rua=mailto:hello@gossans.com; fo=1"


def token():
    t = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if t:
        return t, "environment"
    if TOKEN_FILE.exists():
        t = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if t:
            return t, str(TOKEN_FILE)
    raise SystemExit(
        "No Cloudflare token found.\n"
        "  Either set CLOUDFLARE_API_TOKEN in your environment,\n"
        "  or write the token as the only line of %s\n"
        "The token is read, never printed and never committed." % TOKEN_FILE)


def call(method, path, tok, body=None):
    req = urllib.request.Request(
        API + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": "Bearer " + tok,
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        # Never echo the request headers here: they carry the token.
        raise SystemExit("Cloudflare said %s for %s %s\n%s"
                         % (e.code, method, path, detail))


def records(tok, zone_id):
    out, page = {}, 1
    while True:
        r = call("GET", "/zones/%s/dns_records?per_page=100&page=%d"
                 % (zone_id, page), tok)
        for rec in r["result"]:
            out.setdefault((rec["type"], rec["name"]), []).append(rec)
        info = r["result_info"]
        if info["page"] * info["per_page"] >= info["total_count"]:
            return out
        page += 1


def wanted(s1, s2):
    return [
        {"type": "CNAME", "name": "selector1._domainkey." + ZONE,
         "content": s1, "proxied": False, "ttl": 1,
         "comment": "Microsoft 365 DKIM. Must stay DNS only, never proxied."},
        {"type": "CNAME", "name": "selector2._domainkey." + ZONE,
         "content": s2, "proxied": False, "ttl": 1,
         "comment": "Microsoft 365 DKIM. Must stay DNS only, never proxied."},
        {"type": "TXT", "name": "_dmarc." + ZONE,
         "content": DMARC, "ttl": 1,
         "comment": "DMARC. Start at p=none, tighten once reports are clean."},
    ]


def same(existing, want):
    if existing["content"].strip('"') != want["content"]:
        return False
    if want["type"] == "CNAME" and existing.get("proxied") is not False:
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="actually write. Without it, nothing is changed.")
    ap.add_argument("--verify", action="store_true",
                    help="read the records back from public DNS and stop")
    ap.add_argument("--selector1",
                    default="selector1-gossans-com._domainkey." + TENANT)
    ap.add_argument("--selector2",
                    default="selector2-gossans-com._domainkey." + TENANT)
    args = ap.parse_args()

    if args.verify:
        return verify()

    tok, source = token()
    print("token read from %s" % source)

    zones = call("GET", "/zones?name=" + ZONE, tok)["result"]
    if not zones:
        raise SystemExit(
            "The token cannot see the %s zone. Check it is scoped to that "
            "zone and carries Zone / DNS / Edit." % ZONE)
    zone_id = zones[0]["id"]
    print("zone %s ok\n" % ZONE)

    have = records(tok, zone_id)
    changes = 0
    for want in wanted(args.selector1, args.selector2):
        key = (want["type"], want["name"])
        current = have.get(key, [])
        short = want["name"].replace("." + ZONE, "")
        if len(current) == 1 and same(current[0], want):
            print("  ok      %-22s already correct" % short)
            continue
        if len(current) > 1:
            print("  SKIP    %-22s %d records share this name. Resolve by "
                  "hand." % (short, len(current)))
            continue
        changes += 1
        verb = "update" if current else "create"
        print("  %-7s %-22s -> %s" % (verb, short, want["content"]))
        if not args.apply:
            continue
        if current:
            call("PUT", "/zones/%s/dns_records/%s" % (zone_id, current[0]["id"]),
                 tok, want)
        else:
            call("POST", "/zones/%s/dns_records" % zone_id, tok, want)
        print("          done")

    print()
    if not changes:
        print("Nothing to do. Everything is already published.")
    elif args.apply:
        print("Written. Now enable DKIM signing for %s in the Microsoft\n"
              "Defender portal, or the selectors sign nothing:\n"
              "  security.microsoft.com -> Policies & rules -> Threat "
              "policies\n  -> Email authentication settings -> DKIM" % ZONE)
        print("\nThen: python tools/dns.py --verify")
    else:
        print("Dry run. Nothing was changed. Re-run with --apply to write.")


def verify():
    """Read the records back from public DNS, not from Cloudflare's API.

    Asking Cloudflare what it stores only proves the write landed. Asking a
    public resolver proves the world can see it, which is the thing that
    actually matters for mail.
    """
    checks = [("selector1._domainkey." + ZONE, "CNAME"),
              ("selector2._domainkey." + ZONE, "CNAME"),
              ("_dmarc." + ZONE, "TXT"),
              (ZONE, "TXT"),
              (ZONE, "MX")]
    bad = 0
    for name, rtype in checks:
        req = urllib.request.Request(
            "https://dns.google/resolve?name=%s&type=%s" % (name, rtype),
            headers={"accept": "application/dns-json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r)
        answers = [a["data"] for a in data.get("Answer", [])]
        if rtype == "TXT" and name == ZONE:
            answers = [a for a in answers if "spf" in a.lower()]
        label = name.replace("." + ZONE, "").replace(ZONE, "@")
        if answers:
            print("  ok      %-24s %-5s %s" % (label, rtype, answers[0]))
        else:
            print("  MISSING %-24s %-5s" % (label, rtype))
            bad += 1
    print()
    print("All five published." if not bad else "%d still missing." % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main() or 0)
