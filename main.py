#!/usr/bin/env python
# encoding: utf-8

import argparse
import urllib
import json
import giphypop, pdb
import os

URL = 'http://api.giphy.com/v1/gifs/search?'
PARAMS = {'api_key': 'dc6zaTOxFJmzC'}

JSON_STRUCT = {'scraped_count': 0, 'total_count': 0, 'gifs': [{'id': 'id', 'tags': ['tag1', 'tag2', 'etc']}, {}]
               }


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape GIFs from giphy")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-p", "--phrase", action="store_true", default=True, help="Match all given tags")
    group.add_argument(
        "-a", "--any", action="store_true", help="Match any given tags")
    parser.add_argument(
        "-l", "--limit", type=int, default=None, help="Scraped GIFs limit")
    parser.add_argument('tags', nargs='+', help="Tags of GIFs to be scraped")
    return parser.parse_args()


def main():
    args = parse_args()
    giphy = giphypop.Giphy()
    tags = []
    file_dir = 'gifs/'
    if args.any:
        for tag in args.tags:
            tags.append(tag)
            file_dir = file_dir + tag + '+'
        file_dir = file_dir[:-1]
    else:
        tags = [''.join([t + ' ' for t in args.tags])[:-1]]
        file_dir = file_dir + tags[0]
    gifs = []
    limit = args.limit
    found = 0
    for s in tags:
        print 'searching for "' + s + '":'
        gifs += [x for x in giphy.search(limit=limit, phrase=s)]
        if limit is not None:
            limit = limit - len(gifs)
        print 'found ' + str(len(gifs) - found) + ' GIFs'
        if limit == 0:
            break
        found = len(gifs)
    os.mkdir(file_dir)
    gifs_dict = {}
    gif_ids = []
    gifs_len = str(len(gifs))
    print 'downloading ' + gifs_len + ' GIFs'
    i = 0
    for gif in gifs:
        gif_ids.append(gif.id)
        urllib.urlretrieve(gif.original.mp4, file_dir + '/' + gif.id + '.mp4')
        i = i + 1
        print 'GIF ' + str(i) + ' of '+ gifs_len + ' downloaded'
    gifs_dict['ids'] = gif_ids
    gifs_dict['query'] = tags
    json_file = file_dir + '/_data.json'

    with open(json_file, 'w') as outfile:
                json.dump(gifs_dict, outfile)


if __name__ == '__main__':
    main()
