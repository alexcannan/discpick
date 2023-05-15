"""
reads your discogs collection and picks a random album
"""

import argparse
import os
import random
import tempfile

from ascii_magic import AsciiArt
from colorama import Style
import discogs_client
import requests


user_token = os.environ['DISCOGS_USER_TOKEN']

parser = argparse.ArgumentParser(description='Pick a random album from your Discogs collection')
parser.add_argument('username', type=str, help='your Discogs username')
args = parser.parse_args()

d = discogs_client.Client('discpick/0.0', user_token=user_token)

c = d.user(args.username).collection_folders[0]

n_choices = (c.releases.pages-1) * c.releases.per_page + len(c.releases.page(c.releases.pages))
if n_choices <= 0:
    print(f"{args.username} has no releases in their collection!")
    exit(1)
rchoice = random.randint(0, n_choices-1)
rpage, rindex = divmod(rchoice, c.releases.per_page)
rdisc = c.releases.page(rpage)[rindex]

discinfo = rdisc.data['basic_information']

with tempfile.NamedTemporaryFile() as t:
    params = {'User-Agent': 'discpick/0.0', 'token': user_token}
    with requests.get(discinfo['cover_image'], params=params, headers=params, stream=True) as r:
        r.raise_for_status()
        with open(t.name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    my_art = AsciiArt.from_image(t.name)
    my_art.to_terminal(columns=80, width_ratio=2.5)

print(Style.BRIGHT+', '.join(a['name'] for a in discinfo['artists']), '-', discinfo['title'], f"({discinfo['year']})")
