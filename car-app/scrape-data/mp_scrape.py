import multiprocessing as mp
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import time
from parse_text import parse_vehicle_title, clean_location
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')
db = client['car_database']
collection = db['vehicle_details']


chrome_driver_path = r'C:\Users\sebas\Downloads\chromedriver-win64-new\chromedriver-win64\chromedriver.exe'
base_url = 'https://www.cars.com/shopping/results/?dealer_id=&include_shippable=true&keyword=&list_price_max=60000&list_price_min=&makes[]=&maximum_distance=30&mileage_max=&monthly_payment=1114&page=4&page_size=20&sort=best_match_desc&stock_type=all&year_max=&year_min=&zip=10305'
web_url = 'https://www.cars.com'
cur_url = base_url

def extract_vehicle_details(element):
    
    extracted_details = {}
    try:
        # img_src = [element.find_element(By.CSS_SELECTOR, f"div.image-wrap[data-index='{i}']").find_element(By.TAG_NAME, "img").get_attribute("src") for i in range(6)]
        img_src = []
        for i in range(6):
            try:
                img_src.append(element.find_element(By.CSS_SELECTOR, f"div.image-wrap[data-index='{i}']").find_element(By.TAG_NAME, "img").get_attribute("src"))
            except:
                break
    except:
        img_src = None
        
    try:
        stock_type_element = element.find_element(By.CLASS_NAME, "stock-type")
        stock_type = stock_type_element.text
    except:
        stock_type = None
    
    try:
        title_element = element.find_element(By.CLASS_NAME, "title")
        title = title_element.text
        year_make_model = parse_vehicle_title(title)
        
    except:
        year_make_model = {'year': None, 'make': None, 'model_trim': None}
    
    try:
        mileage_element = element.find_element(By.CLASS_NAME, "mileage")
        mileage = mileage_element.text
    except:
        mileage = None
    
    try:
        primary_price_element = element.find_element(By.CLASS_NAME, "primary-price")
        primary_price = primary_price_element.text
    except:
        primary_price = None
    
    try:
        dealer_name_element = element.find_element(By.CLASS_NAME, "dealer-name")
        dealer_name = dealer_name_element.text
    except:
        dealer_name = None
    
    try:
        location_element = element.find_element(By.CLASS_NAME, "miles-from")
        location = location_element.text
        location = clean_location(location)
    except:
        location = None
    
    extracted_details.update({
        'img_src': img_src,
        'stock_type': stock_type,
        'mileage': mileage,
        'primary_price': primary_price,
        'dealer_name': dealer_name,
        'location': location
    })
    extracted_details.update(year_make_model)
    
    return extracted_details

# @profile
def find_car_specs(driver):
    car_specs = {}
    try:
        # find basic section
        wait = WebDriverWait(driver, 10)
        try:
            basic_section = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sds-page-section.basics-section")))
            description_list = basic_section.find_element(By.CLASS_NAME, "fancy-description-list")
        except TimeoutException:
            print("Timed out waiting for car specs section to load.")
            return car_specs

        if description_list:
            html_string = description_list.get_attribute('innerHTML')
            soup = BeautifulSoup(html_string, "html.parser")
            for dt, dd in zip(soup.find_all("dt"), soup.find_all("dd")):
                if not dt or not dd:
                    continue
                key = dt.text.strip()
                if key == "MPG":
                    value = dd.find("span").text.strip() if dd.find("span") else "N/A"
                else:
                    value = dd.text.strip()
                car_specs[key] = value

    except Exception as e:
        print("Error extracting details from basic section:", e)
    
    return car_specs

# @profile
def find_seller_info_car_info(driver):
    seller_info_car_info = {
        "seller_info": None,
        "car_on_seller_website": None,
        "seller_website": None,
        "seller_notes": None,
        "car_rating": None,
        "car_total_reviews": None,
        "car_total_reviews_text": None
    }

    try:
        seller_info_section = driver.find_element(By.CSS_SELECTOR, ".sds-page-section.seller-info")
        
        # print(seller_info_section.get_attribute('innerHTML'))
        try:
            seller_info_car_info["seller_info"] = seller_info_section.find_element(By.CLASS_NAME, "spark-heading-5.heading.seller-name").text
        except:
            pass
        
        
        try:
            external_links_element = seller_info_section.find_element(By.ID, "external_listing_links")
            external_links = external_links_element.find_elements(By.TAG_NAME, "a")
            if external_links:
                seller_info_car_info["car_on_seller_website"] = external_links[0].get_attribute("href")
                if len(external_links) > 1:
                    seller_info_car_info["seller_website"] = external_links[1].get_attribute("href")
        except:
            pass

        try:
            seller_info_car_info["seller_notes"] = seller_info_section.find_element(By.CLASS_NAME, "seller-notes").text
        except:
            pass
        
        try:
            seller_info_car_info["seller_address"] = seller_info_section.find_element(By.CLASS_NAME, "dealer-address").text
        except:
            pass
        
        # Extracting car review details
        try:
            wait = WebDriverWait(driver, 10)
            car_reviews_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "reviews-content-wrapper")))
            # print("Car reviews section found.")
            
            # print(car_reviews_element.get_attribute('innerHTML'))
            
            try:
                car_rating_element = driver.find_element(By.CSS_SELECTOR, "spark-rating[rating][size]")
                if car_rating_element:
                    seller_info_car_info["car_rating"] = car_rating_element.get_attribute("rating")
            except:
                print("Car rating not found.")
            
            try:
                car_review_link = car_reviews_element.find_element(By.TAG_NAME, "a")
                # print(car_review_link.get_attribute("href"))
                # print(car_review_link.text)
                seller_info_car_info["car_total_reviews"] = car_review_link.get_attribute("href")
                seller_info_car_info["car_total_reviews_text"] = car_review_link.text
            except:
                print("Car review link not found.")
            
        except TimeoutException:
            print("Car reviews section not found.")

    except Exception as e:
        print("Error extracting details from seller info:", e)
        
    return seller_info_car_info

# @profile
def find_vehicle_ratings(driver):
    sample_ratings = {}
    try:
        sample_review_element = driver.find_elements(By.CSS_SELECTOR, ".sds-container.consumer-review-container")[:2]
        for i, review_element in enumerate(sample_review_element):
            try:
                sample_rating = review_element.find_element(By.TAG_NAME, "spark-rating").get_attribute('rating')
                sample_review_heading = review_element.find_element(By.TAG_NAME, "h3").text
                sample_review_text = review_element.find_element(By.CLASS_NAME, "review-body").text
                sample_ratings[f"review_{i+1}_rating"] = sample_rating
                sample_ratings[f"review_{i+1}_heading"] = sample_review_heading
                sample_ratings[f"review_{i+1}_text"] = sample_review_text
            except:
                print("No reviews found.")
        # vehicle_details[-1].update(sample_ratings)
        
    except:
        print("No reviews found.")
    return sample_ratings

def scrape_main_page(current_page_url):
    service = Service(executable_path=chrome_driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") 
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get(current_page_url)
    next_page_url = driver.find_element(By.ID, "next_paginate").get_attribute("href")
    
    vehicle_card_elements = driver.find_elements(By.CSS_SELECTOR, ".vehicle-card")
    vehicle_details = {}
    for element in vehicle_card_elements:
        # link = element.find_element(By.TAG_NAME, "a").get_attribute("href")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )
        link = element.find_element(By.TAG_NAME, "a").get_attribute("href")
        vehicle_details[link] = extract_vehicle_details(element)
    driver.quit()
    return [vehicle_details, next_page_url]

def worker(car_url):
    service = Service(executable_path=chrome_driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") 
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=service, options=options)
    
    res = {car_url: {}}
    
    try:
        driver.get(car_url)
        print(f"Processing URL: {car_url}")
        
        try:
            res[car_url].update(find_car_specs(driver))
            res[car_url].update(find_seller_info_car_info(driver))
            res[car_url].update(find_vehicle_ratings(driver))

        except Exception as e:
            print("Error extracting:", e)
            
    finally:
        driver.quit()
    
    return res
    
if __name__ == "__main__":
    
    for i in range(5):
        info = scrape_main_page(cur_url)
        main_page_info = info[0] # {'url': {'img_src': [], 'mileage': '123'}}
        cur_url = web_url + info[1]
        # print(main_page_info)
        
        links = list(main_page_info.keys())
        
        print(f"Found {len(links)} links. Starting multiprocessing...")

        ts = time()
        with mp.Pool(processes=mp.cpu_count()) as pool:
            detail_page_info = pool.map(worker, links) # [{'url': {'color': 'red'}}, {'url': {'color': 'blue'}}]
        
        for detail in detail_page_info:
            detail_url = list(detail.keys())[0]
            detail_info = detail[detail_url]
            main_page_info[detail_url].update(detail_info)
            collection.insert_one(main_page_info[detail_url])
            
        print(f'page {i+1} Took {time() - ts}s')