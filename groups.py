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

import re

# Not the prettiest way to do this, but it will do for now
# TODO: Make this objected oriented
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
groups['octo_com']['path'] = 'icann/octo/com/'
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
groups['rzerc']['path'] = 'icann/rzerc/pub'
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
