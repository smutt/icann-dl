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

base_dir = '/var/www/htdocs/icann-hamster.nl/ham/'

exclude = []
exclude.append(re.compile('.*/didp-response-process-29oct13-en\.pdf$'))
exclude.append(re.compile('.*/registrar-billing-faq-21dec21-en\.pdf$'))
exclude.append(re.compile('.*/gdd-ops-handbook-registry-operators-15aug18-en\.pdf$'))
exclude.append(re.compile('.*/rsep-process-workflow-14jun19-en\.pdf$'))
exclude.append(re.compile('.*/mosapi-specification\.pdf$'))

groups = {}
groups['ssac'] = {}
groups['ssac']['path'] = 'soac/ssac/reports'
groups['ssac']['uri'] = 'https://www.icann.org/groups/ssac/documents'
groups['ssac']['regex'] = []
groups['ssac']['regex'].append(re.compile('.*/groups/ssac/documents/sac-.*\.pdf$'))
groups['ssac']['regex'].append(re.compile('.*/system/files/files/sac-.*\.pdf$'))

groups['ssac_cor'] = {}
groups['ssac_cor']['path'] = 'soac/ssac/cor'
groups['ssac_cor']['uri'] = 'https://www.icann.org/groups/ssac/documents-correspondence'
groups['ssac_cor']['regex'] = []
groups['ssac_cor']['regex'].append(re.compile('.*/system/files/files/ssac2.*\.pdf$'))

groups['rssac'] = {}
groups['rssac']['path'] = 'soac/rssac/pub'
groups['rssac']['uri'] = 'https://www.icann.org/groups/rssac/documents'
groups['rssac']['regex'] = []
groups['rssac']['regex'].append(re.compile('.*/system/files/files/.*rssac-.*\.pdf$'))
#groups['rssac']['regex'].append(re.compile('^/en/groups/rssac/rssac-iana-stewardship-transition-08may14-en.pdf$'))

groups['octo'] = {}
groups['octo']['path'] = 'icann/octo/pub'
groups['octo']['uri'] = 'https://www.icann.org/resources/pages/octo-publications-2019-05-24-en'
groups['octo']['regex'] = []
groups['octo']['regex'].append(re.compile('.*/octo-.*\.pdf$'))

groups['octo_com'] = {}
groups['octo_com']['path'] = 'icann/octo/com'
groups['octo_com']['uri'] = 'https://www.icann.org/resources/pages/octo-commissioned-documents-2020-11-05-en'
groups['octo_com']['regex'] = []
groups['octo_com']['regex'].append(re.compile('.*/system/files/files/.*\.pdf$'))

groups['ge'] = {}
groups['ge']['path'] = 'icann/ge/pub'
groups['ge']['uri'] = 'https://www.icann.org/en/government-engagement/publications?page=1'
groups['ge']['regex'] = []
groups['ge']['regex'].append(re.compile('.*/en/files/government-engagement-ge/.*\.pdf$'))

groups['ge_gac'] = {}
groups['ge_gac']['path'] = 'icann/ge/gac'
groups['ge_gac']['uri'] = 'https://gac.icann.org/activity/bi-monthly-report-icann-gse-ge-governments-and-igos-engagement-activities'
groups['ge_gac']['regex'] = []
groups['ge_gac']['regex'].append(re.compile('.*/reports/public/.*\.pdf$'))

groups['rzerc'] = {}
groups['rzerc']['path'] = 'soac/rzerc/pub'
groups['rzerc']['uri'] = 'https://www.icann.org/en/rzerc#documents'
groups['rzerc']['regex'] = []
groups['rzerc']['regex'].append(re.compile('.*/uploads/ckeditor/rzerc-0.*\.pdf$'))

groups['icann_cor'] = {}
groups['icann_cor']['path'] = 'icann/cor'
groups['icann_cor']['sub_dir'] = {} # Before 2003 there are no PDFs
groups['icann_cor']['sub_dir']['2003'] = 'https://www.icann.org/resources/pages/2003-2012-10-11-en'
groups['icann_cor']['sub_dir']['2004'] = 'https://www.icann.org/resources/pages/2004-2012-10-11-en'
groups['icann_cor']['sub_dir']['2005'] = 'https://www.icann.org/resources/pages/2005-2012-10-11-en'
groups['icann_cor']['sub_dir']['2006'] = 'https://www.icann.org/resources/pages/2006-2012-10-11-en'
groups['icann_cor']['sub_dir']['2007'] = 'https://www.icann.org/resources/pages/2007-2012-10-11-en'
groups['icann_cor']['sub_dir']['2008'] = 'https://www.icann.org/resources/pages/2008-2012-10-11-en'
groups['icann_cor']['sub_dir']['2009'] = 'https://www.icann.org/resources/pages/2009-2012-10-11-en'
groups['icann_cor']['sub_dir']['2010'] = 'https://www.icann.org/resources/pages/2010-2012-10-11-en'
groups['icann_cor']['sub_dir']['2011'] = 'https://www.icann.org/resources/pages/2011-2012-02-25-en'
groups['icann_cor']['sub_dir']['2012'] = 'https://www.icann.org/resources/pages/2012-2013-01-10-en'
groups['icann_cor']['sub_dir']['2013'] = 'https://www.icann.org/resources/pages/2013-2014-01-24-en'
groups['icann_cor']['sub_dir']['2014'] = 'https://www.icann.org/resources/pages/2014-2014-01-24-en'
groups['icann_cor']['sub_dir']['2015'] = 'https://www.icann.org/resources/pages/correspondence-2015'
groups['icann_cor']['sub_dir']['2016'] = 'https://www.icann.org/resources/pages/correspondence-2016'
groups['icann_cor']['sub_dir']['2017'] = 'https://www.icann.org/resources/pages/correspondence-2017'
groups['icann_cor']['sub_dir']['2018'] = 'https://www.icann.org/resources/pages/correspondence-2018'
groups['icann_cor']['sub_dir']['2019'] = 'https://www.icann.org/resources/pages/correspondence-2019'
groups['icann_cor']['sub_dir']['2020'] = 'https://www.icann.org/resources/pages/correspondence-2020'
groups['icann_cor']['sub_dir']['2021'] = 'https://www.icann.org/resources/pages/correspondence-2021'
groups['icann_cor']['sub_dir']['2022'] = 'https://www.icann.org/resources/pages/correspondence-2022'
groups['icann_cor']['regex'] = []
groups['icann_cor']['regex'].append(re.compile('.*/correspondence/.*\.pdf$'))
groups['icann_cor']['regex'].append(re.compile('.*/system/files/files/.*\.pdf$'))
groups['icann_cor']['regex'].append(re.compile('^/en/news/correspondence/.*-to-.*-en$'))

groups['icann_ext'] = {}
groups['icann_ext']['path'] = 'icann/ext'
groups['icann_ext']['uri'] = 'https://www.icann.org/en/government-engagement/submissions-to-external-bodies'
groups['icann_ext']['regex'] = []
groups['icann_ext']['regex'].append(re.compile('.*/en/files/government-engagement-ge/.*\.pdf$'))

groups['gac'] = {}
groups['gac']['path'] = 'soac/gac/com'
groups['gac']['uri'] = 'https://gac.icann.org/contentMigrated/icann1-singapore-communique'
groups['gac']['option_regex'] = []
groups['gac']['option_regex'].append(re.compile('^/contentMigrated/icann.*-communique$'))
groups['gac']['regex'] = []
groups['gac']['regex'].append(re.compile('^.*/.*communique.*\.pdf[\?language_id.*]?', flags=re.ASCII | re.IGNORECASE))

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
    logit("err:req_exception:" + uri)
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
                  choices=groups.keys(), help='Selected group to download')
ARGS = ap.parse_args()

for gr in groups:
  if ARGS.group != 'all' and ARGS.group != gr:
    continue

  existing = {} # Dict of group files on local disk
  for _, _, files in os.walk(base_dir + groups[gr]['path']):
    for ff in files:
      existing[ff] = True

  if gr == 'icann_cor':
    for sub_dir,URI in groups[gr]['sub_dir'].items():
      if sub_dir == str(date.today().year):
        for ll in get_links(URI, groups[gr]['regex']):
          if ll.endswith('.pdf'): # 2012 and 2013 sometimes add another level of redirection
            if Util.parse_url(ll).path.split('/')[-1] not in existing:
              download(ll, base_dir + groups[gr]['path'] + '/' + sub_dir + '/' + ll.split('/')[-1])
          else:
            for mm in get_links(ll, groups[gr]['regex']):
              if Util.parse_url(mm).path.split('/')[-1] not in existing:
                download(mm, base_dir + groups[gr]['path'] + '/' + sub_dir + '/' + mm.split('/')[-1])

  elif gr == 'gac':
    for page in get_links(groups[gr]['uri'], groups[gr]['option_regex'], ['option', 'value']):
      for ll in get_links(page, groups[gr]['regex']):
        if Util.parse_url(ll).path.split('/')[-1] not in existing:
          download(ll, base_dir + groups[gr]['path'] + '/' + ll.split('/')[-1])

  else:
    for ll in get_links(groups[gr]['uri'], groups[gr]['regex']):
      if Util.parse_url(ll).path.split('/')[-1] not in existing:
        download(ll, base_dir + groups[gr]['path'] + '/' + ll.split('/')[-1])
