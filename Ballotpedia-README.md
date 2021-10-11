
# Installation<a id="sec-1"></a>

Clone this repository, then cd to the directory and run

```bash
pipenv install
chmod 777 ./ballotpedia_scraper.py
```

Start the virtual environment before running the script with

```bash
pipenv shell
```

# Usage<a id="sec-2"></a>

```bash
./ballotpedia_scraper.py U T L [-f NAME_OF_FIRST] [-n TABLE_NAME] [-tn USER_SPECIFIED_FILE_NAME]
```

Where:

| Parameter          | Description                                                           | Example                                   |
|------------------  |---------------------------------------------------------------------  |-----------------------------------------  |
| U                  | URL of the election page with names of the candidates                                                            | <https://ballotpedia.org/City_elections_in_Detroit,_Michigan_(2021)#Community_advisory_council> |
| T                  | Type of the table (list, one col table, two col table)                                          | list                    |
| L                  | Name of the last candidate in the table                                       | "Clinton Topp"              |
| -f                 | name of the first candidate (used when there are multiple elction tables per page) | -f "Bobbi Johnson"                                       |
| -n                 | keywords to match the name of the table (only used when you are not scraping from the first table in the page) | -n "Advisory Council District 7"                                        |
| -tn                | use this flag when want to give a custom name to the file insetad of using auto generated name based on electon name, `-tn` will override `-n` | -tn "My Custom Name"                                      |
| -o [OUTPUT\_PATH]  | Specify the location of the output file; default is out/ (optional)   | -o "./output/"                           |

The full command looks like this:

```bash
./ballotpedia_scraper.py "https://ballotpedia.org/City_elections_in_Detroit,_Michigan_(2021)#Community_advisory_council" list "Clinton Topp" -n "Advisory Council District 7" -f "Bobbi Johnson" -tn "Custom Name"
```

## Output<a id="sec-2-1"></a>

This will output to `ballotpedia_out/election_name.csv` where election_name is either the auto generated name or user specified name with `-tn` flag

## Options for `T` table type flag and examples
1. `Table`:
   
    Refers to the type of candidate table with several columns of candidate names     

   <https://ballotpedia.org/Virginia_House_of_Delegates_elections,_2021#General_election_candidates>
    ```bash
    ./ballotpedia_scraper.py "https://ballotpedia.org/Virginia_House_of_Delegates_elections,_2021#General_election_candidates" table "Robert Bloxom"
    ```
    <https://ballotpedia.org/City_elections_in_New_York,_New_York_(2021)#City_council>
    ```bash
    ./ballotpedia_scraper.py "https://ballotpedia.org/City_elections_in_New_York,_New_York_(2021)#City_council" table "Joe Borelli"
    ```
   We do not need any optional flag because we are scraping the first table in the webpage.
   However, we can use `-tn` to specify the name of the output file if we do not want the crawler to generate one based on the name of the election
   <br><br/>
2. `list`:

    Refers to the table format with just a list of candidates
    
    <https://ballotpedia.org/City_elections_in_New_York,_New_York_(2021)>
     ```bash
    ./ballotpedia_scraper.py "https://ballotpedia.org/City_elections_in_New_York,_New_York_(2021)" list "Devi Nampiaparampil" -f "Jumaane Williams" -n "Public Advocate"
    ```
    Note that `-f` is specified because we are NOT scraping the first table, so we need to tell the scraper from which name should we start looking
    
    The value of `-f` should always be the first candidate's name of the desired election table
    
    Note that `-n` is specified so the crawler can find the election name containing the keywords specified with `-n` and use that as the name of the file
    
    We can also not use `-n` and use `-tn` to manually input a desired file name
    <br/><br/>
    <https://ballotpedia.org/Mayoral_election_in_Seattle,_Washington_(2021)>
     ```bash
    ./ballotpedia_scraper.py "https://ballotpedia.org/Mayoral_election_in_Seattle,_Washington_(2021)" list "Bruce Harrell"
    ```
    Note that in this example, since we are scraping the first table, we do not need to specify the first candidate with `-f`. We also do not need to use `-n` because by default, the crawler uses the name of the first election appeared on the webpage as the name of the out file
    However, we can use `-tn` to manually specify a output file name
    <br></br>
3. `single-table`:
    
    This is the type of table that only has one column of candidates, unlike `table`
    
    Note that please always use `-tn` to specify the election name/output file name
   
    <https://ballotpedia.org/City_elections_in_Atlanta,_Georgia_(2021)#Candidates_and_results>
     ```bash
    ./ballotpedia_scraper.py "https://ballotpedia.org/City_elections_in_Atlanta,_Georgia_(2021)#Candidates_and_results" single-table "Jenne Shepherd" -tn "Atlanta City Council general election" -f "Michael Julian Bond"
    ```
    