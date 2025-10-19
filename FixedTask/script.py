import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def main():
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSch8ezgNkQNILgEruelIzEELdW-hmOxJhi1kgSjVOm74GKk0A/viewform?usp=header"
    name = input("Enter name: ")
    school = input("Enter school: ")
    try:
        valid_year_inputs = ["1st", "2nd", "3rd", "4th", "5+"]
        year = input("Enter year (Enter exactly one of these: 1st, 2nd, 3rd, 4th, 5+): ")
        if year not in valid_year_inputs:
            raise ValueError
    except ValueError:
        print("Invalid year. Stopping session...")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # GO TO FORM PAGE
            print("Navigating to form page...")
            await page.goto(form_url, timeout=30000)

            # Create a locator for the form to ensure form is loaded first
            form_locator = page.locator("form")
            await form_locator.wait_for(state="visible", timeout=30000)

            # ENTER NAME INTO FORM
            print("Filling out name section...")
            name_input = page.locator("input[type=\"text\"]").nth(0)
            await name_input.wait_for(timeout=10000)
            await name_input.fill(name)

            # ENTER SCHOOL NAME INTO FORM
            print("Filling out school section...")
            school_input = page.locator("input[type=\"text\"]").nth(1)
            await school_input.wait_for(state="visible", timeout=10000)
            await school_input.fill(school)
            
            # SELECT WHAT YEAR YOU ARE
            print("Selecting year...")
            year_input = page.locator(f"div[role=\"radio\"][data-value=\"{year}\"]").first
            await year_input.wait_for(state="visible", timeout=10000)
            await year_input.click()
            
            # === Submit form ===
            print("Submitting form...")
            submit_button = page.locator("div[role=\"button\"]:has-text(\"Submit\")")
            await submit_button.wait_for(state="visible", timeout=10000)
            await submit_button.click()

            await browser.close()
            print("DONE!!!")

    except PlaywrightTimeoutError:
        print("Timeout waiting for a page element. The site may be slow or unresponsive.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())