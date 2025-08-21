from playwright.async_api import async_playwright
import pandas as pd
import asyncio

async def scrape_app_links(category_url: str, output_file="app_links.xlsx"):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()
        print(f"🔍 Opening {category_url}")
        await page.goto(category_url, timeout=90000)
        await page.wait_for_load_state("networkidle")

        # Keep clicking "Show More"
        while True:
            try:
                btn = await page.query_selector(
                    "wds-button[data-testid='view-more-button'] >> button"
                )
                if not btn:
                    print("No more 'Show More' button found.")
                    break
                await btn.scroll_into_view_if_needed()
                await btn.click()
                print("Clicked 'Show More'")
                await asyncio.sleep(3)
            except Exception as e:
                print("Error clicking Show More:", e)
                break

        #  Extract app links & names
        apps = await page.query_selector_all(
            "wds-listing-card >> wds-analytics-instrument >> ax-card >> section >> div.title-creds"
        )

        results = []
        for card in apps:
            try:
                link_el = await card.query_selector("a.card-target")
                name_el = await card.query_selector("p[type-style='body-3']")
                
                link = await link_el.get_attribute("href") if link_el else None
                name = (await name_el.inner_text()).strip() if name_el else "Unknown"
                
                if link:
                    results.append({
                        "App Name": name,
                        "Link": "https://appexchange.salesforce.com" + link,
                        
                    })
            except Exception as e:
                print("Error extracting app:", e)

        await browser.close()

        # Deduplicate by Link
        df = pd.DataFrame(results).drop_duplicates(subset=["Link"]).reset_index(drop=True)
        df.insert(0, "Unique ID", df.index + 1)

        # Save to Excel
        df.to_excel(output_file, index=False)
        print(f"Scraped {len(df)} unique apps and saved to {output_file}")


async def main():
    url = "https://appexchange.salesforce.com/explore/business-needs?category=forecasting"
    await scrape_app_links(url, "app_links.xlsx")


if __name__ == "__main__":
    asyncio.run(main())
