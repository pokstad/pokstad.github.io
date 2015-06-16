---
layout: post
tags: [couchdb]
---
If you try modifying the CouchDB configuration file to bind to port 80, you will not be able to access the server. This is because non-root processes cannot bind to port numbers lower than 1024 (these are "privileged" port numbers).

I tried to elevate CouchDB's port assignment rights using the [CAP_NET_BIND_SERVICE method described here](http://stackoverflow.com/questions/413807/is-there-a-way-for-non-root-processes-to-bind-to-privileged-ports-1024-on-l), but it didn't work.

There are a couple of other ways to run CouchDB on port 80. The less risky version is to use iptables to reroute IP traffic on port 80 to port 5984. This is a great choice IF you don't want to use vhosts. From what I've seen, vhosts stop working when the traffic they receive is forwarded by an iptable rule.

Since I want to use vhosts, I'm going to suggest the super sketchy idea of running CouchDB as ROOT. This isn't a horrible idea on my system since all I have is a CouchDB service. If anyone infiltrated my server as the CouchDB user, they would be able to do just as much damage as if they were root. However, if I was running other services and had data that was kept inaccessible from the CouchDB user, I would reconsider this approach.

To run as root, we will need to modify the CouchDB boot configuration file used to configure the environment when the service is started at boot.

If you built CouchDB from source, the file can be found here:

`sudo vi /usr/local/etc/default/couchdb`

Inside, you will replace the line `COUCHDB_USER=couchdb` with `COUCHDB_USER=root`.

If you installed CouchDB on Ubuntu using apt-get, you can find the file here:

`sudo vi /etc/init/couchdb.conf`

Inside, you will replace the line `exec su couchdb -c /usr/bin/couchdb` with `exec su root -c /usr/bin/couchdb`.

Then, you will have to modify the CouchDB application specific config file:

`sudo vi /usr/local/etc/couchdb/local.ini`

Inside, you will change the line `port = 5984` to `port = 80`.

Then, you just need to restart the service:

`sudo /etc/init.d/couchdb restart`

**NOTE:** If you want to enable SSL, you will need to add the line `port = 443` underneath the `[SSL]` section so that it runs on a standard port.

**DOUBLE NOTE:** There is a safer way to accomplish this using authbind on Ubuntu. I'll cover that in a future post.