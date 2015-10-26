from datetime import datetime
import json

filename = 'posts.json'


class Post(object):

    def __init__(self, title, body, postid=0):
        self.postid = postid
        self.title = title
        self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.body = body

    def to_dict(self):
        return {'title': self.title,
                'date': self.date,
                'body': self.body}

    def save(self):
        posts = Post.load()
        if not len(posts):
            self.postid = 1
        if posts.get(self.postid):
            posts[self.postid] = self.to_dict()
        elif not self.postid:
            self.postid = max(posts.keys()) + 1
        posts[self.postid] = self.to_dict()
        with open(filename, 'w') as f:
            json.dump(posts, f)

    @classmethod
    def load(cls, postid=None):
        try:
            with open(filename) as f:
                posts = json.load(f)
        except FileNotFoundError:
            print('File not found: {}'.format(filename))
            return {}
        if postid:
            return {int(k): posts[k] for k in posts.keys() if int(k) in postid}
        else:
            return {int(k): posts[k] for k in posts.keys()}

    @classmethod
    def search(cls, q):
        posts = Post.load()
        matches = {}
        for postid in posts.keys():
            if (q.lower() in posts[postid]['body'].lower() or
                    q.lower() in posts[postid]['title'].lower()):
                matches[postid] = posts[postid]
        return matches

    @classmethod
    def delete(cls, postid):
        posts = Post.load()
        if posts.get(postid):
            del posts[postid]
            with open(filename, 'w') as f:
                json.dump(posts, f)
        else:
            print('Post id not found: {}'.format(postid))
