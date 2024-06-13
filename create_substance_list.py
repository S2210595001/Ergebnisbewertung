import requests
from bs4 import BeautifulSoup
import re

# structure:
# https://www.apotheken-umschau.de/medikamente/wirkstofflisten/
#       .../wirkstofflisten/wirkstoffe_a.html
#       .../wirkstofflisten/wirkstoffe_b.html
# ...
#       .../wirkstofflisten/wirkstoffe_z.html
# ...

# extract html content from url
def extract_and_parse_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
    else:
        print("Error reading page:", response.status_code)
    return BeautifulSoup(html_content, 'html.parser')

# base url to extract medication names
base_url = "https://www.apotheken-umschau.de"
medication_url = "/medikamente/wirkstofflisten/"

# output file for substance list
output_file = open("substance_list.txt", "w", encoding="utf-8")

# general substance page
# substance pages are split into initial letters

# contains list of all general medication pages (starting with one letter)
content = extract_and_parse_content(base_url + medication_url)
general_pages_links = content.find_all('a', href=True)

counter = 0
# find links to general pages for substances starting with one letter
for general_pages_link in general_pages_links:
    general_page = general_pages_link['href']

    # filter links for substances starting with one letter
    if general_page.startswith("/medikamente/") and general_page.endswith(".html"):
        # complete url
        medication_pages_url = base_url + general_page

        medication_pages_content = extract_and_parse_content(medication_pages_url)
        # contains links to all substance names
        medication_pages_links = medication_pages_content.find_all('a', href=True)

        substance_list = []
        for medication_pages_link in medication_pages_links:
            specific_page = medication_pages_link['href']
            # filter links to substance names
            if re.match("^/medikamente/wirkstofflisten/[\W\w]*[\d]+.html", str(specific_page)):

                # get text from url
                text = medication_pages_link.get_text(strip=True)

                # substance name is the first word
                words = text.split(" ")
                substance_name = words[0].upper()

                # use list to filter duplicates
                if substance_name not in substance_list:
                    substance_list.append(substance_name)

        # write medication names to file
        for substance_name in substance_list:
            output_file.write(substance_name + "\n")








