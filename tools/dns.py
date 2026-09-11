#!/usr/bin/env python3
"""Publish the mail authentication records for gossans.com at Cloudflare.

The domain sends through Microsoft 365 and already publishes SPF and MX. It
published neither DKIM nor DMARC, which meant a forger could put gossans.com
in the From line of a message and most receivers had no instruction on what to
do about it. That is the gap this closes.

    set CLOUDFLARE_API_TOKEN, or write it to the token file named below
    python tools/dns.py            # show what would change, change nothing
    python tools/dns.py --apply    # write it
    python tools/dns.py --verify   # check the zone, and how far it has spread

The token is never printed, never logged, and never written by this script.
It is read from the environment first and from a file outside every
repository second, so it cannot be committed by accident.

Scope the token to exactly one permission, Zone / DNS / Edit, and to the
gossans.com zone alone. A token that can only edit one zone's DNS cannot
touch billing, Pages, Workers, or any other domain.

DKIM is two halves and this script is only the first. Publishing the CNAMEs
does nothing until DKIM signing is switched on for the domain in the Microsoft
Defender portal, and Microsoft refuses to switch it on until the CNAMEs
resolve. So: run this, then enable it there.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ZONE = "gossans.com"

#: The tenant short name, not the full onmicrosoft.com domain. Microsoft moved
#: DKIM key hosting from <tenant>.onmicrosoft.com to <tenant>.a-v1.dkim.mail
#: .microsoft, and a tenant created now gets only the latter. The older form is
#: still what most documentation shows, and is what this script tried first;
#: Exchange rejected it and named these instead. If a future tenant differs
#: again, the portal error states the correct targets verbatim: pass them with
#: --selector1 and --selector2 rather than editing this.
TENANT = "Gossans"
DKIM_HOST = "%s-gossans-com._domainkey." + TENANT + ".a-v1.dkim.mail.microsoft"

#: Deliberately outside every repository, so no .gitignore mistake can leak it.
TOKEN_FILE = Path.home() / ".gossans" / "cloudflare-token"

API = "https://api.cloudflare.com/client/v4"

# p=none is the honest starting policy: it asks receivers to report what they
# see and to change nothing. Tighten to quarantine once a fortnight of reports
# shows only Microsoft signing this mail, then to reject, and move SPF from
# ~all to -all at the same time.
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


def zone_records(tok):
    zones = call("GET", "/zones?name=" + ZONE, tok)["result"]
    if not zones:
        raise SystemExit(
            "The token cannot see the %s zone. Check it is scoped to that "
            "zone and carries Zone / DNS / Edit." % ZONE)
    zone_id = zones[0]["id"]

    out, page = {}, 1
    while True:
        r = call("GET", "/zones/%s/dns_records?per_page=100&page=%d"
                 % (zone_id, page), tok)
        for rec in r["result"]:
            out.setdefault((rec["type"], rec["name"]), []).append(rec)
        info = r["result_info"]
        if info["page"] * info["per_page"] >= info["total_count"]:
            return zone_id, out
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
    a = existing["content"].strip('"')
    b = want["content"]
    # Hostnames are case-insensitive and Cloudflare stores them lowercased, so
    # comparing them literally reports a difference on every run and the script
    # never settles at "already correct". A TXT value is not a hostname, so it
    # is compared as written.
    if want["type"] == "CNAME":
        a, b = a.lower().rstrip("."), b.lower().rstrip(".")
    if a != b:
        return False
    if want["type"] == "CNAME" and existing.get("proxied") is not False:
        return False
    return True


def resolve(name, rtype):
    """Ask a public resolver. Returns [] on any failure, deliberately.

    This answers "can the world see it yet", which is a different question
    from "is it configured", and it is much the flakier of the two: public
    resolvers cache negative answers, disagree across their own anycast fleet,
    and rate-limit. So a miss here is reported as lag, never as a fault.
    """
    try:
        req = urllib.request.Request(
            "https://dns.google/resolve?name=%s&type=%s" % (name, rtype),
            headers={"accept": "application/dns-json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.load(r)
        return [a["data"].strip('"') for a in data.get("Answer", [])]
    except Exception:
        return []


def apply(args):
    tok, source = token()
    print("token read from %s" % source)
    zone_id, have = zone_records(tok)
    print("zone %s ok\n" % ZONE)

    changes = 0
    for want in wanted(args.selector1, args.selector2):
        current = have.get((want["type"], want["name"]), [])
        short = want["name"].replace("." + ZONE, "")
        if len(current) == 1 and same(current[0], want):
            print("  ok      %-22s already correct" % short)
            continue
        if len(current) > 1:
            print("  SKIP    %-22s %d records share this name. Resolve by "
                  "hand." % (short, len(current)))
            continue
        changes += 1
        print("  %-7s %-22s -> %s"
              % ("update" if current else "create", short, want["content"]))
        if not args.apply:
            continue
        if current:
            call("PUT", "/zones/%s/dns_records/%s"
                 % (zone_id, current[0]["id"]), tok, want)
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
    return 0


def verify(args):
    """Check the zone is right, then report separately how far it has spread.

    An earlier version asked only a public resolver, and so called a stale
    cache a missing record. That is the worst way to be wrong: it reports a
    fault where none exists and sends you looking for it. The authoritative
    question is now answered from the zone itself, and propagation is reported
    beside it without ever failing the command.
    """
    tok, _ = token()
    _, have = zone_records(tok)

    expect = wanted(args.selector1, args.selector2)
    loose = [{"type": "TXT", "name": ZONE, "content": "v=spf1"},
             {"type": "MX", "name": ZONE, "content": "outlook.com"}]

    print("In the zone:")
    bad = 0
    for want in expect + loose:
        got = have.get((want["type"], want["name"]), [])
        label = "@" if want["name"] == ZONE else want["name"].replace("." + ZONE, "")
        if want in loose:
            ok = any(want["content"] in r["content"] for r in got)
        else:
            ok = len(got) == 1 and same(got[0], want)
        print("  %-7s %-22s %-5s %s"
              % ("ok" if ok else "WRONG", label, want["type"],
                 got[0]["content"][:56] if got else "absent"))
        bad += 0 if ok else 1

    print("\nMicrosoft's signing keys:")
    signing = 0
    for sel in ("selector1", "selector2"):
        live = any("v=DKIM1" in k for k in resolve(DKIM_HOST % sel, "TXT"))
        signing += 1 if live else 0
        print("  %-7s %-22s %s" % ("ok" if live else "-", sel,
                                   "key published" if live else "not generated yet"))

    print("\nPropagation, which lags by up to the old record's TTL:")
    for sel in ("selector1", "selector2"):
        seen = resolve("%s._domainkey.%s" % (sel, ZONE), "CNAME")
        fresh = any("dkim.mail.microsoft" in x for x in seen)
        print("  %-7s %-22s %s" % ("seen" if fresh else "lag", sel,
                                   seen[0][:56] if seen else "not visible yet"))
    seen = resolve("_dmarc." + ZONE, "TXT")
    print("  %-7s %-22s %s" % ("seen" if seen else "lag", "_dmarc",
                               seen[0][:56] if seen else "not visible yet"))

    print()
    if bad:
        print("%d record(s) wrong in the zone. Run without --verify to fix."
              % bad)
    elif signing < 2:
        print("The zone is correct, but DKIM is not signing yet. Switch it on\n"
              "for %s at security.microsoft.com -> Policies & rules ->\n"
              "Threat policies -> Email authentication settings -> DKIM."
              % ZONE)
    else:
        # DNS proves the keys exist. It cannot prove the signing toggle is on,
        # and saying otherwise would be exactly the false all-clear this
        # command was rewritten to stop giving.
        print("Zone correct, and Microsoft has generated both keys.")
        print("DNS cannot show whether the signing toggle is on. Confirm that")
        print("in the Defender portal, then send a message to a Gmail address")
        print("and check that Show original reports DKIM: PASS.")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="actually write. Without it, nothing is changed.")
    ap.add_argument("--verify", action="store_true",
                    help="check the zone and report propagation")
    ap.add_argument("--selector1", default=DKIM_HOST % "selector1")
    ap.add_argument("--selector2", default=DKIM_HOST % "selector2")
    args = ap.parse_args()
    return verify(args) if args.verify else apply(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
