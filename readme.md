# CompSoc Voting Script

This program manages the voting for CompSoc elections, using output from the Google Form.

```
$ python main.py -h
usage: main.py [-h] VOTES_CSV MEMBERS_CSV ROLES_JSON

CompSoc voting tool.

positional arguments:
  VOTES_CSV    Location of CSV file containing votes.
  MEMBERS_CSV  Location of CSV file containing membership for the current
               year.
  ROLES_JSON   Location of JSON file containing description of the roles in
               the comittee.

optional arguments:
  -h, --help   show this help message and exit
```

## Key Features

1. [STV](https://en.wikipedia.org/wiki/STV) ranked choice voting (using [Meek's Method](https://www.researchgate.net/publication/31499523_Algorithm_123_Single_Transferable_Vote_by_Meek's_Method) to count surplus votes).
2. Validation of votes to ensure duplicate votes are not counted, and that only members votes are counted.
3. Extensibility for new roles, with the ability to detect if roles may be held in conjunction with any other roles.
4. CLI for interacting with all these elements.

## Technical Documentation

See the corresponding modules, all functions should be documented in thorough detail including on things like the method used to count votes, how votes are parsed, edges cases, and exceptions.
