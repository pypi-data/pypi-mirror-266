from urllib.parse import unquote

def get_vanity_from_linkedin_url(profile_url):
    profile_url = profile_url.strip()
    profile_url = profile_url if profile_url.startswith(
        'http') else f'https://{profile_url}'
    url_parts = profile_url.split('/')
    li_vanity = False

    if 'linkedin.com/in/' in profile_url:
        li_vanity = parse_vanity_from_array(url_parts)
    elif 'linkedin.com/pub/' in profile_url:
        li_vanity = parse_vanity_from_array(url_parts, True)

    if li_vanity and len(li_vanity) > 0:
        return li_vanity

    return ''

def parse_vanity_from_array(arr, is_pub=False):
    if not is_pub:
        if len(arr) < 5:
            return False
        query = arr[4]
        vanity = query.split('?')[0]
    else:
        if len(arr) < 8:
            return False
        first_part = arr[7].split('?')[0]
        first_part = first_part.zfill(3)
        second_part = arr[6].zfill(2)
        third_part = arr[5] if arr[5] != '0' else ''

        vanity = f'{arr[4]}-{first_part}{second_part}{third_part}'

    if '%' in vanity:
        vanity = unquote(vanity)

    return vanity