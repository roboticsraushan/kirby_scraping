from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time
import sys
from config import get_config, list_configs

def main():
    """Main function to run the Kirby scraper with configurable parameters"""
    
    # Check if configuration name is provided as command line argument
    if len(sys.argv) > 1:
        config_name = sys.argv[1]
    else:
        # Default to major_cities if no argument provided
        config_name = "major_cities"
        print("No configuration specified. Using 'major_cities' as default.")
        print("Available configurations: major_cities, all_states, robotics_hubs, high_population, custom")
        print("Usage: python3 scrape_kirby.py [config_name]")
        print()
    
    # Get configuration
    config = get_config(config_name)
    print(f"Using configuration: {config['description']}")
    print(f"Locations: {len(config['locations'])}")
    print(f"Search Radius: {config['search_radius']} miles")
    print(f"Max Results: {config['max_results']}")
    print()
    
    # Initialize browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)  # Wait up to 20 seconds

    url = "https://www.kirby.com/kirby-owner-support/find-a-kirby-service-center/"

    # Use a set to deduplicate by store id
    unique_stores = dict()

    total_searches = len(config['locations'])
    current_search = 0

    for location in config['locations']:
        current_search += 1
        print(f"Progress: {current_search}/{total_searches} - Searching for: {location}")
        driver.get(url)
        time.sleep(3)
        
        # Dismiss cookie consent popup if present (try multiple ways)
        popup_closed = False
        try:
            # Try by ID
            accept_btn = driver.find_element(By.ID, "hs-eu-confirmation-button")
            accept_btn.click()
            time.sleep(1)
            popup_closed = True
        except Exception:
            pass
        if not popup_closed:
            try:
                # Try by class name
                accept_btn = driver.find_element(By.CLASS_NAME, "hs-eu-confirmation-button")
                accept_btn.click()
                time.sleep(1)
                popup_closed = True
            except Exception:
                pass
        if not popup_closed:
            try:
                # Try by button text
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if "accept" in btn.text.lower() or "agree" in btn.text.lower():
                        btn.click()
                        time.sleep(1)
                        popup_closed = True
                        break
            except Exception:
                pass
        if not popup_closed:
            # As a last resort, remove overlays with JS
            driver.execute_script('''
                var overlays = document.querySelectorAll('[id*="cookie"], [class*="cookie"], [id*="consent"], [class*="consent"]');
                overlays.forEach(function(el) { el.remove(); });
            ''')
            time.sleep(1)
        
        # Set search radius
        try:
            radius_dropdown = driver.find_element(By.ID, "wpsl-radius-dropdown")
            driver.execute_script(f"arguments[0].value = '{config['search_radius']}';", radius_dropdown)
            # Trigger change event
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", radius_dropdown)
            time.sleep(1)
        except Exception as e:
            print(f"Warning: Could not set search radius: {e}")
        
        # Set max results
        try:
            results_dropdown = driver.find_element(By.ID, "wpsl-results-dropdown")
            driver.execute_script(f"arguments[0].value = '{config['max_results']}';", results_dropdown)
            # Trigger change event
            driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", results_dropdown)
            time.sleep(1)
        except Exception as e:
            print(f"Warning: Could not set max results: {e}")
        
        # Enter location
        try:
            search_input = wait.until(EC.presence_of_element_located((By.ID, "wpsl-search-input")))
            search_input.clear()
            search_input.send_keys(location)
            
            # Click search
            search_btn = wait.until(EC.element_to_be_clickable((By.ID, "wpsl-search-btn")))
            try:
                search_btn.click()
            except Exception as e:
                # Try JavaScript click as fallback
                driver.execute_script("arguments[0].click();", search_btn)
            
            # Wait for dynamic content to load
            print(f"Waiting for results to load for {location}...")
            time.sleep(10)  # Initial wait
            
            # Check if store data has loaded
            max_attempts = 5
            for attempt in range(max_attempts):
                soup = BeautifulSoup(driver.page_source, "html.parser")
                stores = soup.find_all("li", attrs={"data-store-id": True})
                
                if stores:
                    print(f"Found {len(stores)} stores for {location}")
                    break
                else:
                    print(f"Attempt {attempt + 1}: No stores found, waiting...")
                    time.sleep(5)
                    # Try clicking search again if no results
                    if attempt < max_attempts - 1:
                        try:
                            search_btn = driver.find_element(By.ID, "wpsl-search-btn")
                            driver.execute_script("arguments[0].click();", search_btn)
                        except:
                            pass
            
            # Parse results
            soup = BeautifulSoup(driver.page_source, "html.parser")
            stores = soup.find_all("li", attrs={"data-store-id": True})
            
            for store in stores:
                store_id = store.get("data-store-id")
                if store_id in unique_stores:
                    continue
                name = store.find("strong").get_text(strip=True) if store.find("strong") else ""
                street = store.find("span", class_="wpsl-street").get_text(strip=True) if store.find("span", class_="wpsl-street") else ""
                city_state_zip = ""
                street_span = store.find("span", class_="wpsl-street")
                if street_span:
                    next_span = street_span.find_next_sibling("span")
                    if next_span:
                        city_state_zip = next_span.get_text(strip=True)
                country = store.find("span", class_="wpsl-country").get_text(strip=True) if store.find("span", class_="wpsl-country") else ""
                contact = store.find("p", class_="wpsl-contact-details")
                phone = ""
                email = ""
                if contact:
                    for span in contact.find_all("span"):
                        if "Phone" in span.get_text():
                            phone = span.get_text(strip=True).replace("Phone:", "").strip()
                        if "Email" in span.get_text():
                            email = span.get_text(strip=True).replace("Email:", "").strip()
                direction_wrap = store.find("div", class_="wpsl-direction-wrap")
                distance = ""
                directions_link = ""
                if direction_wrap:
                    distance = direction_wrap.get_text(strip=True).split("Directions")[0].strip()
                    a_tag = direction_wrap.find("a")
                    if a_tag:
                        directions_link = a_tag["href"]
                unique_stores[store_id] = [name, street, city_state_zip, country, phone, email, distance, directions_link]
                
        except Exception as e:
            print(f"Error processing {location}: {e}")
            continue
        
        # Save intermediate results every 10 searches
        if current_search % 10 == 0:
            filename = f"kirby_service_centers_{config_name}_intermediate_{current_search}.csv"
            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    "Name", "Street", "City/State/Zip", "Country", "Phone", "Email", "Distance", "Directions Link"
                ])
                for row in unique_stores.values():
                    writer.writerow(row)
            print(f"Intermediate save: {len(unique_stores)} unique service centers")

    # Save to CSV
    filename = f"kirby_service_centers_{config_name}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Name", "Street", "City/State/Zip", "Country", "Phone", "Email", "Distance", "Directions Link"
        ])
        for row in unique_stores.values():
            writer.writerow(row)

    driver.quit()
    print(f"Scraping complete! {len(unique_stores)} unique service centers saved to {filename}")

if __name__ == "__main__":
    main()