# yurumikuji

[![PyPI version](https://badge.fury.io/py/yurumikuji.svg)](https://badge.fury.io/py/yurumikuji)
[![Python Versions](https://img.shields.io/pypi/pyversions/wandbox_api.svg)](https://pypi.org/project/yurumikuji/)

[kamidana][] slack additonal

## Usage

```sh
$ pip install yurumikuji
$ echo "SLACK_TOKEN=<your token>" > .env
$ kamidana --additionals=yurumikuji.yurumikuji sample/profile.j2
https://secure.gravatar.com/avatar/a7614593f3f6f46b73da348c89beba81.jpg?s=512&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0023-512.png
https://secure.gravatar.com/avatar/a7614593f3f6f46b73da348c89beba81.jpg?s=512&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0023-512.png
active
```

sample/profile.j2

```j2
{{ ("srz_zumix" | slack_user_id | slack_user_info).profile.image_512 }}
{{ ("srz_zumix" | slack_user_id | slack_user_profile).image_512 }}
{{ "srz_zumix" | slack_user_id | slack_user_presence }}
```

## Features

### Filter

|name|usage|detail|slack required scope|
|:--|:--|:--|:--|
|slack_user_id|\<user_name\> \| slack_user_id |user name\|real_name\|display_name to user_id|users:read|
|slack_user_presence|\<user_id\> \| slack_user_presence |get user presence|users:read|
|slack_user_info|\<user_id\> \| slack_user_info |get user info|users:read|
|slack_user_profile|\<user_id\> \| slack_user_profile |get user profile|users.profile:read|
|slack_user_info_by_email|\<user_email\> \| slack_user_info_by_email |get user info|users:read.email|
|slack_usergroup_id|\<usergroup_name\> \| slack_usergroup_id |usergroup name to usergroup_id|usergroups:read|
|slack_usergroup_member_ids|\<usergroup_id\> \| slack_usergroup_member_ids |get usergroup member user ids|usergroups:read|
|slack_usergroup_member_infos|\<usergroup_id\> \| slack_usergroup_member_infos |get usergroup member user info|usergroups:read|
|slack_usergroup_member_infos|\<usergroup_id\> \| slack_usergroup_member_infos |get usergroup member user info|usergroups:read|
|slack_search|\<search_query\> \| slack_search | search message |search:read|

[kamidana]:https://github.com/podhmo/kamidana
