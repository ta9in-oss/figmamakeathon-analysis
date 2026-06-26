#!/usr/bin/env python3
"""
Capture the exact GraphQL request for SocialPosts pagination,
then replay it with httpx to get all pages.
"""

import json
import time
from playwright.sync_api import sync_playwright


def main():
    captured_requests = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            )
        )
        page = ctx.new_page()

        def handle_request(request):
            if "SocialPosts_socialPostsPaginationQuery" in request.url:
                try:
                    post_data = request.post_data
                    headers = dict(request.headers)
                    captured_requests.append({
                        "url": request.url,
                        "method": request.method,
                        "post_data": post_data,
                        "headers": {
                            k: v for k, v in headers.items()
                            if k.lower() in ("content-type", "x-relay-network-sse", "baggage",
                                             "accept", "x-forwarded-proto", "sec-fetch-dest")
                        }
                    })
                except Exception as e:
                    print(f"Error capturing request: {e}")

        page.on("request", handle_request)
        page.goto("https://contra.com/community/topic/figmamakeathon", wait_until="networkidle", timeout=60_000)
        time.sleep(3)
        # Do a couple scrolls to get pagination requests
        for _ in range(5):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)

        browser.close()

    print(f"Captured {len(captured_requests)} requests")
    for i, req in enumerate(captured_requests[:3]):
        print(f"\n--- Request {i+1} ---")
        print("URL:", req["url"])
        print("Method:", req["method"])
        if req["post_data"]:
            try:
                pd = json.loads(req["post_data"])
                print("Variables:", json.dumps(pd.get("variables", {}), indent=2))
                print("Query (first 200):", pd.get("query", "")[:200])
            except Exception:
                print("Post data (raw):", req["post_data"][:500])

    # Save full capture for analysis
    with open("/tmp/captured_requests.json", "w") as f:
        json.dump(captured_requests, f, indent=2)
    print("\nSaved to /tmp/captured_requests.json")


if __name__ == "__main__":
    main()
