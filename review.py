import pandas as pd
import asyncio
from playwright.async_api import async_playwright

async def scrape_reviews(input_file="app_links.xlsx", output_file="Extracted_Reviews.xlsx"):
    apps_df = pd.read_excel(input_file)
    all_reviews = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()

        for _, row in apps_df.iterrows():
            app_name = row["App Name"]
            app_url = row["Link"]
            unique_id = row["Unique ID"]

            # ✅ Force Reviews tab
            if "&tab=" in app_url:
                reviews_url = app_url.split("&tab=")[0] + "&tab=r"
            else:
                reviews_url = app_url + "&tab=r"

            print(f"🔍 Scraping reviews for {app_name} ({reviews_url})")

            try:
                await page.goto(reviews_url, timeout=90000)
                await page.wait_for_load_state("networkidle")

                # ✅ Load all reviews by tracking count
                prev_count = -1
                while True:
                    reviews = await page.query_selector_all('div.cReviews__review')
                    curr_count = len(reviews)

                    if curr_count == prev_count:  # stop if no new reviews
                        break
                    prev_count = curr_count

                    try:
                        show_more = await page.query_selector('button:has-text("Show More")')
                        if show_more and await show_more.is_visible():
                            await show_more.click()
                            await page.wait_for_timeout(2500)
                        else:
                            break
                    except:
                        break

                # ✅ Extract reviews
                reviews = await page.query_selector_all('div.cReviews__review')

                for review in reviews:
                    try:
                        reviewer_name = await review.query_selector_eval(
                            '.cReviews__reviewUserName', 'el => el.innerText'
                        ) if await review.query_selector('.cReviews__reviewUserName') else ""

                        review_date = await review.query_selector_eval(
                            '.cReviews__reviewDate', 'el => el.innerText'
                        ) if await review.query_selector('.cReviews__reviewDate') else ""

                        review_text = await review.query_selector_eval(
                            '.cReviews__reviewBody', 'el => el.innerText'
                        ) if await review.query_selector('.cReviews__reviewBody') else ""

                        likes = await review.query_selector_eval(
                            '.cReviews__likeCount', 'el => el.innerText'
                        ) if await review.query_selector('.cReviews__likeCount') else "0"

                        # Flags
                        mvp = 1 if await review.query_selector('.cReviews__mvp') else 0
                        ranger = 1 if await review.query_selector('.cReviews__ranger') else 0
                        top_reviewer = 1 if await review.query_selector('.cReviews__topReviewer') else 0

                        # Valence
                        valence = "Neutral"
                        if await review.query_selector('.cIcon--positive'):
                            valence = "Positive"
                        elif await review.query_selector('.cIcon--negative'):
                            valence = "Negative"

                        all_reviews.append({
                            "Unique ID": unique_id,
                            "Review Date": review_date,
                            "Reviewer Name": reviewer_name,
                            "Likes": likes,
                            "Review Valence": valence,
                            "MVP Count": mvp,
                            "Ranger Count": ranger,
                            "Top Reviewer Count": top_reviewer,
                            "Review Text": review_text
                        })
                    except Exception as e:
                        print(f"⚠️ Error extracting a review: {e}")

            except Exception as e:
                print(f"❌ Failed to scrape {app_name}: {e}")

        await browser.close()

    # ✅ Save results
    reviews_df = pd.DataFrame(all_reviews)
    reviews_df.to_excel(output_file, index=False)
    print(f"✅ All reviews saved to {output_file}")


if __name__ == "__main__":
    asyncio.run(scrape_reviews())
