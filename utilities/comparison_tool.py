from fuzzywuzzy import fuzz
import time
import re

PATTERN = re.compile(r'\D')


def compare_prospects(prospect: dict[str, str], potential_matches: dict[str, dict], verbose=False) -> str:
    """
    Compare the prospect to the potential matches
    :param prospect: prospect attributes in a dictionary
    :param potential_matches: dictionary of potential matches
    :param verbose: print the comparison results and delay
    :return: string of the match gid
    """
    normalized_prospect = {
        "name": f"{prospect["last name"]}, {prospect["first name"]} {prospect["middle name"]}",
        "name_alt": f"{prospect["last name"]}, {prospect["first name"]}",
        "birthday": '/'.join([prospect['mm'], prospect['dd'], prospect['yyyy']]).replace('//', ''),
        "address": f"{prospect['street 1']} {prospect['city']} {prospect['state']}",
        "phone": PATTERN.sub('', f"{prospect['phone area']} {prospect['phone number']}"),  # this might need [-10:
        "email": prospect['email'],
        "gender": '',
    }
    for match in potential_matches:
        scores = _compare_dicts(normalized_prospect, potential_matches[match])
        if verbose:
            print(normalized_prospect)
            print(potential_matches[match])
            print(scores, end='\n\n')
        if 100 in [scores['phone'], scores['email'], scores['address']]:
            if scores['name'] < 80 and scores['name_alt'] < 80:  # skip if the name is not a close match
                return 'skip'
            return match
    return 'new person'


def _compare_dicts(dict1: dict[str, str], dict2: dict[str, str]) -> dict[str, int]:
    """
    Compare two dictionaries using the fuzzywuzzy library
    :param dict1: dictionary of strings
    :param dict2: dictionary of strings with the same keys as dict1
    :return: dictionary of scores
    """
    scores = {}
    for key in dict1:
        if (dict1[key]
                and dict2[key]
                and dict1[key].strip()
                and dict2[key].strip()):
            scores[key] = fuzz.ratio(
                dict1[key].strip().lower(),
                dict2[key].strip().lower()
            )
        else:
            scores[key] = 0
    return scores
