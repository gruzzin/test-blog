#!/usr/bin/env python3

import argparse
from datetime import datetime
from collections import OrderedDict
from post import Post


def order_by_date(posts):
    return OrderedDict(
        sorted(posts.items(),
               key=lambda x: datetime.strptime(
                    x[1]['date'], '%Y-%m-%d %H:%M:%S'),
               reverse=True))


def post_table(posts, ordered=None):
    print('{0:3s} | {1:<20s} | {2:<19s} | {3}'
          .format('ID', 'Title', 'Date modified', 'Body'))
    print('-' * 80)
    if ordered == 'date':
        posts = order_by_date(posts)
    for postid in posts.keys():
        print('{0:3d} | {1:20s} | {2:19s} | {3}'
              .format(postid,
                      posts[postid]['title'][:20],
                      posts[postid]['date'],
                      posts[postid]['body'])
              [:80])


def list_posts(args):
    posts = Post.load()
    if args.s:
        post_table(posts, ordered='date')
    else:
        post_table(posts)


def search_posts(args):
    posts = Post.search(args.query)
    if len(posts) > 0:
        if args.s:
            post_table(posts, ordered='date')
        else:
            post_table(posts)
    else:
        print('No posts match query: {}'.format(args.query))


def add_post(args):
    p = Post(args.title, args.body)
    p.save()


def mod_post(args):
    posts = Post.load()
    if not args.title and not args.body:
        print('Either title or body are required for post modificaion')
    else:
        p = Post(args.title or posts[args.postid]['title'],
                 args.body or posts[args.postid]['body'],
                 postid=args.postid)
        p.save()


def del_post(args):
    Post.delete(args.postid)


def trunc(text, max_length):
    words = text.split()
    line = []
    cur_length = 0
    for word in words:
        if cur_length + len(word) <= max_length - len(line):
            line.append(word)
            cur_length += len(word)
        else:
            yield ' '.join(line)
            line = [word, ]
            cur_length = len(word)
    yield ' '.join(line)


def print_post(args):
    if 'all' in args.postid:
        posts = Post.load()
    else:
        try:
            ids = [int(x) for x in args.postid]
        except ValueError:
            print('Post IDs should be numbers')
            return
        print(ids)
        posts = Post.load(ids)
    if not len(posts):
        print('Post ID(s) not found: {}'.format(' '.join(args.postid)))
        return
    if args.s:
        posts = order_by_date(posts)
    for postid in posts.keys():
        if len(posts[postid]['body']) > 74:
            body = '\n      '.join(trunc(posts[postid]['body'], 74))
        else:
            body = posts[postid]['body']
        print('Title: {}\nPost ID: {}, last modification date: {}\nBody: {}'
              .format(posts[postid]['title'],
                      postid,
                      posts[postid]['date'],
                      body))
        print('-' * 80)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple console blog client',
                                     add_help=True)
    actions = parser.add_subparsers(help='Actions')

    l_posts = actions.add_parser('list', help='List all posts')
    l_posts.add_argument('-s', help='Sort by date', action='store_true')
    l_posts.set_defaults(func=list_posts)

    p_post = actions.add_parser('print', help='Print post')
    p_post.add_argument('postid', help='IDs of posts to print or "all"',
                        nargs='+')
    p_post.add_argument('-s', help='Sort by date', action='store_true')
    p_post.set_defaults(func=print_post)

    s_posts = actions.add_parser('search', help='Search posts')
    s_posts.add_argument('query', help='Search string',
                         action='store')
    s_posts.add_argument('-s', help='Sort results by date',
                         action='store_true')
    s_posts.set_defaults(func=search_posts)

    a_post = actions.add_parser('add', help='Add post')
    a_post.add_argument('title', help='Post title', action='store')
    a_post.add_argument('body', help='Post body', action='store')
    a_post.set_defaults(func=add_post)

    m_post = actions.add_parser('modify', help='Modify post')
    m_post.add_argument('postid', help='ID of post to modify', action='store',
                        type=int)
    m_post.add_argument('-t', '--title', help='New title', action='store')
    m_post.add_argument('-b', '--body', help='New body', action='store')
    m_post.set_defaults(func=mod_post)

    d_post = actions.add_parser('delete', help='Delete post')
    d_post.add_argument('postid', help='ID of post do delete', action='store',
                        type=int)
    d_post.set_defaults(func=del_post)

    args = parser.parse_args()

    try:
        args.func(args)
    except AttributeError:
        parser.print_help()
