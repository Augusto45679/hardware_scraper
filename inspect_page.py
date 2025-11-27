from playwright.sync_api import sync_playwright
import sys

def run():
    print("Starting Playwright...", flush=True)
    with sync_playwright() as p:
        print("Launching browser...", flush=True)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating...", flush=True)
        page.goto("https://compragamer.com/productos?criterio=fuente+de+poder&page=1")
        print("Waiting for selector...", flush=True)
        try:
            page.wait_for_selector("cgw-product-card", timeout=10000)
        except Exception as e:
            print(f"Timeout waiting for selector: {e}", flush=True)
            browser.close()
            return

        # Get the first product card
        card = page.query_selector("cgw-product-card")
        if card:
            print("Card HTML found.", flush=True)
            
            # Try to find the image
            img = card.query_selector("img")
            if img:
                print("\nImage found:", flush=True)
                print(f"Src: {img.get_attribute('src')}", flush=True)
                print(f"Class: {img.get_attribute('class')}", flush=True)
            else:
                print("\nNo img tag found inside card", flush=True)
                
                # Check for cgw-item-image
                item_image = card.query_selector("cgw-item-image")
                if item_image:
                    print("\ncgw-item-image found:", flush=True)
                    print(item_image.inner_html(), flush=True)
        else:
            print("No product card found", flush=True)
            
        browser.close()

if __name__ == "__main__":
    run()
