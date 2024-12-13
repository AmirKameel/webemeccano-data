# Parameters
link = 'https://yellowpages.com.eg/ar/search/%D9%85%D8%B7%D8%A7%D8%B9%D9%85'  # URL to scrape
output_folder_path = r'C:\Users\Win 10\Desktop\webemeccano-data-main'  # Folder to save the output file
output_file_name = 'res21'  # Output file name (without extension)
last_page = 10  # Scrape until the last page (-1) or a specific number of pages
start_page = 1  # Start with page 1

import subprocess
import sys
import time
import pandas as pd
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

def install_and_import(package):
    """Install a package if it is not already installed."""
    try:
        __import__(package)
    except ImportError:
        print(f"{package} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"{package} installed successfully.")

# List of packages to install
packages = [
    "selenium",
    "pandas",
    'undetected_chromedriver',
    'time'
]

# Install necessary packages
for package in packages:
    install_and_import(package)

def get_data(link, output_folder_path, output_file_name, last_page, start_page):
    """Main function to scrape data from the given website link."""
    driver = uc.Chrome()  # Initialize the Chrome driver
    try:
        driver.get(link)  # Navigate to the link
        time.sleep(5)  # Wait for the page to load

        # Initialize lists to store data
        descraption, imgs, whatsapp, websites, phones, names, address, address_links, categories = (
            [] for _ in range(9)
        )

        # Determine the last page to scrape
        if last_page == -1:
            last_page = int(driver.find_element(By.CLASS_NAME, 'last-page').get_attribute('href').split('/p')[1])

        # Loop through each page to scrape
        for page in range(start_page, last_page + 1):
            print(f"Scraping page {page}/{last_page}...")
            driver.get(link + f'/p{page}')
            time.sleep(5)  # Wait for the page to load

            # Locate the parent element containing company data
            parent_element = driver.find_element(By.CLASS_NAME, 'companyCards')

            # Extract data for each company
            for e in parent_element.find_elements(By.CLASS_NAME, 'item-title'):
                names.append(e.text)  # Company name
            for e in parent_element.find_elements(By.CLASS_NAME, 'address-text'):
                address.append(e.text)  # Company address
                address_links.append(e.get_attribute('href'))  # Address link
            for e in parent_element.find_elements(By.CLASS_NAME, 'category'):
                categories.append(e.text)  # Company category

            # Extract websites for each company
            all_action_btns = parent_element.find_elements(By.CLASS_NAME, 'item-action-btns')
            for i in all_action_btns:
                try:
                    websites.append(i.find_element(By.CLASS_NAME, 'website').get_attribute('href'))
                except:
                    websites.append('')

            # Extract phone numbers
            for value in parent_element.find_elements(By.CLASS_NAME, 'call-us-click'):
                try:
                    value.click()  # Click to reveal phone number
                    time.sleep(2)
                    phones.append(
                        '\n'.join([e.find_element(By.TAG_NAME, 'a').text for e in driver.find_elements(By.CLASS_NAME, 'popover-phones')])
                    )
                    value.click()  # Close the phone pop-up
                except:
                    phones.append('')

            # Extract descriptions, images, and WhatsApp links
            for i in parent_element.find_elements(By.CLASS_NAME, 'item-details'):
                try:
                    descraption.append(i.find_element(By.CLASS_NAME, 'item-aboutUs').text)  # Company description
                except:
                    descraption.append('')
                try:
                    imgs.append(i.find_element(By.CLASS_NAME, 'logo-container').find_element(By.TAG_NAME, 'img').get_attribute('src'))  # Company logo
                except:
                    imgs.append('')
                try:
                    whatsapp.append(i.find_element(By.CLASS_NAME, 'whatsAppLink').get_attribute('href'))  # WhatsApp link
                except:
                    whatsapp.append('')

            # Extract image thumbnails
            for idx, img in enumerate(imgs):
                try:
                    thumbnails = driver.find_element(By.CLASS_NAME, f'photo{idx}-thumbnails').find_elements(By.TAG_NAME, 'img')
                    new_imgs = ['https:' + thumb.get_attribute('data-src') for thumb in thumbnails]
                    imgs[idx] = img + '\n' + '\n'.join(new_imgs)  # Add thumbnails to image list
                except:
                    continue

        # Save the scraped data
        save(names, websites, phones, whatsapp, address, address_links, descraption, categories, imgs, output_folder_path, output_file_name)

    finally:
        try:
            driver.quit()  # Close the browser
        except Exception as e:
            print(f"Error during cleanup: {e}")

def pad_list(lst, target_length, fill_value=None):
    """Pad a list to ensure it has the same length as the longest list."""
    return lst + [fill_value] * (target_length - len(lst))

def save(names, websites, phones, whatsapp, address, address_links, descraption, categories, imgs, output_folder_path, output_file_name):
    """Save scraped data to a CSV file."""
    max_length = max(len(names), len(websites), len(phones), len(whatsapp), len(address), len(address_links), len(descraption), len(categories), len(imgs))
    
    # Ensure all lists are the same length by padding
    names = pad_list(names, max_length)
    websites = pad_list(websites, max_length)
    phones = pad_list(phones, max_length)
    whatsapp = pad_list(whatsapp, max_length)
    address = pad_list(address, max_length)
    address_links = pad_list(address_links, max_length)
    descraption = pad_list(descraption, max_length)
    categories = pad_list(categories, max_length)
    imgs = pad_list(imgs, max_length)

    data = {
        "Name": names,
        "Website": websites,
        "Phone": phones,
        "WhatsApp": whatsapp,
        "Address": address,
        "Map": address_links,
        "Description": descraption,
        "Category": categories,
        "Images": imgs,
    }

    # Convert data to a pandas DataFrame
    df = pd.DataFrame(data)

    # Save as CSV
    output_file = rf'{output_folder_path}\{output_file_name}.csv'
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

# Run the scraper
get_data(link, output_folder_path, output_file_name, last_page, start_page)
