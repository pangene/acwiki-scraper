import re
import sqlite3
import requests
from bs4 import BeautifulSoup

# I initially tried to filter out all the urls I got for the creatures from the 
# root_urls to speed up the process, but speed isn't really an issue + the 
# filter is kind of inaccurate.
SIMPLE_FILTER = False

VERSIONS = [
    'Animal_Crossing', 
    'Wild_World', 
    'City_Folk', 
    'New_Leaf', 
    'New_Horizons'
]

CREATURES = [
    'bugs', 
    'fish', 
    'deep-sea_creatures'
]

def get_name(url):
    """Returns the name of the animal given wiki url."""
    response = requests.get(url=url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('title')
    title = title.text
    name = title[:title.index('|') - 1]
    return name


def get_description(url, version):
    """Returns the description of the animal given wiki url and version."""
    response = requests.get(url=url)
    soup = BeautifulSoup(response.content, 'html.parser')
    game_heading = soup.find(id=f"In_{version}")
    if game_heading is None:
        return ''
    description = game_heading.findNext('p')
    # Some descriptions are formatted differently, contain an extra i tag
    while len(description.text) < 110:  
        description = description.findNext('p')
    description = description.text
    # If statements to account for weird italics on quotes (ie. missing/present)
    print(description[-1])
    while description[0] in ['"', ' ', '\n']:
        description = description[1:]
    while description[-1] in ['"', ' ', '\n']:
        description = description[:-1]
    return description


def get_all_urls(url, creature):
    """Returns a list containing all urls within the html of a wiki url."""
    response = requests.get(url=url)
    regex = r'/wiki/[A-Za-z_()]+'
    matches = re.findall(regex, response.text)
    no_duplicates = []
    [no_duplicates.append(x) for x in matches if x.lower() \
        not in [x.lower() for x in no_duplicates]]
    if SIMPLE_FILTER:
        no_duplicates = get_creature_urls(no_duplicates, creature)
    no_duplicates = ['https://animalcrossing.fandom.com' + url \
        for url in no_duplicates]
    return no_duplicates


def get_creature_urls(urls, creature):
    """Filters out a list of urls to only contain creature urls."""  # DOESN'T REALLY WORK
    if creature == 'deep-sea_creatures':
        creature = 'pascal'
    elif creature == 'bugs':
        creature = 'file'
    else:
        creature = 'pop'
    urls = urls[
        urls.index(f'/wiki/{creature.capitalize()}') + 1:\
        urls.index('/wiki/Deserted_island')]
    return urls


def construct_root_urls():
    """Constructs the root urls that should contain all creature urls."""
    root_urls = []
    for version in VERSIONS:
        for creature in CREATURES:
            if version not in ['New_Leaf', 'New_Horizons'] \
                and creature == 'deep-sea_creatures':
                continue
            url = f'https://animalcrossing.fandom.com/wiki/{creature}_({version})'
            root_urls.append((version, creature, url))
    return root_urls


def connect_to_database(database):
    """Connects to a database and returns the connection."""
    conn = sqlite3.connect(database)
    return conn


def save_to_database(connection):
    connection.commit()
    connection.close()


def create_creature_description_table(version, creature, url_list, connection):
    """Writes an SQL table to a database containing name, description."""
    c = connection.cursor()
    table_name = f'{version.lower()}_{creature}'
    c.execute(f'''DROP TABLE IF EXISTS {table_name}''')
    c.execute(f'''CREATE TABLE {table_name} (
                    name text PRIMARY KEY,
                    description text NOT NULL)''')
    for url in url_list:
        name = get_name(url)
        description = get_description(url, version)
        if name and len(description) > 30:
            print(name, description[:10], url)
            SQL_insert = f'''INSERT INTO {table_name} VALUES 
                            ({name}, {description})'''
            print(SQL_insert)
            try:
                c.execute(f'INSERT INTO {table_name} VALUES (?, ?)', (name, description))
            except sqlite3.IntegrityError:
                print(f'Found repeat: {name}')

def main():
    root_urls = construct_root_urls()
    '''potential_creature_urls is list composed of tuples
    each tuple (version, creature, [potential urls])'''
    potential_creature_urls = []
    for version, creature, url in root_urls:
        potential_creature_urls.append((version, creature, get_all_urls(url, creature)))
    conn = connect_to_database('test.db')
    create_creature_description_table(*potential_creature_urls[0], conn)
    save_to_database(conn)

def temp(url):
    name = get_name(url)
    description = get_description(url, 'New_Leaf')
    print(name, description)

if __name__ == '__main__':
    main()
    # temp('https://animalcrossing.fandom.com/wiki/Snail')
