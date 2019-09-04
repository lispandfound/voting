from collections import Counter
import math


def meek_stv_round(candidates, keep_values, votes):
    """ Compute the results of one round of Meek STV voting. Keep values
    distribute a vote to mutliple preferences equitably. To illustrate how this
    works consider the vote ADB where A has keep factor 80%, D has keep factor
    20% and B has keep factor 100%:

    A gets 0.8 votes              (80% of one vote)
    D gets 0.2*0.2 = 0.04 votes   (20% of the remaining vote)
    B gets 0.2*0.8*1 = 0.16 votes (100% of the remaining vote)

    This process is computed for each vote in the set of votes and tally of
    everyone's votes is returned. """
    candidate_votes = Counter()
    for vote in votes:
        vote_fraction = 1
        for candidate in vote:
            candidate_votes[candidate] += keep_values[candidate] * vote_fraction
            vote_fraction *= 1 - keep_values[candidate]
    return candidate_votes


def meek_stv(candidates, seats, votes, disqualified=None):
    """ Run a Meek STV election among the candidates for the given number of seats and votes.
    Meek STV is an iterative voting system that attempts to ensure three things,

    1. All votes are considered equally, regardless of if their main preference
       is elected or not.
    2. The outcome of the election most accurately portrays the preferences of
       the voting population.
    3. Voters need to know nothing of how meek stv works to use it.

    Meek STV achieves (1), (2) and (3) by implementing ranked choice voting with
    dynamic election quotas and keep values. The quota is the minimum number of
    votes required to elect a candidate to an available seat, and the keep
    values indicate how much of a preference is allocated to a given candidate
    on a given ballot. The basic algorithm is as follows:

    1. Initialise all keep values to 1
    2. While we haven't elected enough candidates
    3. Compute a quota based on how many votes for uneliminated candidates
       remain, the seats and the total votes.
    4. Run a single round of Meek STV (see meek_stv_round).
    5. Elect all candidates whose total fractional votes exceeds the quota computed in (3).
       (a) For any candidates who are elected compute the keep factor to be
           proportion that they are over the quota.
    6. If some seats remain unfilled eliminate the weakest candidate (setting
    their keep factor to 0 stops meek_stv_round from keeping any of their
    preferences).

    The rational behind 5. (a) is that it ensures the whole preference expressed
    by the voter is carried regardless of whether their first choice is elected
    or not. If the first choice is not elected then that preference is
    distributed among the other candidates lower on the ballot, and if they
    are elected the portion of that voter's ballot that would not change the
    outcome is redistributed among the remaining candidates. This is the extra
    info that Meek STV brings to the table. """
    keep_values = {c: 1 for c in candidates}

    if disqualified:
        for candidate in disqualified:
            keep_values[candidate] = 0

    exhausted_votes = 0
    n = len(votes)
    while True:
        results = meek_stv_round(candidates, keep_values, votes)
        quota = (n - exhausted_votes) / (seats + 1)
        elected = {}
        for candidate, vote_count in results.items():
            if vote_count >= quota:
                elected[candidate] = vote_count
                keep_values[candidate] *= quota / vote_count
        if len(elected) >= seats and all(
            math.isclose(v, quota, rel_tol=1e-6) for c, v in elected.items()
        ):
            return elected

        if not elected:
            minimum_candidate, _ = min(
                ((c, v) for (c, v) in results.items() if keep_values[c] != 0),
                key=lambda cv: cv[1],
            )
            keep_values[minimum_candidate] = 0
        exhausted_votes = n - sum(results.values())


if __name__ == "__main__":
    candidates = ["Alice", "Bob", "Chris", "Don", "Eric"]
    votes = (
        [["Alice", "Bob", "Chris"]] * 28
        + [["Bob", "Alice", "Chris"]] * 26
        + [["Chris"]] * 3
        + [["Don"]] * 2
        + [["Eric"]]
    )
    seats = 3
    elected = meek_stv(candidates, seats, votes)
    print(elected)
