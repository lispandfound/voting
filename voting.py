import re
import csv
from collections import defaultdict
import unicodedata

USER_RE = r"[A-z]{3,4}\d{2,3}"
MEMBERS_USERNAME_COLUMN = "UC Username"
VOTES_USERNAME_COLUMN = "What is your UC usercode (abc123)"
POSITION_COL_RE = r"(.+)?(c|C)andidates\s+\[(.+)?\]"


def valid_usercode(code):
    return isinstance(code, str) and re.match(USER_RE, code)


def read_members(members_fp):
    with open(members_fp) as infile:
        members_reader = csv.DictReader(infile)
        return {
            member[MEMBERS_USERNAME_COLUMN].lower()
            for member in members_reader
            if valid_usercode(member[MEMBERS_USERNAME_COLUMN])
        }


def parse_position(col):
    pos = re.match(POSITION_COL_RE, col)
    if not pos:
        return None

    role = pos.group(1).strip()
    candidate = pos.group(3).replace("\t", " ")
    return role, candidate


def maybe_int(string):
    try:
        return int(string)
    except ValueError:
        return None


def parse_vote(value):
    if not value:
        return None

    preferences = [maybe_int(p) for p in value.split(";")]

    if not all(preferences):
        return None

    return min(preferences)


def read_vote(candidates, votes, vote):
    parsed_vote = defaultdict(dict)
    for col_name, value in vote.items():
        pos = parse_position(col_name)
        if not pos:
            continue
        vote = parse_vote(value)
        position, candidate = pos
        candidates[position].add(candidate)
        if vote and vote not in parsed_vote[position]:
            parsed_vote[position][vote] = candidate
        elif vote in parsed_vote[position]:
            parsed_vote.pop(position)  # spoiled ballot for the position

    for position, vote in parsed_vote.items():
        votes[position].append([v for (_, v) in sorted(vote.items())])


def read_votes(members, votes_fp):
    votes = defaultdict(list)
    candidates = defaultdict(set)
    seen_voters = set()
    with open(votes_fp) as infile:
        votes_reader = csv.DictReader(infile)
        for vote in votes_reader:
            user_code = vote[VOTES_USERNAME_COLUMN].lower()
            if user_code in members and user_code not in seen_voters:
                seen_voters.add(user_code)
                read_vote(candidates, votes, vote)
    return candidates, votes
