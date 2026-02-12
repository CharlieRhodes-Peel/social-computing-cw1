# Social Computing CW1

- Training a model on 100k ratings from ~1000 different users and idk how many items but quite a few
- Then using that model to predict ratings for items that users haven't rated yet. Only does all the backend data base stuff

## General Thought process around flow of the program

- Will be tackling this one with a U2U approach (user-to-user)
- Should first load all of the csv file stuff into an SQL data base just so can query it better (i think)
- Then should create lookup tables for everything (this may not be needed if can just do it with SQL)
- Should then **PRE-COMPUTE** the cosine simularity of each user with every other user (assuming they share at least 2-3 ratings (for optimasation purposes))
- THEN can predict everything using the lookups of the cosine simularities that are already calculated!

## Task list for me to check progress

- [x] SQLite3 table of the data
- [x] Lookup table for users and list of items they have rated or something
- [x] Lookup table for items and users that have rated them (i think i need this?)
- [x] Precomputing cosine simularities between all users and storing results somewhere
- [ ] For items without ratings by a user, find a neighbour of similar users to this user
- [ ] Then calculate an average score
- [ ] Do this for all and write to a file! :) DONE!!!!
