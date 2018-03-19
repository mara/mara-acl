# Changelog

## 1.3.0
*2018-03-19*

- Replace sqlalchemy orm query logic with plain sql queries in order to avoid idling zombie connections
 

## 1.2.0
*2017-12-30*

- Adapt to changes in the [mara-db](https://github.com/mara/mara-db) package


## 1.1.0 
*2017-09-21*

- Adapt to changes in mara ui
- bug fix in invite new user feature


## 1.0.4 
*2017-04-20*

- Emails are always converted to lowercase before processing
- Adapted to mara ui changes

**required changes**

- Convert all users to lowercase with `update acl_user set email = lower(email);`


## 1.0.2 - 1.0.3
*2017-04-20*

- Login bug fix


## 1.0.1
*2017-04-15*

- Refactored login 
- Added function `user_has_permission`

## 1.0.0 
*2017-03-10* 

- Initial version

