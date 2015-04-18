---
layout: post
title: Mo Databases Mo Problems
---
CouchDB has some great strengths, but along with those are accompanying weaknesses. One of the greatest faults of CouchDB is the permission model for documents in a database. Every database is either entirely readable by a user or not readable at all. Read permissions cannot be enforced on a per-document basis. So how do you enforce privacy of a single user's data? One answer is the Database-Per-User model.

Database-Per-User is exactly what it sounds like. Every user in your system gets their very own database to call their own and maintain privacy of data. However, this design also introduces a number of challegnes. As a famous rapper once said: "Mo databases Mo problems".

## Issues with Mo Databases ##

By default, we want to keep data in as few databases as possible. Why?

1. *CouchDB views cannot span databases*  - This is a really important point because any type of query that must be performed over X databases must be done X times.
1. *There are more databases to choose from* - Since there are many more databases, a system must be developed to determine which database to use when. In a database-per-user design, a simple solution is to use a database name that maps to a username so that a user's database can be found easily.
1. *Complicates backup strategies and replication* - Now instead of safeguarding the data of one database, we must now worry about backing up many databases. If you have thousands of users, this means you will need to worry about backing up each individual user's database. When we have a single database, it is very simple to backup using CouchDB's built in replication. Try this with thousands of databases and you will find that CPU utilization will be sky high and you will burn through all of your available file descriptors for open database files and sockets.

## Design ##

There are a number of design components needed to address these challenges:

* A method for monitoring user documents for specific criteria to trigger database creation.
* A convention for tracking which databases belong to which users.
* A permission model to designate which users are allowed to access each database. Also a permission model for admin's to help users with their data.
* A way to conveniently merge databases into a single database for backup and global indexing. We also need to be able to perform the inverse procedure: recreate the user databases back from the global database.

### Permissions ###

The whole point of this setup is to protect the privacy of data, so we need to assign permissions appropriately. Is each database only viewable by the owning user? Do "friends" of a user also have permission to view the database? Do moderators/admin need access to user databases?

The simplest permission model you should adopt is that each database should listen 

## The Dilemma ##

So now we've got these user databases that permit privacy, but what did we lose in the process? It turns out, we lost a lot. In CouchDB, views can only span a single database, which means that we cannot do useful analytics across all of our user's data. 

Another downfall to this strategy is managing backups and replicated data sets. Instead of backing up one database, we now have to manage MANY databases.

## Alternative Projects ##

These projects were written to aide with db-per-user usage:

* MEOW
* MEOW
* MEOW

## Follow Up ##

There is another solution to get around this issue, although it adds some complexity. Look for part 2 of my series.