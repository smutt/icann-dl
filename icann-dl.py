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

import os
import stat
import re
import requests
from bs4 import BeautifulSoup

base_dir = '/home/smutt/www/depht.com/icann/pubs/'

groups = {}
groups['ssac'] = {}
groups['ssac']['uri'] = 'https://www.icann.org/groups/ssac/documents'
groups['ssac']['regex'] = []
groups['ssac']['regex'].append(re.compile('.*/groups/ssac/documents/sac-.*\.pdf$'))
groups['ssac']['regex'].append(re.compile('.*/system/files/files/sac-.*\.pdf$'))

groups['ssac_cor'] = {}
groups['ssac_cor']['uri'] = 'https://www.icann.org/groups/ssac/documents-correspondence'
groups['ssac_cor']['regex'] = []
groups['ssac_cor']['regex'].append(re.compile('.*/system/files/files/ssac2.*\.pdf$'))

groups['rssac'] = {}
groups['rssac']['uri'] = 'https://www.icann.org/groups/rssac/documents'
groups['rssac']['regex'] = []
groups['rssac']['regex'].append(re.compile('.*/system/files/files/.*rssac-.*\.pdf$'))
groups['rssac']['regex'].append(re.compile('^/en/groups/rssac/rssac-iana-stewardship-transition-08may14-en.pdf$'))

groups['octo'] = {}
groups['octo']['uri'] = 'https://www.icann.org/resources/pages/octo-publications-2019-05-24-en'
groups['octo']['regex'] = []
groups['octo']['regex'].append(re.compile('.*/octo-.*\.pdf$'))

groups['octo_com'] = {}
groups['octo_com']['uri'] = 'https://www.icann.org/resources/pages/octo-commissioned-documents-2020-11-05-en'
groups['octo_com']['regex'] = []
groups['octo_com']['regex'].append(re.compile('.*/system/files/files/.*\.pdf$'))

groups['ge'] = {}
groups['ge']['uri'] = 'https://www.icann.org/en/government-engagement/publications?page=1'
groups['ge']['regex'] = []
groups['ge']['regex'].append(re.compile('.*/en/files/government-engagement-ge/.*\.pdf$'))

groups['rzerc'] = {}
groups['rzerc']['uri'] = 'https://www.icann.org/en/rzerc#documents'
groups['rzerc']['regex'] = []
groups['rzerc']['regex'].append(re.compile('.*/uploads/ckeditor/rzerc-0.*\.pdf$'))

exclude = []
exclude.append('/en/system/files/files/didp-response-process-29oct13-en.pdf')
exclude.append('https://www.icann.org/en/system/files/files/registrar-billing-faq-21dec21-en.pdf')
exclude.append('/en/system/files/files/gdd-ops-handbook-registry-operators-15aug18-en.pdf')
exclude.append('/mosapi-specification.pdf')

# Grab a file and write to disk
def download(uri, fname):
  req = requests.get(uri,stream=True)
  if req.status_code == 200:
    with open(fname, 'wb') as f:
      for chunk in req.iter_content(chunk_size=1024):
        if chunk: # filter out keep-alive new chunks
          f.write(chunk)
  os.chmod(fname, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH) # 0644


for gr in groups:
  req = requests.get(groups[gr]['uri'], data=None)
  if req.status_code == 200:
    links = []
    soup = BeautifulSoup(req.text, 'html.parser')
    for link in soup.find_all('a'):
      href = link.get('href')
      if href is None:
        continue
      if href.endswith('.pdf'):
        #print(href)
        for reg in groups[gr]['regex']:
          if reg.match(href):
            if not href in exclude:
              if href.startswith('https://'):
                links.append(href)
              else:
                links.append('https://www.icann.org' + href)

    for ll in links:
      fname = base_dir + gr + '/' + ll.split("/")[-1]
      if not os.path.exists(fname):
        print(ll + ' ==> ' + fname)
        download(ll, fname)
