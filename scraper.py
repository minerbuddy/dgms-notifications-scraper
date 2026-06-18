"""
DGMS Connectivity Debug Script
================================
Run this in GitHub Actions / Render / wherever your scraper runs.
It does NOT scrape notifications — it only diagnoses WHY the connection fails.

It runs 4 tests and prints a clear verdict at the end:
  1. Plain requests.get() to DGMS (what your current scraper does)
  2. requests.get() to a known-good control site (httpbin) — proves network works at all
  3. DNS resolution check for dgms.gov.in
  4. Playwright headless browser load of DGMS (real browser fingerprint)

Install deps before running:
    pip install requests playwright --break-system-packages
    playwright install chromium --with-deps

Run:
    python debug_dgms.py
"""

import socket
import time
import json

RESULTS = {}

DGMS_URL = "https://www.dgms.gov.in/UserView/index?mid=1603"
CONTROL_URL = "https://httpbin.org/get"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
}


def log(section, msg):
    print(f"\n[{section}] {msg}")


def test_dns():
    log("DNS", "Resolving www.dgms.gov.in ...")
    try:
        ip = socket.gethostbyname("www.dgms.gov.in")
        log("DNS", f"Resolved to {ip}")
        RESULTS["dns"] = {"ok": True, "ip": ip}
    except Exception as e:
        log("DNS", f"FAILED: {e}")
        RESULTS["dns"] = {"ok": False, "error": str(e)}


def test_control_site():
    log("CONTROL", f"GET {CONTROL_URL} (sanity check that outbound HTTPS works at all)")
    import requests
    try:
        start = time.time()
        r = requests.get(CONTROL_URL, headers=HEADERS, timeout=15)
        elapsed = time.time() - start
        log("CONTROL", f"Status={r.status_code} Time={elapsed:.2f}s")
        RESULTS["control"] = {"ok": True, "status": r.status_code, "time": elapsed}
    except Exception as e:
        log("CONTROL", f"FAILED: {e}")
        RESULTS["control"] = {"ok": False, "error": str(e)}


def test_plain_requests():
    log("REQUESTS", f"GET {DGMS_URL} with browser headers, timeout=(10,30)")
    import requests
    try:
        start = time.time()
        r = requests.get(DGMS_URL, headers=HEADERS, verify=False, timeout=(10, 30))
        elapsed = time.time() - start
        log("REQUESTS", f"Status={r.status_code} Time={elapsed:.2f}s Bytes={len(r.content)}")
        log("REQUESTS", f"First 200 chars: {r.text[:200]!r}")
        RESULTS["plain_requests"] = {"ok": True, "status": r.status_code, "time": elapsed}
    except Exception as e:
        log("REQUESTS", f"FAILED: {type(e).__name__}: {e}")
        RESULTS["plain_requests"] = {"ok": False, "error": f"{type(e).__name__}: {e}"}


def test_playwright():
    log("PLAYWRIGHT", f"Launching headless Chromium -> {DGMS_URL}")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log("PLAYWRIGHT", "SKIPPED - playwright not installed (pip install playwright && playwright install chromium)")
        RESULTS["playwright"] = {"ok": False, "error": "not installed"}
        return

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=HEADERS["User-Agent"])
            start = time.time()
            try:
                response = page.goto(DGMS_URL, timeout=30000, wait_until="domcontentloaded")
                elapsed = time.time() - start
                status = response.status if response else None
                content_len = len(page.content())
                log("PLAYWRIGHT", f"Status={status} Time={elapsed:.2f}s ContentLen={content_len}")
                RESULTS["playwright"] = {"ok": True, "status": status, "time": elapsed}
            except Exception as e:
                elapsed = time.time() - start
                log("PLAYWRIGHT", f"FAILED after {elapsed:.2f}s: {type(e).__name__}: {e}")
                RESULTS["playwright"] = {"ok": False, "error": f"{type(e).__name__}: {e}"}
            finally:
                browser.close()
    except Exception as e:
        log("PLAYWRIGHT", f"Setup FAILED: {type(e).__name__}: {e}")
        RESULTS["playwright"] = {"ok": False, "error": f"{type(e).__name__}: {e}"}


def verdict():
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    dns_ok = RESULTS.get("dns", {}).get("ok")
    control_ok = RESULTS.get("control", {}).get("ok")
    plain_ok = RESULTS.get("plain_requests", {}).get("ok")
    pw_ok = RESULTS.get("playwright", {}).get("ok")

    if not control_ok:
        print("-> Outbound internet/HTTPS itself is broken in this environment.")
        print("   This is NOT a DGMS-specific issue. Check runner network config.")
    elif not dns_ok:
        print("-> DNS resolution for dgms.gov.in is failing from this environment.")
        print("   Possible DNS-level blocking or runner DNS misconfiguration.")
    elif plain_ok and pw_ok:
        print("-> Both plain requests AND Playwright succeeded.")
        print("   The earlier failures were likely transient (site instability) or")
        print("   the headers/retry fix already solved it. Re-run a few times to confirm.")
    elif (not plain_ok) and pw_ok:
        print("-> Plain requests FAILS but Playwright SUCCEEDS.")
        print("   Strong signal: bot/fingerprint-based filtering, not a full IP ban.")
        print("   DGMS is likely allowing real-browser TLS/JS fingerprints and")
        print("   rejecting/dropping simple HTTP client connections.")
        print("   -> Recommended fix: move scraping to Playwright.")
    elif (not plain_ok) and (not pw_ok):
        print("-> BOTH plain requests AND Playwright FAIL from this environment,")
        print("   while the control site (httpbin) works fine.")
        print("   Strong signal: this specific IP/range is blocked at the network")
        print("   level for dgms.gov.in (TCP handshake never completes for ANY client).")
        print("   -> Recommended fix: run from a non-datacenter IP (residential proxy,")
        print("      mobile/ISP connection, or a self-hosted runner on a home/VPS")
        print("      machine with a residential-ish IP). Playwright alone will NOT help.")
    else:
        print("-> Inconclusive — re-run and check raw results below.")

    print("\nRaw results:")
    print(json.dumps(RESULTS, indent=2, default=str))


if __name__ == "__main__":
    test_dns()
    test_control_site()
    test_plain_requests()
    test_playwright()
    verdict()
