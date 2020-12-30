import requests
from bs4 import BeautifulSoup as bs


def pemex_scrapper(pemex_url):

    ## Requesting Pemex Site
    page = requests.get(pemex_url)
    print("Request Status: ",page)

    ## Scrapping WebSite
    soup = bs(page.content, 'html.parser')
    table = soup.find(id='mitabla')
    rows = table.find_all("tr")

    # Getting Headings
    row0 = rows[0].find_all("th")
    head_names = []
    for el in row0:
        head_names.append(el.text)

    # Getting Content
    content = []
    max_el = 5
    for row in rows[1:max_el+1]:
        cells = row.find_all("td")
        dict2 = {head_names[i]:cells[i].text for i in range(len(cells))}
        content.append(dict2)

    return content
