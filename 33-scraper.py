from bs4 import BeautifulSoup
import requests

url = "https://en.wikipedia.org/wiki/Artificial_intelligence"

# 1. Create the Fake ID Badge (This is an exact copy of a Google Chrome User-Agent)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 2. Pass the headers into the get request
response = requests.get(url, headers=headers)

article = response.text

soup = BeautifulSoup(article, 'html.parser')

# print(soup.title.text)

content = soup.find_all('p')

massive_string = ""
for paragraph in content:
    massive_string += paragraph.get_text() +"\n"

print(massive_string[:500]) # Prints just the first 500 characters

