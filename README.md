# Introduction

This is a small Python webscraping script for the [Animal Crossing wiki](https://animalcrossing.fandom.com/wiki/Animal_Crossing_Wiki)

This scrapes the wiki for all creatures (bugs, fish, sea creatures) for all versions of Animal Crossing. For each version and each type of creature, it creates a SQL table named "version_creature[s]". All the SQL tables are stored in the dialogue.db file. The SQL tables are just 2-columns: name of the creature, and Blather's description of the creature when donating.

Some creatures are missing. This can be seen by counting the rows of each SQL table and comparing with how many creatures is supposed to be in that version's creature table. I'm not sure which creatures are missing, and it's only a couple for game (ie. AC gamecube has 40 bugs and fishes, my table has 39 bugs and fishes). I may add these in manually later if I have time to figure out which ones are missing, but the database for that will probably be in the blathers talkbot I made rather than this project.

A lot of the unreliability of this program is unavoidable, since the wiki itself is just edited by regular fans of the games and strict conformity is not maintained, so it's hard to have a clean procedure to getting the information needed.

This project is an accompaniment to my [blathers talkbot](https://github.com/pangene/blathers-talkbot-py). I needed the dialogue for all the creatures, and I didn't want to copy-and-paste them in manually (although that would've been WAY faster).

It was a fun little experience doing some webscraping, and I learned quite a bit.

# Detailed Look

Obviously, for the most-detailed examination of the functionality, read the code.

Basically, I have a function that identifies what I call "root_urls". The wikipedia page of these urls should contain every link of all the relevant creatures I need.

Using these root_urls, I then identify every single url in that webpage. Many of these urls do not connect to a creature's wikipedia page. I did try and make a simple filter to only have the creature wikipedia page, but it was too difficult considering the lack of uniformity.

Now, with the identified list of urls for each webpage, I construct the SQL tables. I scrape each url in the list to find the name of the creature and the description. Unrelated webpages should be ignored. However, some links use the same ids even though they aren't creature pages, so I manually blocked them in the FORBIDDEN_URLS list. I probably could've done this better, but it would've been more work than it was worth (although that could be said for this entire project).

That is essentially how this script functions.

# Improvements

* If I wanted to improve this and perhaps understand why I'm missing some animals, I think there is one big thing I can do: change the regex I use to identify all urls on the root_url html. I only include urls that follow the pattern [/wiki/blahblahblah]. This covers most urls, but obviously misses the ones that include the entire url link. Although I'm not sure if any of the links of that pattern would include creatures.

* Improve my filter. I go through a lot of unnecessary links. I didn't bother filtering because of how messy it was considering the lack of uniformity, but it would radically speed up the scraping.

* Just make things neater. For example, all urls are actually contained in a tuple that contains (version, creature, [list of urls or individual url]). This should've been its own class if I planned it out better.

I probably won't make most of these improvements since this was just a learning project. Frankly, manually creating the SQL tables would've been way faster and resistant to missing creatures. But, hey, it was fun I guess.
