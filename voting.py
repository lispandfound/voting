import re
import csv
from collections import defaultdict

USER_RE = r"[A-z]{3,4}\d{2,3}"
MEMBERS_USERNAME_COLUMN = "UC Username"
VOTES_USERNAME_COLUMN = "What is your UC usercode (abc123)"
POSITION_COL_RE = r"(.+)?(c|C)andidates\s+\[(.+)?\]"


def valid_usercode(code):
    """ Returns True if the given user code matches the USER_RE regex. This matches 3-4 alphabetical
    characters followed by 2-3 digits, e.g "jaf150" or "abcd23". """
    return isinstance(code, str) and re.match(USER_RE, code)


def read_members(members_fp):
    """ Read a set of members from the members csv file.
    Returns a set of every usercode in the members file. """
    with open(members_fp) as infile:
        members_reader = csv.DictReader(infile)
        return {
            member[MEMBERS_USERNAME_COLUMN].lower()
            for member in members_reader
            if valid_usercode(member[MEMBERS_USERNAME_COLUMN])
        }


def parse_position(col):
    """ Parse a candidate for a position into a candidate name
    i.e President Candidates [Foo Bar] -> Foo Bar"""
    pos = re.match(POSITION_COL_RE, col)
    if not pos:
        return None

    role = pos.group(1).strip()
    candidate = pos.group(3).replace("\t", " ")
    return role, candidate


def parse_vote(value):
    """ Parse a single vote for a single position as a list of preferences.
    e.g abc123 may make Foo Bar their number 1, 2 and 3 option as president.
    This would reflect in the CSV as "1;2;3" in the "President Candidates [Foo Bar]"
    column of the voting.csv. The parse_vote function would then turn "1;2;3" into the preference 1
    for Foo Bar (it always takes the highest preference allocated).

    Examples:
    >>> parse_vote('1;2;3')
    1
    """
    if not value:
        return None

    try:
        preferences = [int(p) for p in value.split(";")]
    except ValueError:
        return None

    return min(preferences)


def read_ballot(candidates, ballots, ballot):
    """ Read a single ballot from a given dictionary representing a single row
    of the ballots csv file.

    A single ballot is a single row in the voting csv file. It has a number of columns,

    Usercode column:: Matches MEMBERS_USERNAME_COLUMN in CSV header. Has a single entry representing
        the user's usercode
    Vote columns:: A bunch of columns that match POSITION_COL_RE and represent a list of preferences
        for a given candidate in a given position,
        e.g President Candidates [Foo Bar] might have a corresponding entry '1;2;3'.

    Takes in a dictionary of candidates, the dictionary holding all ballots, and the current ballot
    from the csv and then processes the ballot by:

    1. Iterating over each column in the ballot. This column is then parsed into a position
        and a candidate if it is a vote column.
        e.g the 'President Candidates [Foo Bar]' column becomes ('President', 'Foo Bar').
    2. Adding the candidate it represents to the set of candidates for that position.
        e.g 'Foo Bar' is added to the set candidates['President'].
    3. Parsing the preference indicated by the voter. Always takes the highest preference listed.
        e.g '1;2;3' becomes a vote with first preference,
            this is stored in parsed_ballot['President'][1] = 'Foo Bar'.
    4. All votes the user has made for all candidates is then added to the dictionary of ballots.
        e.g The vote ['Foo Bar', 'Baz', 'Bing'] is added to ballots['President']
            if the voter indicates 'Foo Bar', 'Baz' and 'Bing' in
            that preference order for the position.

    """
    parsed_ballot = defaultdict(dict)
    for col_name, value in ballot.items():
        pos = parse_position(col_name)
        if not pos:
            continue
        vote = parse_vote(value)
        position, candidate = pos
        candidates[position].add(candidate)
        if vote and vote not in parsed_ballot[position]:
            parsed_ballot[position][vote] = candidate
        elif vote in parsed_ballot[position]:
            parsed_ballot.pop(position)  # spoiled vote for the position

    for position, vote in parsed_ballot.items():
        ballots[position].append([v for (_, v) in sorted(vote.items())])


def read_ballots(members, ballots_fp):
    """ Read a list of ballots from the ballots csv file, taking care to only count each member once,
    and to only count ballots from members. """
    ballots = defaultdict(list)
    candidates = defaultdict(set)
    seen_voters = set()
    with open(ballots_fp) as infile:
        ballots_reader = csv.DictReader(infile)
        for ballot in ballots_reader:
            user_code = ballot[VOTES_USERNAME_COLUMN].lower()
            if user_code in members and user_code not in seen_voters:
                seen_voters.add(user_code)
                read_ballot(candidates, ballots, ballot)
    return candidates, ballots
