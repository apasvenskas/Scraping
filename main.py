import requests
import selectorlib
import time
import smtplib, ssl

"INSERT INTO events VALUES ('Tigers', 'Tiger City', '1988.10.14)" # this sql query and will be excuted by python.


URL = "https://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def scrape(url):
    """ Scrape the pages source from webpage URL. """
    response = requests.get(url, headers=HEADERS)
    source = response.text
    return source

def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["tours"]
    return value

if __name__ == "__main__":
    scraped = scrape(URL)
    extrated = extract(scraped)
    print(extrated)

def send_email():
    print("Email was sent")

def store(extraction):
    with open("data.txt", "a") as file:
        file.write(extraction + "\n")

def read(extracted):
    with open("data.txt", "r") as file:
        return file.read()

if __name__ == "__main__":
    scraped = scrape(URL)
    extracted = extract(scraped)
    print(extracted) 
    content = read(extracted)
    if extracted != "No upcoming tours":
        if extrated not in content:
            store(extracted)
            send_email()