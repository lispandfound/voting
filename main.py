import roles
import voting
import meek
import argparse
import pathlib
from collections import defaultdict


def main():
    parser = argparse.ArgumentParser(description="CompSoc voting tool.")
    parser.add_argument(
        "votes_csv", metavar="VOTES_CSV", help="Location of CSV file containing votes."
    )
    parser.add_argument(
        "members_csv",
        metavar="MEMBERS_CSV",
        help="Location of CSV file containing membership for the current year.",
    )
    parser.add_argument(
        "roles_json",
        metavar="ROLES_JSON",
        default="roles.json",
        help="Location of JSON file containing description of the roles in the comittee.",
    )
    args = parser.parse_args()
    members = voting.read_members(args.members_csv)
    candidates, votes = voting.read_votes(members, args.votes_csv)
    committee_roles = roles.load_roles(args.roles_json)
    disqualified = set()
    for role in committee_roles:
        # This handles the case where the particular role has no candidates
        # e.g for the 2019 secretary position. In this case we just skip the
        # election for this role.
        if not role.name not in candidates:
            continue
        print()
        print(f"Results for election of {role.name}:")
        try:
            role_candidates = candidates[role.name]
            elected = meek.meek_stv(
                role_candidates[role.name],
                # In the case where the number of canidates running is fewer the number of seats
                # we instead elect as many as possible (everyone except no confidence).
                # This occurred in the 2019 elections for equity officer.
                min(len(role_candidates) - 1, role.number_of_positions),
                votes[role.name],
                set() if role.held_in_conjunction else disqualified,
            )
        except ValueError as e:
            print(f"Could not elect a valid candidate!")
            print(
                f"Our candidates: {candidates[role.name]}, disqualified candidates: {disqualified}."
            )
            continue
        for i, candidate in enumerate(elected):
            print(f"{i + 1}. {candidate}")

        if "No Confidence" in elected:
            print("!!! No Confidence was elected !!!")
        if not role.held_in_conjunction:
            disqualified.update(e for e in elected if e != "No Confidence")


if __name__ == "__main__":
    main()
