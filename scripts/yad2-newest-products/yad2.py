from selenium import webdriver
from bs4 import BeautifulSoup, Tag
from datetime import datetime, timedelta
import time

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)


def is_outdated(iso_date: str, days_threshold: int):
    # Convert the ISO date string to a datetime object
    try:
        date_obj = datetime.fromisoformat(iso_date)
    except ValueError:
        print("Invalid ISO date format.")
        return False

    # Get the current date
    current_date = datetime.now()

    # Calculate the difference between the current date and the given date
    difference = current_date - date_obj

    # Check if the difference is equal to or greater than three days
    if difference >= timedelta(days=days_threshold):
        return True
    else:
        return False


def search_for_item(keyword: str):

    driver.get("https://www.yad2.co.il/products/furniture?category=2&info={}".format(keyword))
    html = driver.page_source

    if "captcha" in html:
        time.sleep(20)

    html = driver.page_source

    soup = BeautifulSoup(html, "html.parser")
    recent_items = soup.find_all("div", class_="feeditem table")

    for item in recent_items:
        if not isinstance(item, Tag):
            continue

        item_data = {}

        title_el = item.find("span", class_="title")
        item_data["title"] = title_el.text.strip() if title_el else None

        if item_data["title"] == None:
            print("No title for item")
            continue

        price_el = item.find("span", class_="price")
        item_data["price"] = price_el.text.strip() if price_el else ""

        img_el = item.find("img", class_="feedImage")
        item_data["img"] = img_el.get("src") if img_el else ""

        item_id_el = item.find("div", attrs={"item-id": True})
        if item_id_el == None:
            print("Couldn't get item id")
            continue

        item_data["url"] = "https://www.yad2.co.il/products/item/" + item_id_el.get("item-id")

        date_el = item.find("span", class_="date")
        item_data["date"] = date_el.text.strip() if date_el else ""

        if item_data["date"] != "עודכן היום":
            try:
                item_data["date"] = datetime.strptime(item_data["date"], "%d/%m/%Y").isoformat()

                if is_outdated(item_data["date"], days_threshold=3):
                    continue

            except ValueError:
                print("Failed to transform date of publish/update for item")
                print(item_data)
                continue

        yield item_data


def main():
    with open("keywords.txt") as file:
        keywords = [l.rstrip().lstrip().strip() for l in file]

    with open("items.csv", "w") as file:
        file.write("Keyword,Product,Price,Image,Link,Date\n")
        for key in keywords:
            for item in search_for_item(key):
                data_to_write = '"' + key + '"' + "," + ",".join('"' + val + '"' for val in item.values()) + "\n"
                file.write(data_to_write)


if __name__ == "__main__":
    main()
