from fuzzywuzzy import fuzz
import re

PATTERN = re.compile(r'\D')


def compare_prospects(prospect: dict[str, str], potential_matches: dict[str, dict]) -> str:
    """
    Compare the prospect to the potential matches
    :param prospect: prospect attributes in a dictionary
    :param potential_matches: dictionary of potential matches
    :return:
    """
    normalized_prospect = {
            "name": f"{prospect["last name"]}, {prospect["first name"]} {prospect["middle name"]}".strip(),
            "name_alt": f"{prospect["last name"]}, {prospect["first name"]}".strip(),
            "birthday": '/'.join([prospect['mm'], prospect['dd'], prospect['yyyy']]).strip().replace('//', ''),
            "address": f"{prospect['street 1']} {prospect['city']} {prospect['state']} {prospect['zipcode'][:5]}".strip(),
            "phone": PATTERN.sub('', f"{prospect['phone area']} {prospect['phone number']}"),  # this might need [-10:
            "email": prospect['email'].strip(),
            "gender": '',
    }
    for match in potential_matches:
        scores = _compare_dicts(normalized_prospect, potential_matches[match])
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
