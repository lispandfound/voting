import roles
import voting
import meek
import argparse
import pathlib

def main():
    parser = argparse.ArgumentParser(description='CompSoc voting tool.')
    parser.add_argument('votes_csv', metavar="VOTES_CSV", help='Location of CSV file containing votes.')
    parser.add_argument('members_csv', metavar="MEMBERS_CSV", help='Location of CSV file containing membership for the current year.')
    parser.add_argument('roles_json', metavar='ROLES_JSON', default='roles.json', help='Location of JSON file containing description of the roles in the comittee.')
    args = parser.parse_args()
    members = voting.read_members(args.members_csv)
    candidates, votes = voting.read_votes(members, args.votes_csv)
    committee_roles = roles.load_roles(args.roles_json)
    disqualified = set()
    for role in committee_roles:
        print()
        print(f'Results for election of {role.name}:')
        try:
            elected = meek.meek_stv(candidates[role.name], role.number_of_positions, votes[role.name], disqualified)
        except ValueError as e:
            print(f'Could not elect a valid candidate!')
            print(f'Our candidates: {candidates[role.name]}, disqualified candidates: {disqualified}.')
            print(e)
            continue
        for i, candidate in enumerate(elected):
            print(f'{i + 1}. {candidate}')

        if 'No Confidence' in elected:
            print('!!! No Confidence was elected !!!')
        print(f'{role.name} may not be held in conjunction with any other role, eliminating elected candidates from further elections...')
        if not role.held_in_conjunction:
            disqualified.update(e for e in elected if e != 'No Confidence')


if __name__ == '__main__':
    main()
