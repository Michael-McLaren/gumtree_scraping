from typing import Any, Callable, List
import requests
from bs4 import BeautifulSoup
import re
import pymysql


class scraper:
    def __init__(
        self, category: str, query: str, location: str, keywords: List[str] = []
    ) -> None:
        self.category = category
        self.query = query
        self.location = location
        self.keywords = keywords

        self.listings: List = []

    def conditions(self, item: Any):

        if any(
            keyword in (item.description or item.title) for keyword in self.keywords
        ):
            return True
        else:
            return False

    def scrape_page(self) -> None:

        url = "https://www.gumtree.com/search?search_category={}&q={}&search_location={}".format(
            self.category, self.query, self.location
        )
        response = requests.get(url)
        content = BeautifulSoup(response.content, "html.parser")
        # fmt: off
        for listing_article in content.find_all("article", class_="listing-maxi"):
            item = Item()
            link = listing_article.find("a", class_="listing-link")["href"]
            item.link = "gumtree.com" + link
            l_content = listing_article.find("div", class_="listing-content")
            item.title = l_content.find("h2", class_="listing-title").get_text()
            item.location = l_content.find("div", class_="listing-location").span.get_text()
            item.description = l_content.find("p", class_="listing-description").get_text()
            price = l_content.find("span", class_="listing-price").strong.get_text()
            price = re.sub("[^0-9]", "", price)
            item.price = int(price)
            
            if self.keywords:
                if self.conditions(item):
                    self.listings.append(item)
            else:
                self.listings.append(item)

        # fmt: on

    def print_listings(self, num: int) -> None:

        for i in range(num):
            print(self.listings[i].print)

    def store_data(self):
        password = input("Password: ")
        conn = pymysql.connect(
            host="127.0.0.1",
            unix_socket="/tmp/mysql.sock",
            user="root",
            passwd=password,
            db="mysql",
        )
        cur = conn.cursor()
        cur.execute("USE gumtree")

        def store_item(item):
            cur.execute(
                f"INSERT INTO listing (title, link, location, description_, price) VALUES ({item.title}, {item.link}, {item.location}, {item.description}, {item.price})"
            )
            cur.connection.commit()

        try:
            for item in self.listings:
                store_item(item)

        finally:
            cur.close()
            conn.close()


class Item:
    """
    An individual gumtree item
    """

    def __init__(self):
        self.title = ""
        self.link = ""
        self.location = ""
        self.description = ""
        self.price = -1

    @property
    def print(self):
        output = "title: {} \nlink: {} \nlocation: {} \ndescription: {} \nprice: {}\n".format(
            self.title, self.link, self.location, self.description, self.price
        )
        print(output)


scraper1 = scraper("all", "climbing+shoe", "edinburgh")
scraper1.scrape_page()
scraper1.print_listings(2)
