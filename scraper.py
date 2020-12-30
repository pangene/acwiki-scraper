import re
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

def get_description(url, version):
    '''Returns the description of the animal given wiki url and version.'''
    response = requests.get(url=url)
    soup = BeautifulSoup(response.content, 'html.parser')
    game_heading = soup.find(id=f"In_{version}")
    if game_heading is None:
        return ''
    description = game_heading.findNext('i').findNext('i')
    if len(description.text) < 15:
        description = description.findNext('i')
    return description.text

def get_creature_urls(urls, creature):
    '''Filters out a list of urls to only contain creature urls.'''  # DOESN'T REALLY WORK
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

def get_all_urls(url, creature):
    '''Returns a list containing all urls within the html of a wiki url.'''
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

def construct_root_urls():
    '''Constructs the root urls that should contain all creature urls.'''
    root_urls = []
    for version in VERSIONS:
        for creature in CREATURES:
            if version not in ['New_Leaf', 'New_Horizons'] \
                and creature == 'deep-sea_creatures':
                continue
            url = f'https://animalcrossing.fandom.com/wiki/{creature}_({version})'
            root_urls.append((version, creature, url))
    return root_urls

def main():
    root_urls = construct_root_urls()
    print(root_urls)
    # potential_creature_urls is list composed of tuples
    # each tuple (version, creature, [potential urls])
    potential_creature_urls = []
    for version, creature, url in root_urls:
        potential_creature_urls.append((version, creature, get_all_urls(url, creature)))
    print(len(potential_creature_urls[0][2]))


if __name__ == '__main__':
    main()
