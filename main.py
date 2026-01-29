
# url = "https://ir.youradv.com/stock-information/stock-quote-and-chart/default.aspx"
url = "https://ir.youradv.com/news-events/news-releases/default.aspx"


# ###########################################################################
# from weasyprint import HTML
# HTML(url).write_pdf('output_weasyprint.pdf')


# ###########################################################################
# import asyncio
# from playwright.async_api import async_playwright

# async def url_to_pdf(url, output_path):
#     async with async_playwright() as p:
#         browser = await p.chromium.launch()
#         page = await browser.new_page()
#         await page.goto(url)
#         await page.pdf(path=output_path)
#         await browser.close()

# # Example usage
# asyncio.run(url_to_pdf(url, "output_playwright.pdf"))   


# ###########################################################################
# import pdfkit
# pdfkit.from_url(url, "output_pdfkit.pdf")
# # wkhtmltopdf error


# ###########################################################################
import asyncio
# from crawl4ai import *
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, DefaultMarkdownGenerator, PruningContentFilter
import os
from pathlib import Path

import ipdb
# ipdb.set_trace()


async def main():
    # Define download path
    download_path = os.path.join(Path.home(), ".crawl4ai", "downloads")
    os.makedirs(download_path, exist_ok=True)

    browser_config = BrowserConfig(
        headless=True,
        verbose=True,
        text_mode=True,
        java_script_enabled=True,
        accept_downloads=True,
        downloads_path=download_path
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(),                                       
            # options={
            #     # "ignore_links": True,
            #     "escape_html": False,
            #     # "body_width": 80
            # }
        )

        js_code="""
            var css_selector = 'a.evergreen-news-attachment-PDF[href$=".pdf"]';
            const downloadLinks = document.querySelectorAll(css_selector);
            for (const link of downloadLinks) {
                link.click();
                // Delay between clicks
                await new Promise(r => setTimeout(r, 2000));
            }
        """

        # screenshot=True
        crawler_config = CrawlerRunConfig(
            markdown_generator=markdown_generator,
            exclude_all_images=True,
            excluded_tags=["header", "footer", "nav"],
            # url_matcher="*.pdf",
            pdf=True,
            js_code=js_code,
            wait_for="css:a.evergreen-news-attachment-PDF:nth-of-type(1)"  # Wait for at least 5 news items
            # .evergreen-news-content-list:nth-child(5)
            # .evergreen-news-item:nth-of-type(5)
        )

        result = await crawler.arun(
            url=url,
            config=crawler_config
        )

        if result.success:
            # print("Markdown:\n", result.markdown[:100])  # Just a snippet
            # result.markdown.markdown_with_citations

            found_int_urls = result.links.get("internal", []) # r.youradv.com
            found_ext_urls = result.links.get("external", []) # s21.q4cdn.com
            print(f"Found {len(found_int_urls)} internal links and {len(found_ext_urls)} external links.")
            print("PDF Links Found:")
            for found_url in (found_int_urls + found_ext_urls):
                if found_url.get("href").lower().endswith(".pdf"):
                    print(found_url.get("href"))

            if result.downloaded_files:
                print("PDF files Downloaded:")
                for file in result.downloaded_files:
                    print(f"- {file}")
            else:
                print("No files downloaded.")

            # Save to file
            with open("output_crawl4ai.md", "w", encoding="utf-8") as f:
                f.write(result.markdown)
        else:
            print("Crawl failed:", result.error_message)


# def main():
#     print("Hello from poc-weasyprint!")


if __name__ == "__main__":
    # main()
    asyncio.run(main())
