import requests
from bs4 import BeautifulSoup

# structure:
# https://www.apotheken-umschau.de/medikamente/arzneimittellisten/
#       .../arzneimittellisten/medikamente_a.html
#       .../arzneimittellisten/medikamente_a-2.html
#       .../arzneimittellisten/medikamente_a-3.html
# ...
#       .../arzneimittellisten/medikamente_b.html
#       .../arzneimittellisten/medikamente_2.html
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
medication_url = "/medikamente/arzneimittellisten/"

# output file for medication list
output_file = open("medication_list.txt", "w", encoding="utf-8")

# general medication page
# medication pages are split into initial letters
# each initial letter is split into multiple pages for this letter

# contains list of all general medication pages (starting with one letter)
content = extract_and_parse_content(base_url + medication_url)
general_pages_links = content.find_all('a', href=True)

# visit general pages for medication starting with one letter
for general_pages_link in general_pages_links:
    general_page = general_pages_link['href']

    # filter links
    if general_page.startswith("/medikamente") and general_page.endswith(".html"):

        # contains list of all specific medication pages (multiple parts for one letter)
        medication_pages_url = base_url + general_page
        medication_pages_content = extract_and_parse_content(medication_pages_url)
        medication_pages_links = medication_pages_content.find_all('a', href=True)

        # medication pages starting with one letter are split into multiple pages for this letter
        # visit pages that contain parts of medication names starting with this letter
        visited = False  # the same page should only be visited once
        current_page_url = ""
        for medication_pages_link in medication_pages_links:
            medication_page_part_url = medication_pages_link['href']
            general_page_url_without_ending = general_page.replace(".html", "")

            # medication pages starting with one letter are split into multiple parts
            medication_list = []
            if general_page_url_without_ending in medication_page_part_url:
                if current_page_url == medication_page_part_url:  # check if page has already be visited
                    visited = True
                else:
                    current_page_url = medication_page_part_url

                if not visited:         # page has not been visited
                    # contains partial list of medication names for this initial letter
                    medication_content = extract_and_parse_content(base_url + medication_page_part_url)
                    # page with medication, parse names
                    partial_medication_pages_links = medication_content.find_all('a', href=True)
                    for partial_medication_pages_link in partial_medication_pages_links:
                        href = partial_medication_pages_link["href"]

                        if href.startswith("/medikamente/beipackzettel") and href.endswith(".html"):
                            # get text from url
                            text = partial_medication_pages_link.get_text(strip=True)

                            # medication name is the first word
                            medication_name = text.split()[0]

                            # use list to filter duplicates
                            if medication_name not in medication_list:
                                medication_list.append(medication_name)
                else:
                    visited = False

            # write medication names to file
            for medication_name in medication_list:
                output_file.write(medication_name + "\n")


# close output file
output_file.close()
