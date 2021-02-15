# Instagram Crawler
This is a small tool with a CLI that allows you to collect some information and data about the user, it`s posts, stories, highlights and IGTV content of an Instagram account.

## Table of Contents
- [Instagram Crawler](#instagram-crawler)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Getting Started](#getting-started)
    - [Direct Usage](#direct-usage)
    - [CLI](#cli)
      - [Parameters](#parameters)
  - [Build With](#build-with)
  - [Author](#author)

## Installation 
```
mkdir InstaProject
cd InstaProject
python3.8 -m venv venv
. venv/bin/activate
git clone https://www.github.com/RHabby/InstaCrawler.git
cd InstaCrawler/
pip install -r requirements.txt
touch main.py # run this file
```


## Getting Started
### Direct Usage 
```python
# InstaProject/InstaCrawler/main.py
from app.insta_crawler.insta import InstaCrawler

# Should be enough to paste values of 'ig_did' and 'sessionid'
# example: "ig_did=XXXXXXXX-YYYY-CCCC-AAAA-ZZZZZZZZZZZZ; sessionid=1111111111111111111111111;"
cookie = "ig_did=XXXXXXXX-YYYY-CCCC-AAAA-ZZZZZZZZZZZZ; sessionid=1111111111111111111111111;"
insta = InstaCrawler(cookie=cookie)

post_url = "https://www.instagram.com/shortcode/"
user_url = "https://www.instagram.com/username/"

cookie_user = insta.get_cookie_user()
user_info = insta.get_user_user(url=user_url)
single_post = insta.get_single_post(url=post_url)
posts = insta.get_posts(url=user_url)
stories = insta.get_stories(url=user_url)
highlights = insta.get_highlights(url=user_url)
igtv = insta.get_all_igtvs(url=user_url)
followers = insta.get_followers(url=user_url)
followed_by_user = insta.get_folllowed_by_user(url=user_url)
```

### CLI
```
# /InstaCralwer

# cookie user 
python get_insta.py cookie-user \
--cookie="ig_did=XXXXXXXX-YYYY-CCCC-AAAA-ZZZZZZZZZZZZ; sessionid=1111111111111111111111111;"

# user info
python get_insta.py user-info \
--username="username" \
--cookie="ig_did=XXXXXXXX-YYYY-CCCC-AAAA-ZZZZZZZZZZZZ; sessionid=1111111111111111111111111;"

# single post
python get_insta.py post \
--url="https://www.instagram.com/(p OR tv)/shortcode/" \
--cookie="ig_did=XXXXXXXX-YYYY-CCCC-AAAA-ZZZZZZZZZZZZ; sessionid=1111111111111111111111111;"

# category
python get_insta.py category \
--content-type="(posts OR stories OR highlights OR igtv OR all)" \
--username="username" \
--cookie="ig_did=XXXXXXXX-YYYY-CCCC-AAAA-ZZZZZZZZZZZZ; sessionid=1111111111111111111111111;"

# followers
python get_insta.py followers \
--username="username" \
--cookie="ig_did=XXXXXXXX-YYYY-CCCC-AAAA-ZZZZZZZZZZZZ; sessionid=1111111111111111111111111;"

# followed by user
python get_insta.py followed-by-user \
--username="username" \
--cookie="ig_did=XXXXXXXX-YYYY-CCCC-AAAA-ZZZZZZZZZZZZ; sessionid=1111111111111111111111111;"
```

#### Parameters
* cookie — Cookie-string from your browser (ig_did and sessionid should be enough);
* url — link to the post or igtv: "https://www.instagram.com/[p OR tv]/shortcode/";
* username — user`s username

## Build With
* [Python 3.8.5](https://www.python.org/)

## Author
* **Ravil Khabibullin** — [rhabby](https://www.github.com/RHabby)
