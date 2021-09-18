#!/usr/bin/env python3
import argparse
import csv
import pprint
import ftfy

import requests
from bs4 import BeautifulSoup
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
    print(f"names: {names}")
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
                        pair[0], {"class", pair[1]}, recursive=False
                    )
                # do not use class if no class
                else:
                    # set the parent element to the children that matches the pattern pair
                    elements[i] = elements[i].findChildren(pair[0], recursive=False)
                # if found valid children, add the array of children to existing children
                if elements[i] is not None:
                    children.extend(elements[i])
                # if did not find valid children, set the element to None
                else:
                    elements[i] = None
                print(elements[i])
        # after iterating through parent elements, set parent elements to the valid child elements, then recursion
        elements = children
    return elements


# Returns either the text elements or links in a given soup object by pattern
def get_text_by_pattern(soup, pattern, get_link=False):
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
        # set final output as text if element is not anchor tag
        if not get_link:
            wanted.append(el.text.strip())
        # set final output as link if element is anchor tag
        else:
            wanted.append(el["href"])
    return list(dict.fromkeys(wanted))


# returns an array of string issues of this candidate
def get_issues(soup):
    issues = get_text_by_pattern(soup, args.issue_pattern)
    return issues


def get_descriptions(soup, url):
    descriptions = []
    if args.follow_link:
        # get the links to each issue descriptions
        links = get_text_by_pattern(soup, args.follow_link, get_link=True)
        print(links)
        for link in links:
            # construct full url if link is relative url
            if link[0] == "/":
                link = url.rsplit('/', 1)[0] + link
            # get soup obj of new page
            soup = get_page_soup(link)
            # get the issue description by using the description pattern arg
            description = get_text_by_pattern(soup, args.description_pattern)
            # convert paragraphs of description into a string
            description = "\n".join(description)
            descriptions.append(description.strip())
    else:
        # if all on same page, just get the description
        descriptions = get_text_by_pattern(soup, args.description_pattern)
    return descriptions


def main():
    soup = get_page_soup(args.url)
    issues = list(filter(None, get_issues(soup)))
    descriptions = list(filter(None, get_descriptions(soup, args.url)))[1:12]
    print(issues)
    for i, desc in enumerate(descriptions):
        print(f"======= {i} =======")
        print(f"{desc[:20]}....{desc[-20:-1]}")
    # check if there is an issue description correspond to each issue
    if len(issues) != len(descriptions) and not args.force:
        print(f"Error: Issue length({len(issues)}) does not match description length({len(descriptions)})")
        return
    if (args.outfile):
        path = args.outfile
    else:
        path = 'out'

    Path(path).mkdir(parents=True, exist_ok=True)

    filename = path + "/" + args.name.replace(' ', '_') + '.csv'
    length = len(issues)
    # add empty string to whichever is not parsed successfully
    if len(issues) < len(descriptions):
        length = len(descriptions)
        while len(issues) < length:
            issues.append("")
    else:
        while len(descriptions) < length:
            descriptions.append("")

    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(length):
            writer.writerow([args.name, ftfy.fix_text(issues[i]),
                             ftfy.fix_text(descriptions[i]), args.url])
        writer.writerow(["", "", "", ""])

# ./scraper.py "Adam Schiff" "https://adamschiff.com/issues/" "div#toggle default>h3" "div#wpb_text_column wpb_content_element>div#wpb_wrapper"
# ./scraper.py -fl "div#tiles>div>a" "Pete Aguilar" "https://peteaguilar.com/on-the-issues/" "div#not-secret>h3" "section#article>div#insides"
# ./scraper.py -fl "div>div#_2Z-zX>a" "Josh Barnett" "https://www.barnettforaz.com/cd7-issues-arizona" "div>div#_2Z-zX>a" "div#_1Q9if"

main()
