import time
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
TARGET_URL = "https://sites.google.com/iit.ac.lk/launchpilot-ai/home"
DOMAIN_FILTER = "sites.google.com/iit.ac.lk/launchpilot-ai"

def get_stealth_driver():
    chrome_options = Options()
    
    # --- FIX: USE YOUR REAL CHROME PROFILE ---
    # This allows the bot to stay logged in as YOU instead of a 'Guest'
    user_home = os.path.expanduser("~")
    profile_path = os.path.join(user_home, "AppData", "Local", "Google", "Chrome", "User Data")
    
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument("--profile-directory=Profile 1") # Change to 'Profile 1' if you use a secondary profile
    
    # Stealth: Hide automation flags
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Stealth: Remove the 'navigator.webdriver' flag for Analytics
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    
    return driver

def scroll_and_click(driver):
    print("  📜 Scrolling and looking for buttons...")
    
    # Human-like Scroll
    total_height = driver.execute_script("return document.body.scrollHeight")
    current_pos = 0
    while current_pos < total_height:
        step = random.randint(400, 700)
        current_pos += step
        driver.execute_script(f"window.scrollTo(0, {current_pos});")
        time.sleep(random.uniform(0.5, 1.0))
    
    # Find clickable elements
    buttons = driver.find_elements(By.CSS_SELECTOR, "button, [role='button'], input[type='button']")
    
    # Ignore list to prevent 'Report Abuse' or 'Logout' popups
    ignore_list = ["report", "abuse", "logout", "sign out", "feedback", "google", "terms", "privacy"]
    
    for btn in buttons:
        try:
            btn_text = btn.text.lower().strip()
            if any(word in btn_text for word in ignore_list) or btn_text == "":
                continue
                
            if btn.is_displayed() and btn.is_enabled():
                print(f"  🔘 Clicking: {btn_text[:25]}")
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(random.uniform(2, 4)) # Wait for action to load
        except:
            continue

def run_automation():
    # IMPORTANT: Close all other Chrome windows before running!
    driver = get_stealth_driver()
    visited = set()
    to_visit = [TARGET_URL]

    print("🚀 Bot started using your Chrome Profile...")

    try:
        while to_visit:
            current = to_visit.pop(0)
            if current in visited:
                continue
            
            print(f"\n📄 Visiting: {current}")
            driver.get(current)
            visited.add(current)
            
            # Extra time on the first page in case you need to click 'Sign In'
            if len(visited) == 1:
                print("⏳ Checking if login is required...")
                time.sleep(5) 

            scroll_and_click(driver)

            # Extract internal links
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and DOMAIN_FILTER in href:
                    clean_url = href.split('#')[0].rstrip('/')
                    if clean_url not in visited and clean_url not in to_visit:
                        to_visit.append(clean_url)

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 TIP: Make sure ALL Chrome windows are closed before running this script.")
    finally:
        print(f"\n✨ Done. Visited {len(visited)} pages.")
        driver.quit()

if __name__ == "__main__":
    run_automation()