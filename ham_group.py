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
#  Copyright (C) 2023, 2024 Andrew McConachie, <andrew.mcconachie@icann.org>

import basic
import funk
import os
import re
import requests
import stat
from datetime import date

class Ham_group():
  base_dir = '/var/www/htdocs/icannhaz.org/ham/' # Where the local fun starts

  def __init__(self):
    self.enabled = True
    self.async_safe = True
    self.regex = []
    self.help_text = '' # Help text displayed with the group. Intended to be overridden

    self.exclude = [] # Links to exclude for all groups
    self.exclude.append(re.compile(r'.*/didp-response-process-29oct13-en\.pdf$'))
    self.exclude.append(re.compile(r'.*/registrar-billing-faq-21dec21-en\.pdf$'))
    self.exclude.append(re.compile(r'.*/gdd-ops-handbook-registry-operators-15aug18-en\.pdf$'))
    self.exclude.append(re.compile(r'.*/rsep-process-workflow-14jun19-en\.pdf$'))
    self.exclude.append(re.compile(r'.*/mosapi-specification\.pdf$'))
    self.exclude.append(re.compile(r'.*/delegation-of-authority-guidelines-08nov16-en.pdf$'))
    self.exclude.append(re.compile(r'.*/delegation-of-authority-guidelines-16mar17-en.pdf$'))
    self.exclude.append(re.compile(r'.*/delegation-of-authority-guidelines-24oct24-en.pdf$'))

  # Wrapper for _download()
  def download(self, remote):
    return self._download(remote, self.base_dir + self.path + '/' + self.clean_filename(remote.split('/')[-1]))

  # Grab a file and write to disk
  # Takes a remote URI and a local filename
  def _download(self, url, fname):
    if os.path.exists(fname):
      return

    try:
      req = requests.get(url, stream=True)
      if req.status_code == 200:
        with open(fname, 'wb') as f:
          for chunk in req.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
              f.write(chunk)
        os.chmod(fname, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH) # 0644
        basic.logit('||' + self.help_text + '||' + url + '||' + fname)
      else:
        basic.logit("err:dl_bad_response:" + url)
    except requests.RequestException:
      basic.logit("err:dl_req_exception:" + url)

  # Wrapper for funk.local_files()
  def local_files(self):
    try:
      path = self.top_path
    except:
      path = self.path
    return funk.local_files(self.base_dir + path)

  # Wrapper for funk.remote_file()
  def remote_file(self, URL):
    return funk.remote_file(URL)

  # Wrapper for funk.get_links()
  def get_links(self):
    return funk.get_links(self.uri, self.regex, ['a', 'href'], self.exclude)

  # Converts a dirty filename (fname) to a clean filename
  def clean_filename(self, fname):
    return fname.replace(" ", "-").replace("%20", "-")


#####################
# Individual Groups #
#####################

# ALAC
class Alac(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'ALAC Publications'
    self.top_path = 'soac/alac/pub'
    self.path = 'soac/alac/pub/' + str(date.today().year)
    self.uri = 'https://atlarge.icann.org/policy-summary?page=1'
    self.top_regex = []
    self.top_regex.append(re.compile(r'^.*/advice_statements/.*$'))
    self.regex.append(re.compile(r'.*/uploads/advice_statement_document/document/.*\.pdf$'))

  def get_links(self):
    rv = []
    for doc in funk.get_links(self.uri, self.top_regex, ['a', 'href'], self.exclude):
      rv.extend(funk.get_links(doc, self.regex, ['option', 'value'], self.exclude))
    return rv

# ASO Minutes
class Aso_min(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'ASO Meeting Minutes'
    self.path = 'soac/aso/min'
    self.uri = 'https://aso.icann.org/aso-ac/meetings/ac-meeting-minutes/'
    self.regex.append(re.compile(r'.*\.pdf$'))

# ASO Policy
class Aso_policy(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'ASO Global Policies'
    self.path = 'soac/aso/policy'
    self.uri = 'https://aso.icann.org/policy/global/current-global-policies/'
    self.regex.append(re.compile(r'.*\.pdf$'))

# ASO Historical
class Aso_pres(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'ASO Presentations'
    self.path = 'soac/aso/pres'
    self.uri = 'https://aso.icann.org/documents/presentations/'
    self.regex.append(re.compile(r'.*\.pdf$'))

# Stub class for audio
# Audio files are never automatically fetched, we manage them manually.
# This is just a stub class for counting the files and bytes
# TODO: Get this into it's own file and out of ham_group.py
class Audio(Ham_group):
  base_dir = '/var/www/htdocs/icannhaz.org/audio/' # Overridden from Ham_group

  def __init__(self):
    super().__init__()
    self.help_text = 'Stub Group for audio recordings'
    self.enabled = False
    self.path = ''

# ICANN Board Briefings
# Specific search broken for briefing materials, once fixed the url can get more specific
class Board_brief(Ham_group):
  def __init__(self):
    super().__init__()
    self.async_safe = False
    self.help_text = 'ICANN Board Briefings'
    this_year = str(date.today().year)
    self.uri = 'https://www.icann.org/en/board-activities-and-meetings?start-date=01-01-' + this_year \
      + '&end-date=31-12-' + this_year + '&expand-all=true'
    self.path = 'icann/board/brief'
    self.regex.append(re.compile(r'.*/briefing-materials/.*\.pdf'))

# ICANN Board Other
# Must be run after Board_brief
# If we ever add another Board group this will need changing
class Board_other(Ham_group):
  def __init__(self):
    super().__init__()
    self.async_safe = False
    self.help_text = 'ICANN Board Other'
    self.top_path = 'icann/board'
    this_year = str(date.today().year)
    self.uri = 'https://www.icann.org/en/board-activities-and-meetings?start-date=01-01-' + this_year \
      + '&end-date=31-12-' + this_year + '&expand-all=true'
    self.path = 'icann/board/other'
    self.regex.append(re.compile(r'.*\.pdf'))

# CCNSO Parent Class
# The primary reason for doing this is to prevent the same file showing up in multiple CCNSO groups
class Ccnso(Ham_group):
  def __init__(self):
    super().__init__()
    self.async_safe = False
    self.root_path = 'soac/ccnso'

  # Wrapper for local_files()
  def local_files(self):
    return funk.local_files(self.base_dir + self.root_path)

# CCNSO Correspondence
class Ccnso_cor(Ccnso):
  def __init__(self):
    super().__init__()
    self.help_text = 'CCNSO Correspondence'
    self.path = 'soac/ccnso/cor'
    self.uri = 'https://ccnso.icann.org/en/library?tid[19]=19&page=0'
    self.regex.append(re.compile(r'.*\.pdf$'))

# CCNSO Guidelines
class Ccnso_guide(Ccnso):
  def __init__(self):
    super().__init__()
    self.help_text = 'CCNSO Guidelines'
    self.path = 'soac/ccnso/guide'
    self.uri = 'https://ccnso.icann.org/en/library?tid[25]=25&page=0'
    self.regex.append(re.compile(r'.*\.pdf$'))

# CCNSO Meeting Minutes
class Ccnso_min(Ccnso):
  def __init__(self):
    super().__init__()
    self.help_text = 'CCNSO Minutes'
    self.path = 'soac/ccnso/min'
    self.uri = 'https://ccnso.icann.org/en/library?tid[28]=28&page=0'
    self.regex.append(re.compile(r'.*\.pdf$'))

# CCNSO Presentations (not Tech Day)
class Ccnso_pres(Ccnso):
  def __init__(self):
    super().__init__()
    self.help_text = 'CCNSO Presentations'
    self.path = 'soac/ccnso/pres'
    self.uri = 'https://ccnso.icann.org/en/library?tid[36]=36&page=0'
    self.regex.append(re.compile(r'.*\.pdf$'))

# CCNSO Reports
class Ccnso_rep(Ccnso):
  def __init__(self):
    super().__init__()
    self.help_text = 'CCNSO Reports'
    self.path = 'soac/ccnso/reports'
    self.uri = 'https://ccnso.icann.org/en/library?tid[41]=41&page=0'
    self.regex.append(re.compile(r'.*\.pdf$'))

# CCNSO Tech Day
class Ccnso_tech(Ccnso):
  def __init__(self):
    super().__init__()
    self.help_text = 'CCNSO Tech Day'
    self.enabled = False
    self.path = 'soac/ccnso/techday'

# CCNSO Transcripts
class Ccnso_tran(Ccnso):
  def __init__(self):
    super().__init__()
    self.help_text = 'CCNSO Transcripts'
    self.path = 'soac/ccnso/tran'
    self.uri = 'https://ccnso.icann.org/en/library?tid[51]=51&page=0'
    self.regex.append(re.compile(r'.*\.pdf$'))

# CEO Reports to the Board
class Ceo(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'CEO Reports to the Board'
    self.path = 'icann/ceo/board'
    self.uri = 'https://www.icann.org/reports-to-board'
    self.regex.append(re.compile(r'^.*/uploads/board_report/attachment/.*\.pdf$'))
    self.regex.append(re.compile(r'^.*/en/files/.*\.pdf$'))

# GAC
class Gac(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'GAC Communiques'
    self.path = 'soac/gac/com'
    self.uri = 'https://gac.icann.org/contentMigrated/icann1-singapore-communique'
    self.regex.append(re.compile(r'^.*/.*communique.*\.pdf[\?language_id.*]?', flags=re.ASCII | re.IGNORECASE))
    self.option_regex = []
    self.option_regex.append(re.compile(r'^/contentMigrated/icann.*-communique\?.*$'))

  def get_links(self):
    rv = []
    for page in funk.get_links(self.uri, self.option_regex, ['option', 'value'], self.exclude):
      rv.extend(funk.get_links(page, self.regex, ['a', 'href'], self.exclude))
    return rv

# Government Engagement Publications
class Ge(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'ICANN GE Publications'
    self.path = 'icann/ge/pub'
    self.uri = 'https://www.icann.org/en/government-engagement/publications?page=1'
    self.regex.append(re.compile(r'.*/en/files/government-engagement-ge/.*\.pdf$'))

# Government Engagement Reports to the GAC
class Ge_gac(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'ICANN GE Reports to GAC'
    self.path = 'icann/ge/gac'
    self.uri = 'https://gac.icann.org/activity/bi-monthly-report-icann-gse-ge-governments-and-igos-engagement-activities'
    self.regex = []
    self.regex.append(re.compile(r'.*/reports/public/.*\.pdf$'))

# GNSO Parent Class
# The primary reason for doing this is to prevent the same file showing up in multiple GNSO groups
class Gnso(Ham_group):
  def __init__(self):
    super().__init__()
    self.async_safe = False
    self.root_path = 'soac/gnso'

  # Wrapper for local_files()
  def local_files(self):
    return funk.local_files(self.base_dir + self.root_path)

# GNSO Elections
class Gnso_elect(Gnso):
  def __init__(self):
    super().__init__()
    self.help_text = 'GNSO Elections'
    self.path = 'soac/gnso/elections'
    self.uri = 'https://gnso.icann.org/en/council/elections'
    self.regex = []
    self.regex.append(re.compile(r'.*\.pdf$'))
    self.regex.append(re.compile(r'.*\.ppt$'))
    self.regex.append(re.compile(r'.*\.pptx$'))

# GNSO Correspodence
class Gnso_cor(Gnso):
  def __init__(self):
    super().__init__()
    self.help_text = 'GNSO Correspondence'
    self.path = 'soac/gnso/cor'
    self.uri = 'https://gnso.icann.org/en/council/correspondence/' + str(date.today().year)
    self.regex = []
    self.regex.append(re.compile(r'.*\.pdf$'))
    self.regex.append(re.compile(r'.*\.ppt$'))
    self.regex.append(re.compile(r'.*\.pptx$'))

# GNSO Presentations
class Gnso_pres(Gnso):
  def __init__(self):
    super().__init__()
    self.help_text = 'GNSO Presentations'
    self.path = 'soac/gnso/pres'
    self.uri = 'https://gnso.icann.org/en/council/presentations'
    self.regex = []
    self.regex.append(re.compile(r'.*\.pdf$'))
    self.regex.append(re.compile(r'.*\.ppt$'))
    self.regex.append(re.compile(r'.*\.pptx$'))

# GNSO Reports
class Gnso_rep(Gnso):
  def __init__(self):
    super().__init__()
    self.help_text = 'GNSO Reports'
    self.path = 'soac/gnso/reports'
    self.uri = 'https://gnso.icann.org/en/library?tid[41]=41'
    self.regex = []
    self.regex.append(re.compile(r'.*\.pdf$'))

# GNSO Transcripts
class Gnso_tran(Gnso):
  def __init__(self):
    super().__init__()
    self.help_text = 'GNSO Transcripts'
    self.path = 'soac/gnso/tran'
    self.uri = 'https://gnso.icann.org/en/library?tid[51]=51'
    self.regex = []
    self.regex.append(re.compile(r'.*\.pdf$'))

# ICANN Correspondence
class Icann_cor(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'ICANN Correspondence'
    self.top_path = 'icann/cor'
    self.path = 'icann/cor/' + str(date.today().year)
    self.uri = 'https://www.icann.org/resources/pages/correspondence'
    self.regex.append(re.compile(r'.*/correspondence/.*\.pdf$'))
    self.regex.append(re.compile(r'.*/system/files/files/.*\.pdf$'))
    self.regex.append(re.compile(r'^/en/news/correspondence/.*-to-.*-en$'))

# ICANN Correspondence Sent Externally
class Icann_ext(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'ICANN Submissions to External Bodies'
    self.path = 'icann/ext'
    self.uri = 'https://www.icann.org/en/government-engagement/submissions-to-external-bodies'
    self.regex.append(re.compile(r'.*/en/files/government-engagement-ge/.*\.pdf$'))

# OCTO Publications
# UNDER CONSTRUCTION
class Octo(Ham_group):
  def __init__(self):
    super().__init__()
    self.async_safe = False
    self.help_text = 'ICANN OCTO Publications'
    self.path = 'icann/octo/pub'
    self.uri = 'https://www.icann.org/resources/pages/octo-publications-2019-05-24-en'
    self.regex.append(re.compile(r'.*/octo-.*\.pdf$'))

  # Wrapper for get_links()
  # OCTO versioning requires we check if a new version has been uploaded
  def get_links(self):
    links = funk.get_links(self.uri, self.regex, ['a', 'href'], self.exclude)
    return links + funk.real_locations(links)

# OCTO Commissioned Publications
class Octo_com(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'ICANN OCTO Commissioned Publications'
    self.path = 'icann/octo/com'
    self.uri = 'https://www.icann.org/resources/pages/octo-commissioned-documents-2020-11-05-en'
    self.regex.append(re.compile(r'.*/system/files/files/.*\.pdf$'))

# OCTO Archive
class Octo_archive(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'ICANN OCTO Archive'
    self.path = 'icann/octo/archive'
    self.uri = 'https://www.icann.org/octo-document-archive'
    self.regex.append(re.compile(r'/en.*\.pdf$'))
    self.regex.append(re.compile(r'/news.*$'))
    self.regex.append(re.compile(r'/en.*\.htm$'))
    self.regex2 = []
    self.regex2.append(re.compile(r'/.*\.pdf$'))

  def local_files(self):
    return funk.local_files(self.base_dir + self.path) | funk.local_files(self.base_dir + 'soac/ssac/reports')

  def get_links(self):
    rv = []
    for ll in super().get_links():
      if ll.endswith('.pdf'):
        rv.append(ll)
      else:
        for mm in funk.get_links(ll, self.regex2, ['a', 'href'], self.exclude):
          rv.append(mm)
    return rv

# RSSAC Publications
class Rssac(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'RSSAC Publications'
    self.path = 'soac/rssac/pub'
    self.uri = 'https://www.icann.org/en/rssac/publications'
    self.regex.append(re.compile(r'.*/root-server-system-advisory-committee-rssac-publications/.*\.pdf$'))
    self.regex.append(re.compile(r'.*/system/files/files/.*rssac-.*\.pdf$'))
    self.regex.append(re.compile(r'^/en/groups/rssac/rssac-iana-stewardship-transition-08may14-en.pdf$'))

# RSSAC Meeting Minutes
class Rssac_min(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'RSSAC Minutes'
    self.path = 'soac/rssac/min'
    self.uri = 'https://www.icann.org/en/rssac/meetings'
    self.regex.append(re.compile(r'.*/en/files/meetings/.*\.pdf$'))

# RSSAC Caucus Meeting Minutes
class Rssac_c_min(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'RSSAC Caucus Minutes'
    self.path = 'soac/rssac/caucus/min'
    self.uri = 'https://www.icann.org/en/rssac/caucus/meetings'
    self.regex.append(re.compile(r'.*/en/files/root-server-system-advisory-committee-rssac-caucus/.*\.pdf$'))

# RZERC Publications
class Rzerc(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'RZERC Publications'
    self.path = 'soac/rzerc/pub'
    self.uri = 'https://www.icann.org/en/rzerc#documents'
    self.regex.append(re.compile(r'.*/uploads/ckeditor/rzerc-0.*\.pdf$'))

# RZERC Correspondence
class Rzerc_cor(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'RZERC Correspondence'
    self.path = 'soac/rzerc/cor'
    self.uri = 'https://www.icann.org/en/rzerc/rzerc-correspondence'
    self.regex.append(re.compile(r'.*/uploads/ckeditor/.*\.pdf$'))

# RZERC Minutes
class Rzerc_min(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'RZERC Minutes'
    self.path = 'soac/rzerc/min'
    self.uri = 'https://www.icann.org/rzerc'
    self.regex.append(re.compile(r'.*/uploads/iana_work_session_asset/attachment/.*inute.*\.pdf$'))

# RZERC Transcipts
class Rzerc_tran(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'RZERC Transcripts'
    self.path = 'soac/rzerc/tran'
    self.uri = 'https://www.icann.org/rzerc'
    self.regex.append(re.compile(r'.*/uploads/iana_work_session_asset/attachment/(?!.*inute).*ranscrip.*\.pdf$'))
    self.regex.append(re.compile(r'.*/uploads/iana_work_session_asset/attachment/(?!.*inute).*[Tt]eleconference.*\.pdf$'))
    self.regex.append(re.compile(r'.*/uploads/iana_work_session_asset/attachment/(?!.*inute).*ELECONFERENCE.*\.pdf$'))
    self.regex.append(re.compile(r'.*/uploads/iana_work_session_asset/attachment/(?!.*inute).*ecording.*\.pdf$'))
    self.regex.append(re.compile(r'.*/uploads/iana_work_session_asset/attachment/(?!.*inute).*[Mm]onthly_[Mm]eeting.*\.pdf$'))

# SSAC Reports
class Ssac(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'SSAC Reports'
    self.path = 'soac/ssac/reports'
    self.uri = 'https://www.icann.org/en/ssac/publications'
    self.regex.append(re.compile(r'.*icann.org/en/files/security-and-stability-advisory-committee-ssac-reports/.*\.pdf$'))

# SSAC Correspondence
class Ssac_cor(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'SSAC Correspondence'
    self.path = 'soac/ssac/cor'
    self.uri = 'https://www.icann.org/en/ssac/correspondence'
    self.regex.append(re.compile(r'.*icann.org/en/files/security-and-stability-advisory-committee-ssac-correspondence/.*\.pdf'))

# SSAC DNSSEC Workshop (now called DNSSEC & Security Workshop)
class Ssac_dnssec(Ham_group):
  def __init__(self):
    super().__init__()
    self.help_text = 'SSAC DNSSEC Workshop'
    self.enabled = False
    self.path = 'soac/ssac/dnssec/'

# All our groups
groups = {}
groups['alac'] = Alac()
groups['aso_min'] = Aso_min()
groups['aso_pol'] = Aso_policy()
groups['aso_pres'] = Aso_pres()
groups['audio'] = Audio()
groups['board_brief'] = Board_brief()
groups['board_other'] = Board_other()
groups['ccnso_cor'] = Ccnso_cor()
groups['ccnso_guide'] = Ccnso_guide()
groups['ccnso_min'] = Ccnso_min()
groups['ccnso_pres'] = Ccnso_pres()
groups['ccnso_rep'] = Ccnso_rep()
groups['ccnso_tech'] = Ccnso_tech()
groups['ccnso_tran'] = Ccnso_tran()
groups['ceo'] = Ceo()
groups['gac'] = Gac()
groups['ge'] = Ge()
groups['ge_gac'] = Ge_gac()
groups['gnso_elect'] = Gnso_elect()
groups['gnso_cor'] = Gnso_cor()
groups['gnso_pres'] = Gnso_pres()
groups['gnso_rep'] = Gnso_rep()
groups['gnso_tran'] = Gnso_tran()
groups['icann_cor'] = Icann_cor()
groups['icann_ext'] = Icann_ext()
groups['octo'] = Octo()
groups['octo_com'] = Octo_com()
groups['octo_arc'] = Octo_archive()
groups['rssac'] = Rssac()
groups['rssac_c_min'] = Rssac_c_min()
groups['rssac_min'] = Rssac_min()
groups['rzerc'] = Rzerc()
groups['rzerc_cor'] = Rzerc_cor()
groups['rzerc_min'] = Rzerc_min()
groups['rzerc_tran'] = Rzerc_tran()
groups['ssac'] = Ssac()
groups['ssac_cor'] = Ssac_cor()
groups['ssac_dnssec'] = Ssac_dnssec()
