
---

# 📘 Salesforce AppExchange Scraper

This project is a **web scraper** built with [Playwright](https://playwright.dev/python/) and [Pandas](https://pandas.pydata.org/).
It extracts **App names** and **links** from Salesforce AppExchange category pages and saves the results into an Excel file.

---

## 🚀 Features

* Opens any **Salesforce AppExchange category URL**.
* Automatically clicks the **"Show More"** button until all apps are loaded.
* Extracts:

  * ✅ App Name
  * ✅ App Link
* Removes duplicate entries.
* Generates a **Unique ID** for each app.
* Saves results to **Excel** (`.xlsx`).

---

## 📂 Project Structure

```
.
├── scrape_app_links.py   # Main Python script
├── README.md             # Documentation (this file)
└── app_links.xlsx        # Output file (generated after running)
```

---

## 🛠️ Requirements

* Python 3.8+
* Playwright
* Pandas
* Asyncio (built-in with Python)

### Install dependencies:

```bash
pip install playwright pandas
```

Initialize Playwright browsers:

```bash
playwright install
```

---

## ▶️ Usage

### Run the script:

```bash
python scrape_app_links.py
```

The script will:

1. Open the browser (non-headless, so you can watch).
2. Load the given AppExchange category page.
3. Keep clicking **"Show More"** until all apps are visible.
4. Extract app names and links.
5. Save them into **`app_links.xlsx`**.

---

## 📑 Script Explanation

### 1. Imports

```python
from playwright.async_api import async_playwright
import pandas as pd
import asyncio
```

* `async_playwright`: Automates browser actions asynchronously.
* `pandas`: Organizes and saves scraped data.
* `asyncio`: Runs async functions.

---

### 2. Scraping Function

```python
async def scrape_app_links(category_url: str, output_file="app_links.xlsx"):
```

* Takes a **category URL** and an optional **output Excel filename**.

---

### 3. Launch Browser

```python
async with async_playwright() as pw:
    browser = await pw.chromium.launch(headless=False)
    page = await browser.new_page()
    await page.goto(category_url, timeout=90000)
    await page.wait_for_load_state("networkidle")
```

* Starts a Chromium browser.
* Opens the given page.
* Waits until network requests are done.

---

### 4. Load All Apps

```python
while True:
    btn = await page.query_selector("wds-button[data-testid='view-more-button'] >> button")
    if not btn: break
    await btn.scroll_into_view_if_needed()
    await btn.click()
    await asyncio.sleep(3)
```

* Finds the **"Show More"** button.
* Keeps clicking it until it disappears.
* Waits `3 seconds` after each click for new apps to load.

---

### 5. Extract Apps

```python
apps = await page.query_selector_all(
    "wds-listing-card >> wds-analytics-instrument >> ax-card >> section >> div.title-creds"
)
```

* Selects **all app cards**.

For each app:

```python
link_el = await card.query_selector("a.card-target")
name_el = await card.query_selector("p[type-style='body-3']")
link = await link_el.get_attribute("href") if link_el else None
name = (await name_el.inner_text()).strip() if name_el else "Unknown"
```

* Extracts **App Name** and **Link**.

---

### 6. Store Data

```python
results.append({
    "App Name": name,
    "Link": "https://appexchange.salesforce.com" + link,
})
```

* Saves results in a Python list.

---

### 7. Save to Excel

```python
df = pd.DataFrame(results).drop_duplicates(subset=["Link"]).reset_index(drop=True)
df.insert(0, "Unique ID", df.index + 1)
df.to_excel(output_file, index=False)
```

* Converts results to a DataFrame.
* Removes duplicates.
* Adds a `"Unique ID"` column.
* Saves everything to Excel.

---

### 8. Main Entry Point

```python
if __name__ == "__main__":
    asyncio.run(main())
```

* Runs the scraper when executed directly.

---

## 📊 Output Example

Excel file (`app_links.xlsx`) will contain:

| Unique ID | App Name          | Link                                                                                                                                         |
| --------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 1         | Sales Forecasting | [https://appexchange.salesforce.com/appxListingDetail?listingId=12345](https://appexchange.salesforce.com/appxListingDetail?listingId=12345) |
| 2         | Revenue Planner   | [https://appexchange.salesforce.com/appxListingDetail?listingId=67890](https://appexchange.salesforce.com/appxListingDetail?listingId=67890) |

---

## 📌 Notes

* `headless=False` is set so you can **watch the browser**. Change to `True` for faster invisible scraping.
* Salesforce may update their site → selectors may need updating in the future.
* The script scrapes only **publicly visible data**.

---

## 🔗 Next Steps

* Add multiple category URLs.
* Export also to CSV or JSON.
* Generate **hash-based unique IDs** (instead of numbers).

---

