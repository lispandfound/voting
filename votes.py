import csv
from collections import namedtuple, defaultdict
import re

CANDIDATE_RE = r'(.*)?candidates \[([^\]]+)\]'
UC_USERCODE = 'What is your UC usercode (abc123)'
MEMBER_UC_USERCODE = 'UC Username'


def parse_ballot(ballot_row):
    ''' Parse an individual user's ballot. The ballot_row is a csv row
    (dictionary mapping csv columns to values). The function iterates
    over the rows of the vote file and attempts to match each column
    to CANDIDATE_RE. If it can successfully do this, the function then
    extracts the position and the candidate from the column using the
    regex and then checks the value of the column. The value of the
    column should be either an integer or list (semicolon delimeted) of integers indicating
    the voters preference for a given candidate. If the preference is
    a list, e.g 1;2;3 the minimum or highest preference is assumed, so
    the preference would just be '1'.

    Args:
    - ballot_row :: CSV row, a dictionary mapping column names to values.

    Returns:
    - A dictionary mapping positions to the sorted list of voters preferences for each candidate. '''
    ballot = defaultdict(list)
    for col, preference in ballot_row.items():
        ballot_col = re.match(CANDIDATE_RE, col)
        if ballot_col and preference:
            position = ballot_col.group(1)
            candidate = ballot_col.group(2).replace('\t', ' ')
            ballot[position.strip()].append((min(int(p) for p in preference.split(';')), candidate))
    return {p: sorted(preference) for p, preference in ballot.items()}
    
def read_votes(members, vote_csv):
    ''' Read and interpret all valid member votes from the response
    csv file.

    Args:
    - members :: A set containing the valid member codes for voting.
    - vote_csv :: The CSV file for the votes.

    Returns:
    - A dictionary mapping position to a list of voter preferences for
      each candidate. '''
    position_votes = defaultdict(list)
    with open(vote_csv) as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            if row[UC_USERCODE].lower() not in members:
                continue
            ballot = parse_ballot(row)
            for position, preference in ballot.items():
                position_votes[position].append(preference)
    return position_votes

def read_members(members_csv):
    ''' Read in a list of members from the members.csv file. 

    Args:
    - members_csv :: The CSV file containing the list of members.

    Returns:
    - A set of all members. '''
    with open(members_csv) as infile:
        reader = csv.DictReader(infile)
        return {row[MEMBER_UC_USERCODE].lower() for row in reader}
