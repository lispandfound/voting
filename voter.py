import meek
import roles
import votes

ROLES_JSON = "roles.json"


def main():
    committee_roles = roles.load_roles(ROLES_JSON)
    candidates, member_votes = votes.load_votes(committee_roles, MEMBERS_CSV, VOTES_CSV)
    disqualified_candidates = []
    for role, valid_votes in member_votes:
        elected = meek.meek_stv(
            candidates, role.number_of_positions, valid_votes, disqualified_candidates
        )
        print(f"Elected for {role.name}: {elected}")
        if not role.held_in_conjunction:
            disqualified_candidates.extend(c for c, _ in elected)
