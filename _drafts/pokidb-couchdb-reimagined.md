---
layout: post
title: PokiDB: CouchDB Reimagined
tags: [software, couchdb, databases, golang]
---

CouchDB has been one of my favorite databases, but it's also been one of my biggest
disappointments.

To understand my initial optimism, check out my Quora answer to
["What is the essence of CouchDB"](https://www.quora.com/What-is-the-essence-of-CouchDB):

> CouchDB is of the web.
> 
> Damien Katz (original creator of CouchDB) said in an interview that CouchDB
> felt like something in the natural world that he discovered rather than
> invented. The creation and continued evolution of CouchDB is something that
> has a life of its own.
> 
> Everything in CouchDB is designed around being scalable. This means not
> supporting single server actions that are slower than O(log(n)). Everything is
> stored in B-Trees that are easy to append data to and fast to look up and
> indexes are updated incrementally on each access. (Note: The benefits of
> scaling will become more evident as BigCouch, a.k.a. IBM Cloudant's CouchDB,
> is merged into Apache CouchDB 2.0 to support multi-server CouchDB.)
> 
> Everything in CouchDB is web-accessible by being RESTful and JSON-based. This
> means that it can be accessed from browser side Javascript. This is so true
> that the management tool is actually a web app (Futon/Fauxton) written in
> purely HTML and Javascript. It also means that you don't need special database 
> drivers to access CouchDB. If you have a library for handling HTTP requests,
> then you can access CouchDB. Stuck behind an HTTP proxy? You can still access
> your database.
> 
> Probably the biggest thing that makes CouchDB what it is, is master-master
> replication. CouchDB is a peer-to-peer app. It allows data to propagate
> virally the same way that rumors spread via word of mouth. The full potential
> of CouchDB has yet to be tapped into. A Javascript clone of CouchDB, called
> PouchDB, was created to be compatible with the same replication API. This
> allows a user to pull their data off the server and store it locally in the
> browser. Mobile libraries Couchbase Lite and Cloudant Sync are also compatible 
> with the replication API so that data can be pulled and pushed from mobile
> devices. Couchbase Server uses the replication API as a gateway between their
> non-HTTP-based database and the HTTP world.
> 
> CouchDB's entire API is a web API. So if you really wanted to, you could take
> any server side environment (e.g. Node, Python, Perl, Go, Java, Ruby, etc...)
> and emulate the same API to behave the same way and function with existing
> CouchDB servers. Theoretically, you could take an existing datastore (e.g.
> Google App Engine, Amazon Dynamo, MongoDB, MySQL) and put a "CouchDB layer" on
> top of it to make it compatible with other CouchDB servers. That is really
> cool.

Through my experience with both CouchDB and Go programming, I've come to the conclusion that things could be done differently... and by differently I mean better.

## Pitfalls

That was written back at the end of 2014. Since then, I've learned some lessons about Couch.

###  Couch Apps

Couch Apps were one of the big promises that attracted many initial users, but it was
[secretly deprecated](http://mail-archives.apache.org/mod_mbox/couchdb-user/201702.mbox/%3CF694E5A0-4BFC-4CB5-8CF8-6FEE44099D19@apache.org%3E).
Read through the mailing lists and you'll see recommendations to avoid using the `_show` and
`_list` transformations that were [hyped so well in the CouchDB: Definitive Guide] (
http://guide.couchdb.org/editions/1/en/show.html). Some CouchApp users became concerned and
voiced frustration:

- [the future of couchapps](http://mail-archives.apache.org/mod_mbox/couchdb-user/201505.mbox/%3cCADdZc95CgPfjh74CSS=_0M5qy4M2-Kw9H3EJ4ZK50Y2cPBBW1A@mail.gmail.com%3e)
- [how couchapps fit into the couchdb story](http://mail-archives.apache.org/mod_mbox/couchdb-user/201505.mbox/%3cCAPMhwa4mc=RMSPHcabSB0gPL6LaZi0MbDSEnosgeW_0achXEqQ@mail.gmail.com%3e)

At the end of the day, the core CouchDB team recommended using dedicated web server code to
access and present data from CouchDB. That's all fine and dandy, but then why are we using this
HTTP based protocol that is easily accessible from web browsers (but not the most performant for
use from a backend service)? That leads me into the next issue...

### JSON HTTP API

While the JSON API was bleeding edge at the time, it has begun to show its age. HTTP 1.1 doesn't
expose the performance benefits of HTTP2, such as multiplexing requests, proactively pushing
responses, and reducing overhead.

Better yet, gRPC could allow for bi-directional streams between CouchDB and a client. The ability
to push streams of data between peers would be awesome possum. Even better yet: use protobuf
as the message format to reduce the overhead of repeitive field definitions.

### No Schema

One of the first things people enjoy about CouchDB is the ability to dump JSON messages with
any arbitrary structure. It's nice because you add new document types without having to update
a database schema. In theory, this utopian freedom seems liberating, but in practice it's frustrating.

My primary concern with no schemas is human error. As developers, we need feedback that the
way we are interacting with the database is valid. With no schemas, there is a lack of feedback.
While coordinating with other developers, or even just working on a solo project, having a way to
guarantee that types of data in a database fits a understood pattern is critical.

In my mind, there is no doubt that some enforcement of schema's is necessary, but the more
important question is: how much? We, as developers, want freedom to insert whatever we want
into the database. Over time though, we start to recognize patterns and understand where that
freedom is not wanted. Ideally, a good CouchDB schema enforcement would rely on the
designation of required and optional fields. Something like JSON schemas could accomplish this.
Maybe JSON schemas are overkill. Protobuf definitions are much simpler and allow for deprecating
fields over time.

### Erlang

Erlang has always been hyped as the special sauce of CouchDB. "It's designed for distributed
systems" is what we always hear, and it's true. Erlang shines in distributed systems. The problem
though, has been the fact that CouchDB historically was a single node system that scaled via an
HTTP based protocol. The Erlang VM was only leveraged for a single node (not sure if that's the
case for CouchDB 2.0).

Perhaps the biggest issue with Erlang has been the aversion of CouchDB users to dive into the
code base. If the project were reimagined today, it would almost certainly be written in an easier to
onboard language like Go or Elixir. Looking at many of the newer database projects, there has
been a surge in new codebases based on Go.

There is also the strange quirk that view and transform functions are written in Javascript. The
CouchDB community has strong crossover ties to the Javascript peeps. Take a look at PouchDB,
and Mustache.js. It probably would have made the most sense to write CouchDB in Node.js given
the community that ended up embracing CouchDB the strongest. Max Ogden, one of the most
influential CouchDB hackers, ended up writing a new database, [Dat](https://datproject.org), in
Node.js that was heavily inspired by CouchDB.

### Big Couch (a.k.a. CouchDB 2.0)

The current state of CouchDB has been the result of a major refactoring/merging
of code from IBM's acquired Cloudant service. This signaled a new milestone in
CouchDB's lifetime. It was no longer simply a single node product, but now a
very complex system designed for enterprise usage.

## Poki: CouchApps Reimagined

Poki is a new kind of database with a modest goal: become the database/webserver of choice for small independently owned websites. The goal of this tool is not to become the infrastructure of large corporations. It is designed to enable simple solutions for communities that wish to be self reliant. Self reliance means not depending on a spyware infested social media company to provide your services.

The core design principles of Poki:

- Poki Apps are the core feature, everything else supports their purpose
- Database and app design is centered around user data
- Pluggable architecture that allows for sharing of apps and submodules
- A single language for all components: i.e. server, apps, and submodules
- Single process design - all pluggable components operate in the same process space

The database improves upon CouchDB in the following ways:

- Pure Go - written in pure Go to leverage all tooling benefits and improve onboarding 
- Library first - designed for easily embedding in other Go apps, similar to BoltDB
- Authentication/View/Show/Validate/Filter functions are implemented in the same process via:
	- Closures - for experienced Go devs - simliar to BoltDB's transaction model
	- Compiled Go plugins - for non-devs - allow easy sharing of Poki Apps within community without writing code
- Multiple pluggable interfaces based upon core Go API
	- Protobuf based gRPC interface
	- JSON based HTTP2 interface
- Replication protocol
	- available for reuse through libraries - e.g. allows writing adapters that can perform backups
 
### Poki: Go Interface Draft

How should this interface look to a Go dev embedding this into a program? Some initial thoughts:

#### Documents

A document is a collection of bytes with the following attributes:

- ID (database unique) - user provided (or database generated) UUID
- Revision - a crypto hash of the data
- content type - is this JSON, PNG, HTML, JSON, Protobuf? Useful to serve resources.

```go
package poki

type ContentType string

type Document struct {
	ID 		string
	Rev 	[]byte
	Data 	[]byte
	Type  ContentType
}
```

#### Databases

A database is a sequential collection of revisions. It is possible to iterate over every single document revision in order. This is what makes replication possible: a time series log of documents.

```go
db, err := NewServer("/home/poki").Get("users")
If err != nil { return err }

err = db.ForEachRev(func(d poki.Doc) error {
	fmt.Printf("Doc: %+v", d)
	return nil
})
```

You can also iterate over every document (which implicitly only iterates over the last revision for each ID) with `ForEachDoc`.

#### Servers are composed of DB's

A server is essentially a collection of databases and the access controls to them. Servers control access to databases through the use of a pluggable authentication modules.

```go
type Auther interface {
	Authenticate() (UserContext, error)
}

srv := NewServer("/home/poki")
srv.SetAuth(
```

