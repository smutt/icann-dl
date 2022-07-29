#!/usr/bin/env python3

#  The file is part of the icann-dl Project.
#
#  The icann-dl Project is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  The icann-dl Project is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#  Copyright (C) 2022, Andrew McConachie, <andrew.mcconachie@icann.org>

import argparse
import os
import stat
import re
import requests
from bs4 import BeautifulSoup
from urllib3 import util as Util
from datetime import datetime, date
import groups

base_dir = '/var/www/htdocs/icann-hamster.nl/ham/'

exclude = []
exclude.append(re.compile('.*/didp-response-process-29oct13-en\.pdf$'))
exclude.append(re.compile('.*/registrar-billing-faq-21dec21-en\.pdf$'))
exclude.append(re.compile('.*/gdd-ops-handbook-registry-operators-15aug18-en\.pdf$'))
exclude.append(re.compile('.*/rsep-process-workflow-14jun19-en\.pdf$'))
exclude.append(re.compile('.*/mosapi-specification\.pdf$'))

# Basic logging to stdout
def logit(s):
  print(datetime.isoformat(datetime.utcnow()) + ' ' + s.strip())

# Grab a file and write to disk
def download(uri, fname):
  if os.path.exists(fname):
    return

  logit(uri + ' ' + fname)
  try:
    req = requests.get(uri,stream=True)
    if req.status_code == 200:
      with open(fname, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
          if chunk: # filter out keep-alive new chunks
            f.write(chunk)
      os.chmod(fname, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH) # 0644
    else:
      logit("err:dl_bad_response:" + uri)
  except requests.RequestException:
    logit("err:req_exception:" + uri)


# Grab links in tags matching regex
# Returns deduplicated list of links
def get_links(URI, regex, tags=['a', 'href']):
  def is_excluded(s): # Should we exclude this link?
    for pattern in exclude:
      if pattern.match(s):
        return True
    return False

  links = []
  url_t = Util.parse_url(URI)

  try:
    req = requests.get(URI)
  except requests.RequestException:
    logit("err:req_exception:" + URI)
    return []

  if req.status_code == 200:
    soup = BeautifulSoup(req.text, 'html.parser')
    for tag in soup.find_all(tags[0]):
      link = tag.get(tags[1])
      if link is None:
        continue
      if not is_excluded(link):
        for reg in regex:
          if reg.match(link):
            link = link.split('?')[0] # Strip any trailing garbage
            if Util.parse_url(link).host is None:
              links.append(url_t.scheme + '://' + url_t.host + link)
            elif len(Util.parse_url(link).host) < len('icann.org'): # Relative path missing leading /
              links.append(url_t.scheme + '://' + url_t.host + '/' + link)
            else:
              links.append(link)
  return list(dict.fromkeys(links))

# BEGIN EXECUTION
ap = argparse.ArgumentParser(description='Download PDFs from icann.org')
ap.add_argument('-g', '--group', type=str, action='store', default='all',
                  choices=groups.groups.keys(), help='Selected group to download')
ARGS = ap.parse_args()

for gr in groups.groups:
  if ARGS.group != 'all' and ARGS.group != gr:
    continue

  existing = {} # Dict of group files on local disk
  for _, _, files in os.walk(base_dir + groups.groups[gr]['path']):
    for ff in files:
      existing[ff] = True

  if gr == 'icann_cor':
    for sub_dir,URI in groups.groups[gr]['sub_dir'].items():
      if sub_dir == str(date.today().year):
        for ll in get_links(URI, groups.groups[gr]['regex']):
          if ll.endswith('.pdf'): # 2012 and 2013 sometimes add another level of redirection
            if Util.parse_url(ll).path.split('/')[-1] not in existing:
              download(ll, base_dir + groups.groups[gr]['path'] + '/' + sub_dir + '/' + ll.split('/')[-1])
          else:
            for mm in get_links(ll, groups.groups[gr]['regex']):
              if Util.parse_url(mm).path.split('/')[-1] not in existing:
                download(mm, base_dir + groups.groups[gr]['path'] + '/' + sub_dir + '/' + mm.split('/')[-1])

  elif gr == 'gac':
    for page in get_links(groups.groups[gr]['uri'], groups.groups[gr]['option_regex'], ['option', 'value']):
      for ll in get_links(page, groups.groups[gr]['regex']):
        if Util.parse_url(ll).path.split('/')[-1] not in existing:
          download(ll, base_dir + groups.groups[gr]['path'] + '/' + ll.split('/')[-1])

  else:
    for ll in get_links(groups.groups[gr]['uri'], groups.groups[gr]['regex']):
      if Util.parse_url(ll).path.split('/')[-1] not in existing:
        download(ll, base_dir + groups.groups[gr]['path'] + '/' + ll.split('/')[-1])
