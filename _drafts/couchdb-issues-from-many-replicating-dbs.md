---
layout: post
title: CouchDB Issues from Many Continuous Replications
---
CouchDB has issues arising from having many databases performing continuous replications. Even if new documents aren't being inserted into the database, it causes CPU utilization to surge. This post provides code for recreating this issue and confirming the issue.

I'll be using Safari on Mac OS X Yosemite (10.10) to perform this experiment since Safari easily allows webpages from the filesystem to access localhost without a CORS violation (try the same source code file on Firefox with default settings and you won't be permitted to run the code properly).

The following Github hosted gist contains the HTML and Javascript code needed to run the experiment. It references external Javascript libraries so it requires Internet access.



## Problems Identified ##

* CouchDB requires a file descriptor for a database with continuous replication even when the database is not being modified.
* When CouchDB has adequate file descriptors for running many continuous replications, CPU utilization surges.

## Solutions ##

Ideally, these solutions should be addressed in the CouchDB source code. Alternatively, we can utilize an external application to trigger one time replications each time a database is modified.
