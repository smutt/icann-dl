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
from urllib3 import util as Util
from datetime import datetime, date

# Basic logging to stdout
# TODO: For now this remains a global func
def logit(s):
  print(datetime.isoformat(datetime.utcnow()) + ' ' + s.strip())

class DL_Group():
  base_dir = '/var/www/htdocs/icann-hamster.nl/ham/' # Where the local fun starts

  def __init__(self):
    self.regex = []

    self.exclude = [] # Links to exclude for all groups
    self.exclude.append(re.compile('.*/didp-response-process-29oct13-en\.pdf$'))
    self.exclude.append(re.compile('.*/registrar-billing-faq-21dec21-en\.pdf$'))
    self.exclude.append(re.compile('.*/gdd-ops-handbook-registry-operators-15aug18-en\.pdf$'))
    self.exclude.append(re.compile('.*/rsep-process-workflow-14jun19-en\.pdf$'))
    self.exclude.append(re.compile('.*/mosapi-specification\.pdf$'))

  # Grab a file and write to disk
  # Takes a remote URI and a local filename
  def _download(self, uri, fname):
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

  # Wrapper for _download()
  def download(self, remote):
    return self._download(remote, self.base_dir + self.path + '/' + remote.split('/')[-1])

  # Return dict of files existing locally on disk for group
  # Whitespaces in files are escaped with %20
  def local_files(self):
    rv = {}
    for _, _, files in os.walk(self.base_dir + self.path):
      for ff in files:
        rv[ff.strip()] = True
    return rv

  # Should we exclude passed link
  def is_excluded(self, s):
    for pattern in self.exclude:
      if pattern.match(s):
        return True
    return False

  # Grab links in tags matching regex
  # URI => the URI to grab and parse
  # regex => regex for matching the links
  # tags => a list of [html_tag, attribute] to match regex against
  # Returns deduplicated list of links
  def _get_links(self, URI, regex, tags):
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
        if not self.is_excluded(link):
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

  # Wrapper for _get_links()
  def get_links(self):
    return self._get_links(self.uri, self.regex, ['a', 'href'])

# CEO Reports to the Board
class Ceo(DL_Group):
  def __init__(self):
    super().__init__()
    self.path = 'icann/ceo/board'
    self.uri = 'https://www.icann.org/reports-to-board'
    self.regex.append(re.compile('^.*/uploads/board_report/attachment/.*\.pdf$'))

# GAC
class Gac(DL_Group):
  def __init__(self):
    super().__init__()
    self.path = 'soac/gac/com'
    self.uri = 'https://gac.icann.org/contentMigrated/icann1-singapore-communique'
    self.regex.append(re.compile('^.*/.*communique.*\.pdf[\?language_id.*]?', flags=re.ASCII | re.IGNORECASE))
    self.option_regex = []
    self.option_regex.append(re.compile('^/contentMigrated/icann.*-communique\?.*$'))

  def get_links(self):
    rv = []
    for page in self._get_links(self.uri, self.option_regex, ['option', 'value']):
      rv.extend(self._get_links(page, self.regex, ['a', 'href']))
    return rv

# Government Engagement Publications
class Ge(DL_Group):
  def __init__(self):
    super().__init__()
    self.path = 'icann/ge/pub'
    self.uri = 'https://www.icann.org/en/government-engagement/publications?page=1'
    self.regex.append(re.compile('.*/en/files/government-engagement-ge/.*\.pdf$'))

# Government Engagement Reports to the GAC
class Ge_gac(DL_Group):
  def __init__(self):
    super().__init__()
    self.path = 'icann/ge/gac'
    self.uri = 'https://gac.icann.org/activity/bi-monthly-report-icann-gse-ge-governments-and-igos-engagement-activities'
    self.regex = []
    self.regex.append(re.compile('.*/reports/public/.*\.pdf$'))

# ICANN Correspondence
class Icann_cor(DL_Group):
  def __init__(self):
    super().__init__()
    self.path = 'icann/cor'
    self.regex.append(re.compile('.*/correspondence/.*\.pdf$'))
    self.regex.append(re.compile('.*/system/files/files/.*\.pdf$'))
    self.regex.append(re.compile('^/en/news/correspondence/.*-to-.*-en$'))

    self.sub_dir = {} # Before 2003 there are no PDFs
    self.sub_dir['2003'] = 'https://www.icann.org/resources/pages/2003-2012-10-11-en'
    self.sub_dir['2004'] = 'https://www.icann.org/resources/pages/2004-2012-10-11-en'
    self.sub_dir['2005'] = 'https://www.icann.org/resources/pages/2005-2012-10-11-en'
    self.sub_dir['2006'] = 'https://www.icann.org/resources/pages/2006-2012-10-11-en'
    self.sub_dir['2007'] = 'https://www.icann.org/resources/pages/2007-2012-10-11-en'
    self.sub_dir['2008'] = 'https://www.icann.org/resources/pages/2008-2012-10-11-en'
    self.sub_dir['2009'] = 'https://www.icann.org/resources/pages/2009-2012-10-11-en'
    self.sub_dir['2010'] = 'https://www.icann.org/resources/pages/2010-2012-10-11-en'
    self.sub_dir['2011'] = 'https://www.icann.org/resources/pages/2011-2012-02-25-en'
    self.sub_dir['2012'] = 'https://www.icann.org/resources/pages/2012-2013-01-10-en'
    self.sub_dir['2013'] = 'https://www.icann.org/resources/pages/2013-2014-01-24-en'
    self.sub_dir['2014'] = 'https://www.icann.org/resources/pages/2014-2014-01-24-en'
    self.sub_dir['2015'] = 'https://www.icann.org/resources/pages/correspondence-2015'
    self.sub_dir['2016'] = 'https://www.icann.org/resources/pages/correspondence-2016'
    self.sub_dir['2017'] = 'https://www.icann.org/resources/pages/correspondence-2017'
    self.sub_dir['2018'] = 'https://www.icann.org/resources/pages/correspondence-2018'
    self.sub_dir['2019'] = 'https://www.icann.org/resources/pages/correspondence-2019'
    self.sub_dir['2020'] = 'https://www.icann.org/resources/pages/correspondence-2020'
    self.sub_dir['2021'] = 'https://www.icann.org/resources/pages/correspondence-2021'
    self.sub_dir['2022'] = 'https://www.icann.org/resources/pages/correspondence-2022'
    #self.sub_dir['2023'] = '' Will need to add these for each year

  def get_links(self):
    rv = []
    this_year = str(date.today().year)
    if this_year in self.sub_dir:
      for ll in self._get_links(self.sub_dir[this_year], self.regex, ['a', 'href']):
        if ll.endswith('.pdf'): # 2012 and 2013 sometimes added another level of redirection
          rv.append(ll)
        else:
          for mm in self._get_links(ll, self.regex, ['a', 'href']):
            rv.append(mm)
    return rv

  def download(self, remote):
    this_year = str(date.today().year)
    if this_year in self.sub_dir:
      return self._download(remote, self.base_dir + self.path + '/' + this_year + '/' + remote.split('/')[-1])

# ICANN Correspondence Sent Externally
class Icann_ext(DL_Group):
  def __init__(self):
    super().__init__()
    self.path = 'icann/ext'
    self.uri = 'https://www.icann.org/en/government-engagement/submissions-to-external-bodies'
    self.regex.append(re.compile('.*/en/files/government-engagement-ge/.*\.pdf$'))

# OCTO Publications
class Octo(DL_Group):
  def __init__(self):
    super().__init__()
    self.path = 'icann/octo/pub'
    self.uri = 'https://www.icann.org/resources/pages/octo-publications-2019-05-24-en'
    self.regex.append(re.compile('.*/octo-.*\.pdf$'))

# OCTO Commissioned Publications
class Octo_com(DL_Group):
  def __init__(self):
    super().__init__()
    self.path = 'icann/octo/com/'
    self.uri = 'https://www.icann.org/resources/pages/octo-commissioned-documents-2020-11-05-en'
    self.regex.append(re.compile('.*/system/files/files/.*\.pdf$'))

# RSSAC Publications
class Rssac(DL_Group):
  def __init__(self):
    super().__init__()
    self.path = 'soac/rssac/pub'
    self.uri = 'https://www.icann.org/groups/rssac/documents'
    self.regex.append(re.compile('.*/system/files/files/.*rssac-.*\.pdf$'))
    self.regex.append(re.compile('^/en/groups/rssac/rssac-iana-stewardship-transition-08may14-en.pdf$'))

# RZERC Publications
class Rzerc(DL_Group):
  def __init__(self):
    super().__init__()
    self.path = 'soac/rzerc/pub'
    self.uri = 'https://www.icann.org/en/rzerc#documents'
    self.regex.append(re.compile('.*/uploads/ckeditor/rzerc-0.*\.pdf$'))

# SSAC Reports
class Ssac(DL_Group):
  def __init__(self):
    super().__init__()
    self.path = 'soac/ssac/reports'
    self.uri = 'https://www.icann.org/groups/ssac/documents'
    self.regex.append(re.compile('.*/groups/ssac/documents/sac-.*\.pdf$'))
    self.regex.append(re.compile('.*/system/files/files/sac-.*\.pdf$'))

# SSAC Correspondence
class Ssac_cor(DL_Group):
  def __init__(self):
    super().__init__()
    self.path = 'soac/ssac/cor'
    self.uri = 'https://www.icann.org/groups/ssac/documents-correspondence'
    self.regex.append(re.compile('.*/system/files/files/ssac2.*\.pdf$'))


# All our groups
groups = {}
groups['ceo'] = Ceo()
groups['gac'] = Gac()
groups['ge'] = Ge()
groups['ge_gac'] = Ge_gac()
groups['icann_cor'] = Icann_cor()
groups['icann_ext'] = Icann_ext()
groups['octo'] = Octo()
groups['octo_com'] = Octo_com()
groups['rssac'] = Rssac()
groups['rzerc'] = Rzerc()
groups['ssac'] = Ssac()
groups['ssac_cor'] = Ssac_cor()
