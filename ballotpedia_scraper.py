#!/usr/bin/env python3
import argparse
import csv
import pprint
import ftfy

import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
from pathlib import Path

parser = argparse.ArgumentParser(description="Scrapes candidate issue info")
parser.add_argument("name", metavar="N", type=str, help="Name of candidate")
parser.add_argument("url", metavar="U", type=str, help="URL of candidate")
parser.add_argument("-o", "--outfile", dest='outfile', type=str, required=False,
                    help="location of the output file (default is out)")

parser.add_argument(
    "issue_pattern",
    metavar="I",
    type=str,
    help="HTML Element pattern of the issue element, see README for pattern explanation",
)
parser.add_argument(
    "description_pattern",
    metavar="D",
    type=str,
    help="HTML Element pattern of the description element, see README for pattern explanation",
)
parser.add_argument(
    "-fl",
    "--follow-link",
    dest="follow_link",
    type=str,
    required=False,
    help="If issue element is link to a page with the description",
)

parser.add_argument(
    "-f",
    "--force",
    dest="force",
    action='store_true',
    help="Force write to csv"
)

parser.add_argument(
    "-i",
    "--invalid",
    dest="invalid",
    action='store_true',
    help="Force to make invalid HTTP request"
)

args = parser.parse_args()
pp = pprint.PrettyPrinter(indent=4)


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
def get_candidate_names_links(soup, pattern, get_link=False):
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
            print(el["href"])
            wanted.append((el.text.strip(), el["href"]))
    return wanted


def get_individual_candidate_bio(candidates_name_link):
    link = candidates_name_link[1]
    soup = get_page_soup(link)
    info_box_html = soup.select('div.infobox.person')
    candidate_data = OrderedDict([('Name', ''), ('DOB', ''), ('status', ''), ('currentOffice', ''), ('Party', ''), ('OfficeType', ''), ('Office', ''), ('State', ''), ('Email', ''), ('Education', ''), ('Profession', ''), ('District', ''), ('Photo', ''), ('Twitter', ''), ('Facebook', ''), ('Instagram', ''), ('YouTube', ''), ('Campaign Website', ''), ('Gender', ''), ('Race', ''), ('FEC ID', ''), ('recipient.cfscore', ''), ('contrib.cfscore', ''), ('Election', '')])
    print(candidate_data)


def main():
    soup = get_page_soup(args.url)
    candidates_names_links = get_candidate_names_links(soup, args.issue_pattern)
    print(candidates_names_links)
    get_individual_candidate_bio(candidates_names_links[1])
    #Name,DOB,status,currentOffice,Party,OfficeType,Office,State,Email,Education,Profession,District,Photo,Twitter,Facebook,Instagram,YouTube,Campaign Website,Gender,Race,FEC ID,recipient.cfscore,contrib.cfscore,Election




if __name__ == '__main__':
    main()
