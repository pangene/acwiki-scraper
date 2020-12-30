import logging
import re
import sqlite3
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# I initially tried to filter out all the urls I got for the creatures from the 
# root_urls to speed up the process, but speed isn't really an issue + the 
# filter is kind of inaccurate.
SIMPLE_FILTER = False

# urls that escape me despite the best of my abilities...
FORBIDDEN_URLS = [
    'https://animalcrossing.fandom.com/wiki/Bugs',
    'https://animalcrossing.fandom.com/wiki/Isabelle',
    'https://animalcrossing.fandom.com/wiki/Blathers',
    'https://animalcrossing.fandom.com/wiki/Pascal',
    'https://animalcrossing.fandom.com/wiki/Bug',
    'https://animalcrossing.fandom.com/wiki/Tree',
    'https://animalcrossing.fandom.com/wiki/Flower',
    'https://animalcrossing.fandom.com/wiki/Bug_Off',
    'https://animalcrossing.fandom.com/wiki/Flick',
    'https://animalcrossing.fandom.com/wiki/River',
    'https://animalcrossing.fandom.com/wiki/Fishing_Tourney',
    'https://animalcrossing.fandom.com/wiki/Net',  # This one's actually handled, but not well
    'https://animalcrossing.fandom.com/wiki/Trash',
    'https://animalcrossing.fandom.com/wiki/Waterfall',
    'https://animalcrossing.fandom.com/wiki/Fishing_Rod'
]

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
    if url in FORBIDDEN_URLS:
        return ''
    response = requests.get(url=url)
    soup = BeautifulSoup(response.content, 'html.parser')
    game_heading = soup.find(id=f"In_{version}")
    if game_heading is None:
        return ''
    try:
        description = game_heading.findNext('p')
        # Some descriptions are formatted differently, contain an extra p tag
        while len(description.text) < 120:
            description = description.findNext('p')
    except AttributeError:
        logging.warning('Error while getting description')
        logging.warning(url)
        logging.warning(version)
        return ''
    description = description.text
    # If statements to account for weird italics on quotes (ie. missing/present)
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
    c.execute(f'''DROP TABLE IF EXISTS "{table_name}"''')
    c.execute(f'''CREATE TABLE "{table_name}" (
                    name text PRIMARY KEY,
                    description text NOT NULL)''')
    for url in url_list:
        name = get_name(url)
        description = get_description(url, version)
        if name and len(description) > 50:
            logging.info(table_name)
            logging.info(name)
            logging.info(description[:30])
            logging.info(url)
            # logging.debug(f'INSERT INTO {table_name} VALUES ({name}, {description})')
            try:
                c.execute(f'INSERT INTO "{table_name}" VALUES (?, ?)',
                    (name, description))
            except sqlite3.IntegrityError:
                logging.info(f'Found repeat: {name}')
            except sqlite3.OperationalError as e:
                logging.debug('Error inserting into table probably.')
                logging.warning(e)
                logging.warning(f'INSERT INTO "{table_name}" VALUES ({name}, {description})')

def main():
    global conn
    root_urls = construct_root_urls()
    '''potential_creature_urls is list composed of tuples
    each tuple (version, creature, [potential urls])'''
    potential_creature_urls = []
    for version, creature, url in root_urls:
        potential_creature_urls.append((version, creature, get_all_urls(url, creature)))
    conn = connect_to_database('dialogue.db')
    for version, creature, url_list in potential_creature_urls:
        create_creature_description_table(version, creature, url_list, conn)
    save_to_database(conn)

def get(url, version):
    name = get_name(url)
    description = get_description(url, 'New_Leaf')
    print(name, description)

if __name__ == '__main__':
    main()
    # temp('https://animalcrossing.fandom.com/wiki/Snail')
