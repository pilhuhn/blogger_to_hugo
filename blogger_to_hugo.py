import os
import sys
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import xmltodict
import requests
from markdownify import markdownify as md

# File path for the exported file
in_file = "/Users/hrupp/downloads/blog-05-01-2024.xml"
# Where to write the output.
out_dir = "/tmp/blog"

hugo_article_header = """
---
title: '{title}'
date: {date}
tags: {tags}
lang: 'en'
useCover: true
Summary: '{title}'
---

"""


def find_is_post(category_list) -> bool:
    if isinstance(category_list, list):
        found = False
        for c_dict in category_list:
            if find_is_post_from_dict(c_dict):
                found = True
        return found
    else:
        return find_is_post_from_dict(category_list)


def find_is_post_from_dict(c_dict):
    if c_dict['@scheme'] == 'http://schemas.google.com/g/2005#kind':
        if c_dict["@term"] == 'http://schemas.google.com/blogger/2008/kind#post':
            return True
    return False


def get_tags(categories):
    out = '[ '
    if isinstance(categories, list):
        i = 1
        for c_dict in categories:
            if c_dict['@scheme'] == 'http://www.blogger.com/atom/ns#':
                out = out + "'%s'" % c_dict['@term']
                if i < len(categories) - 1:  # -1 because of the generic kind category
                    out = out + ', '
                i = i + 1
    out = out + ' ]'
    return out


def get_published_year(published_date):
    return published_date[:4]


def fetch_image(src_url, img_path_on_disk) -> bool:
    r = requests.get(src_url, allow_redirects=True)
    if r.status_code != 200:
        print("Warning, can't retrieve content for %s from %s " % (img_path_on_disk, src_url))
        return False
    else:
        open(img_path_on_disk, mode="wb").write(r.content)
        return True


def mangle_content(content, dir):
    soup = BeautifulSoup(content, 'html.parser')
    for img in soup.find_all('img'):
        src = img.attrs['src']
        src_url = urlparse(src)
        pos = src_url.path.rfind('/')
        src2 = src_url.path[pos + 1:]
        if src.startswith('https:/lh3'):
            # Some urls are mangled. Perhaps Google's way of preventing scraping..
            src = 'https://lh3' + src[10:]

        img_path_on_disk = '%s/%s' % (dir, src2)
        # fetch from remote if not yet there
        if not os.path.exists(img_path_on_disk):
            fetch_image(src, img_path_on_disk)
        img.attrs['src'] = src2

    return soup.prettify()


#
# ------- main ------
#
os.makedirs(out_dir, exist_ok=True)

unknown_count = 0
runs = 0

with open(in_file) as fd:
    d = xmltodict.parse(fd.read())
    entries = d['feed']['entry']
    for entry in entries:
        entry_content = entry['content']
        title_dict = entry['title']
        categories = entry['category']
        is_post = find_is_post(categories)
        if not is_post:
            continue
        # For whatever strange reason I have posts without title...
        if '#text' not in title_dict:
            title = 'no-title-%d' % unknown_count
            unknown_count = unknown_count + 1
        else:
            title = title_dict['#text']
        title_for_dir = title.replace(' ', '-').replace(':', '').replace('&quot;', '').replace('/', '_')
        published_date = entry['published']
        publish_year = get_published_year(published_date)
        art_dir = "%s/%s/%s" % (out_dir, publish_year, title_for_dir)
        os.makedirs(art_dir, exist_ok=True)

        tags = get_tags(categories)

        content_dict = entry['content']
        content = content_dict['#text']
        content = mangle_content(content, art_dir)

        index_file_name = "%s/%s" % (art_dir, 'index.md')
        with open(index_file_name, "w") as index:
            index.write(hugo_article_header.format(
                title=title,
                date=published_date,
                tags=tags,
                summary=title
            ))
            index.write('\n')

            # Turn html content into Markdown
            mdc = md(content)

            # We need html <i> as the body from blogger is html and hugo would not understand MarkDown here
            index.write('| _This is a historical article and was first posted on **Blogger in %s**_\n' % publish_year)
            index.write('\n')
            index.write('\n')
            index.write(mdc)

