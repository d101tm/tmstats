#!/bin/bash
mysql -hmysql.d101tm.org -ud101tmorg  -pM8-ynvHQ d101tm_org --table <<FOO
select  posts.post_title, users.display_name, posts.post_modified from wp_zqr3uq_postmeta postmeta inner join wp_zqr3uq_users users on postmeta.meta_value = users.id inner join wp_zqr3uq_posts posts on posts.id = postmeta.post_id where meta_key = '_edit_last' and post_type = 'page' order by posts.post_modified;
FOO
