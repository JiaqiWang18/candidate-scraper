#!/usr/bin/env python3
import argparse
import csv
import pprint
import ftfy
import re
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
from pathlib import Path

parser = argparse.ArgumentParser(description="Scrapes candidate bio info")
parser.add_argument("url", metavar="U", type=str, help="URL of candidate list")
parser.add_argument("-o", "--outfile", dest='outfile', type=str, required=False,
                    help="location of the output file (default is out)")

parser.add_argument(
    "table_type",
    metavar="D",
    type=str,
    help="HTML Element pattern of the type of table, see README for pattern explanation",
)

parser.add_argument(
    "name_of_last_candidate_in_table",
    metavar="D",
    type=str,
    help="Used to separate tables",
)

parser.add_argument(
    "-i",
    "--invalid",
    dest="invalid",
    action='store_true',
    help="Force to make invalid HTTP request"
)

parser.add_argument(
    "-f",
    dest="name_of_first_candidate_in_table",
    metavar="D",
    type=str,
    required=False,
    help="Used to separate tables",
)

args = parser.parse_args()
pp = pprint.PrettyPrinter(indent=4)
STATE_NAMES = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}
OFFICE_TYPES = ["House of Representatives", "District Attorney", "Lieutenant Governor", "House of Delegates",
                "City Council", "Governor", "U.S. House", "Mayor", "City Controller", "Court of Common Pleas",
                "Municipal Court", "City Attorney"]
TABLE_PATTERN = {
    'table': 'div>table#candidateListTablePartisan>p>a',
    'list': 'tr#results_row>a'
}
TABLE_HEADER = "Name,DOB,status,currentOffice,Party,OfficeType,Office,State,Email,Education,Profession,District,Photo," \
               "Twitter,Facebook,Instagram,YouTube,Campaign Website,Gender,Race,FEC ID,recipient.cfscore,contrib.cfscore," \
               "Election".split(",")


# Generates beautiful soup object
def get_page_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }
    if not args.invalid:
        page = requests.get(url, headers=headers).content
    else:
        page = requests.get(url, headers=headers, verify=False).content

    return BeautifulSoup(page, "html.parser")


# Gets the innermost children of the passed elements given the names where
# names is a list of pairs of strings (element_name, element_class)
def get_children(names, elements):
    # iterate through pattern pairs
    for pair in names:
        children = []
        # iterate through parent elements
        for i in range(0, len(elements)):
            if elements[i] is not None:
                # if patter pair has class, use the class
                if pair[1]:
                    # set the parent element to the children that matches the pattern pair
                    elements[i] = elements[i].findChildren(
                        pair[0], {"class", pair[1]}, recursive=True
                    )
                # do not use class if no class
                else:
                    # set the parent element to the children that matches the pattern pair
                    elements[i] = elements[i].findChildren(pair[0], recursive=True)
                # if found valid children, add the array of children to existing children
                if elements[i] is not None:
                    children.extend(elements[i])
                # if did not find valid children, set the element to None
                else:
                    elements[i] = None
        # after iterating through parent elements, set parent elements to the valid child elements, then recursion
        elements = children
    return elements


# Returns either the text elements or links in a given soup object by pattern
def get_candidate_names_links(soup, pattern):
    element_names_unformatted = pattern.split(">")
    element_names = []
    # loop that parse pattern and store a list of tag, class pair
    for el_name in element_names_unformatted:
        if "#" in el_name:
            el_parts = el_name.split("#")
            element_names.append((el_parts[0], el_parts[1]))
        else:
            element_names.append((el_name, None))
    # print(element_names)
    elements = None
    # now find parent elements
    if element_names[0][1]:
        # if has class name, find with class
        if element_names[0][1][0] == "^":
            elements = soup.find_all(id=element_names[0][1][1:])
            print(elements)
        else:
            elements = soup.find_all(element_names[0], {"class": element_names[0][1]})
    else:
        # find without class
        elements = soup.find_all(element_names[0])
    # elements contain all parent elements found, now we find children of that element that matches the pattern
    elements = list(get_children(element_names[1:], elements))
    # get rid of None or empty strings
    elements = list(filter(lambda x: x is not None and len(x) != 0, elements))
    # elements now contain all the children that matches the pattern

    wanted = []
    for el in elements:
        if el.text.strip() != '':
            if el.text.strip() == args.name_of_first_candidate_in_table:
                wanted = []
            wanted.append((el.text.strip(), el["href"]))
            if el.text.strip() == args.name_of_last_candidate_in_table:
                break
    for w in wanted:
        print(w[0])
    return wanted


def get_individual_candidate_bio(candidates_name_link):
    link = candidates_name_link[1]
    soup = get_page_soup(link)
    info_box_html = soup.select('div.infobox.person')[0]
    candidate_data = OrderedDict(
        [('Name', candidates_name_link[0]), ('DOB', ''), ('status', ''), ('currentOffice', ''), ('Party', ''),
         ('OfficeType', ''),
         ('Office', ''), ('State', ''), ('Email', ''), ('Education', ''), ('Profession', ''), ('District', ''),
         ('Photo', ''), ('Twitter', ''), ('Facebook', ''), ('Instagram', ''), ('YouTube', ''), ('Campaign Website', ''),
         ('Gender', ''), ('Race', ''), ('FEC ID', ''), ('recipient.cfscore', ''), ('contrib.cfscore', ''),
         ('Election', '')])
    candidate_data['Party'] = ' '.join(
        info_box_html.findChild()['class'][2:len(info_box_html.findChild()['class']) - 1])
    if candidate_data['Party'] == "Democratic": candidate_data['Party'] = "Democrat"
    photo = info_box_html.findChild({'img'})['src']
    candidate_data['Photo'] = photo if "Placeholder" not in photo else ''
    infos = info_box_html.findChildren(recursive=False)
    print(f"start parsing bio for {candidate_data['Name']}")
    for i, child in enumerate(infos):
        if "Candidate," in child.text:
            full_offcie_name = child.text.strip()
            for s in STATE_NAMES:
                if s in full_offcie_name:
                    candidate_data['State'] = STATE_NAMES[s]
                    break
            for o in OFFICE_TYPES:
                if o in full_offcie_name:
                    candidate_data['OfficeType'] = o
            candidate_data['Office'] = f"{candidate_data['State']} {candidate_data['OfficeType']}"
            if "District" in full_offcie_name:
                candidate_data['District'] = full_offcie_name[full_offcie_name.index("District"):]
        elif 'Profession' in child.text:
            candidate_data['Profession'] = child.text[child.text.index("Profession") + 11:].strip()
        elif "Campaign Facebook" in child.text:
            candidate_data['Facebook'] = child.findChild({'a'})['href']
        elif "Campaign Instagram" in child.text:
            candidate_data['Instagram'] = child.findChild({'a'})['href']
        elif "Campaign Twitter" in child.text:
            candidate_data['Twitter'] = child.findChild({'a'})['href']
        elif "Campaign website" in child.text:
            candidate_data['Campaign Website'] = child.findChild({'a'})['href']
        elif "Official website" in child.text:
            candidate_data['Campaign Website'] = child.findChild({'a'})['href']
        elif "Personal website" in child.text:
            candidate_data['Campaign Website'] = child.findChild({'a'})['href']
        elif "YouTube" in child.text:
            candidate_data['YouTube'] = child.findChild({'a'})['href']
        elif "Education" in child.text:
            edu = ", ".join(
                [re.sub("[\\t\\n\\r]+", "", tag.text) for tag in list(infos[i + 1].find_all({'div'}))][0:2])
            candidate_data['Education'] = edu
        elif "Tenure" in child.text:
            current_office = re.sub("[\\t\\n\\r]+", "", infos[i - 1].text)
            candidate_data['currentOffice'] = current_office
        # print(f"------{i}-------\n{child.text.strip()}")

    return list(candidate_data.values())


def main():
    soup = get_page_soup(args.url)
    if args.table_type == 'table':
        election_name = get_children([('h4', None)], soup.find_all({'table'}))[0].text
    else:
        election_name = get_children([('h5', 'votebox-header-election-type')],
                                     soup.find_all('div', {'class': 'race_header nonpartisan'}))[2].text
    print(election_name)
    candidates_names_links = get_candidate_names_links(soup, TABLE_PATTERN[args.table_type])
    print(len(candidates_names_links))
    # print(candidates_names_links)
    if args.outfile:
        path = args.outfile
    else:
        path = 'ballotpedia_out'
    Path(path).mkdir(parents=True, exist_ok=True)
    filename = path + "/" + election_name.replace(' ', '_') + '.csv'
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(TABLE_HEADER)
        for i, cl in enumerate(candidates_names_links):
            cand_data = get_individual_candidate_bio(cl)
            writer.writerow(cand_data)
            print(f"{i + 1}/{len(candidates_names_links)} Completed")


if __name__ == '__main__':
    main()
