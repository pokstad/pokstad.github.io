---
layout: post
title: PokiDB CouchDB Reimagined
tags: [software, couchdb, databases, golang]
--- 

CouchDB has been one of my favorite databases, but it's also been one of my biggest disappointments.

To understand my initial optimism, check out my Quora answer to ["What is the essence of CouchDB"](https://www.quora.com/What-is-the-essence-of-CouchDB):

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

Couch Apps were one of the big promises that attracted many initial users, but it was [secretly deprecated](http://mail-archives.apache.org/mod_mbox/couchdb-user/201702.mbox/%3CF694E5A0-4BFC-4CB5-8CF8-6FEE44099D19@apache.org%3E). Read through the mailing lists and you'll see recommendations to avoid using the `_show` and `_list` transformations that were [hyped in the CouchDB: Definitive Guide](http://guide.couchdb.org/editions/1/en/show.html). Some CouchApp users became concerned and voiced frustration:

- [the future of couchapps](http://mail-archives.apache.org/mod_mbox/couchdb-user/201505.mbox/%3cCADdZc95CgPfjh74CSS=_0M5qy4M2-Kw9H3EJ4ZK50Y2cPBBW1A@mail.gmail.com%3e)
- [how couchapps fit into the couchdb story](http://mail-archives.apache.org/mod_mbox/couchdb-user/201505.mbox/%3cCAPMhwa4mc=RMSPHcabSB0gPL6LaZi0MbDSEnosgeW_0achXEqQ@mail.gmail.com%3e)

At the end of the day, the core CouchDB team recommended using dedicated web server code to access and present data from CouchDB. That's all fine and dandy, but then why are we using this HTTP based protocol that is easily accessible from web browsers (but not the most performant for use from a backend service)? That leads me into the next issue...

### JSON HTTP API

While the JSON API was bleeding edge at the time, it has begun to show its age. HTTP 1.1 doesn't expose the performance benefits of HTTP2, such as multiplexing requests, proactively pushing responses, and reducing overhead.

Better yet, gRPC could allow for bi-directional streams between CouchDB and a client. The ability to push streams of data between peers would be awesome possum. Even better yet: use protobuf as the message format to reduce the overhead of repeitive field definitions.

### No Schema

One of the first things people enjoy about CouchDB is the ability to dump JSON messages with any arbitrary structure. It's nice because you add new document types without having to update a database schema. In theory, this utopian freedom seems liberating, but in practice it's frustrating.

My primary concern with no schemas is human error. As developers, we need feedback that the way we are interacting with the database is valid. With no schemas, there is a lack of feedback. While coordinating with other developers, or even just working on a solo project, having a way to guarantee that types of data in a database fits a understood pattern is critical.

In my mind, there is no doubt that some enforcement of schema's is necessary, but the more important question is: how much? We, as developers, want freedom to insert whatever we want into the database. Over time though, we start to recognize patterns and understand where that freedom is not wanted. Ideally, a good CouchDB schema enforcement would rely on the designation of required and optional fields. Something like JSON schemas could accomplish this. Maybe JSON schemas are overkill. Protobuf definitions are much simpler and allow for deprecating fields over time.

### Erlang

Erlang has always been hyped as the special sauce of CouchDB. "It's designed for distributed systems" is what we always hear, and it's true. Erlang shines in distributed systems. The problem though, has been the fact that CouchDB historically was a single node system that scaled via an HTTP based protocol. The Erlang VM was only leveraged for a single node (not sure if that's the case for CouchDB 2.0).

Perhaps the biggest issue with Erlang has been the aversion of CouchDB users to dive into the code base. If the project were reimagined today, it would almost certainly be written in an easier to onboard language like Go or Elixir. Looking at many of the newer database projects, there has been a surge in new codebases based on Go.

There is also the strange quirk that view and transform functions are written in Javascript. The CouchDB community has strong crossover ties to the Javascript peeps. Take a look at PouchDB, and Mustache.js. It probably would have made the most sense to write CouchDB in Node.js given the community that ended up embracing CouchDB the strongest. Max Ogden, one of the most influential CouchDB hackers, ended up writing a new database, [Dat](https://datproject.org), in Node.js that was heavily inspired by CouchDB.

### Big Couch (a.k.a. CouchDB 2.0)

The current state of CouchDB has been the result of a major refactoring/merging of code from IBM's acquired Cloudant service. This signaled a new milestone in CouchDB's lifetime. It was no longer simply a single node product, but now a very complex system designed for enterprise usage.

## Poki: CouchApps Reimagined

Poki is a new kind of database with a modest goal: become the database/webserver of choice for small independently run websites. The goal of this tool is not to become the infrastructure of large corporations. It is designed to enable simple solutions for communities that wish to be self reliant. Self reliance means not depending on a spyware infested social media company to provide your services.

The core design principles of Poki:

- Poki Apps are the core feature, everything else supports their purpose
- Poki Apps are centered around user data (similar to Parse, Firebase, iCloud Kit)
- Type safety - leverage Go static type safety for database documents
- Pluggable architecture that allows for minimal footprint while enabling the sharing of apps and submodules
- A single language for all components: i.e. server, apps, and submodules
- Single process design - all pluggable components operate in the same process space
- Maintainability over performance - a decision to improve performance should never be made if it sacrifices maintainability (e.g. readability and complexity)

The database improves upon CouchDB in the following ways:

- Pure Go - written in pure Go to leverage all tooling benefits and improve onboarding 
- Library first - designed for easily embedding in other Go apps, similar to BoltDB
- Authentication/View/Show/Validate/Filter functions are all implemented in the same process via:
	- Closures - for experienced Go devs - simliar to BoltDB's transaction model
	- Compiled Go plugins - for non-devs - allow easy sharing of Poki Apps within community without writing code
- Multiple pluggable interfaces based upon core Go API
	- Protobuf based gRPC interface
	- JSON based HTTP2 interface
- Replication protocol
	- available for reuse through libraries - e.g. allows writing adapters that can perform backups
 
### Poki: Go Interface Draft

How should this interface look to a Go dev embedding this into a program? Some initial thoughts:

Everything should be pluggable via interface. Out of the box, Poki will provide persistence via BoltDB in the local filesystem, but it is entirely up to the user to replace that with an abstraction to another type of datastore (e.g. RAM or SQL backed).

```go
type Datastore interface {
	StoreDocRev(poki.Doc) (string, error)
	StoreViewMap(name, key string, val []byte) (string, error)
	StoreViewReduce(name, key, reduce []byte) (string, error)
}
```

```go
srvr := poki.NewServer(boltdb.Store("/database"), poki.OpenAuth())
```

All servers also require a form of database autherization. The simplest (and least secure) way to move forward is to use `OpenAuth` to simply allow open access to everyone.

To access information, a Poki server utilizes a pluggable autherization modules that authorizes a user access to specific databases and provides that database contextual information about the user accessing it.

```go
package poki

// UserCtx represents the entity requesting access to a resource. The zero value
// represents an unauthenticated user (anybody/nobody).
type UserCtx struct {
	ID		string
	Roles	[]string
}

// AuthDB grants access to a database based on the user context. Returning true
// indicates the user is authorized to access the database resource.
type AuthDB interface {
	AutherizeDB(db string, uctx UserCtx) (bool, error)
}

// OpenDBAuth allows DB access to anyone
type OpenDBAuth struct{}

// AutherizeDB ignores database and user context and simply authorizes access
func(OpenDBAuth) AutherizeDB(db string, uctx UserCtx) (bool, error) {
	return true, nil
}
```

For example, using a custom authenticator `myAuther` to validate username and password access to a database:

```go
srvr := poki.NewServer(boltdb.Store("/database"), OpenDBAuth())

// AccessDB(db string, uctx UserCtx) (poki.DB, error)
db, err := srvr.AccessDB("databaseX", myAuther.Authenticate(user, password))
```

Admins can create and remove DBs:

```go
func(s Server)CreateDatabase(name string, uctx UserCtx) (DB, error) { /*...*/ }
```

Once authorized to access a database, document CRUD operations become available:

```go
var (
	id		string
	data	[]byte
	doc		poki.Doc
)

// Create only works if the ID doesn't already exist
doc, err := db.Create(id, data)

// Read can specify a revision or implicitly fetch the latest revision
doc, err := db.Read(id [, rev])

// Update requires the current revision to create the next revision
doc, err := db.Update(id, rev, data)

// Delete is the same as: db.Update(id, rev, nil). Deletions are revisions.
doc, err := db.Delete(id, rev)
```

Poki's database model is essentially a key-value store. Each document is represented by an ordered list of revisions. Each revision is keyed by the crypto hash of the underlying payload. The payload can be any Go type capable of being serialized by the [Gob library]().

```go
package poki

// Doc 
type Doc interface {
	ID			string	// unique key in database
	Revs		[]Rev		// ordered list of revs
}

// Rev 
type Rev interface {
	Hash string			// crypto hash (SHA256) of Data when gob encoded
	Data interface{} // arbitrary gob encodable data
}
```

*Notice that `string`'s are used instead of `[]byte` slices. This is intentional to keep data immutable when passing documents between Couch App functions.*

Gob is used to keep things simple and idiomatic. By using an encoder designed for Go types, we are able to utilize simple Go primitives (e.g. integers, strings, byte slices, maps) as our document data. Protobuf and JSON don't allow for this simplicity.

#### Databases

A database is a sequential collection of revisions. It is possible to iterate over every single document revision in order. This is what makes replication possible: a time series log of documents.

```go
import "github.com/pokstad/poki"

func main() {
	db, err := poki.NewServer("/home/poki").Get("users")
	If err != nil { return err }

	err = db.ForEachRev(func(d poki.Doc) error {
		fmt.Printf("Doc: %+v", d)
		return nil
	})
}
```

You can also iterate over every document (which implicitly only iterates over the last revision for each ID) with `ForEachDoc`.

##### Replication

The secret sauce of databases are their ability to replicate bi-directionally. For now, this is kept simple by sending all docs since a known checkpoint.

```go
type Filter func(poki.Doc) bool

type Syncer interface {
	Transmit(ctx context.Context, sinceRev string, f Filter) (<-chan poki.Doc, error)
	Receive(ctx context.Context, <-chan poki.Doc, f Filter) error
}

func (db DB) Pull(ctx context.Context, p Syncer) (ReplStats, error) {/*...*/}
func (db DB) Push(ctx context.Context, p Syncer) (ReplStats, error) {/*...*/}
```

### Apps

Porting the concept of Couch Apps to Poki while maintaining type safety is not easy, especially since Golang doesn't support generics. Since any Gob encodable type is allowed in Poki, we allow the empty interface as the primary medium for App functions.

#### Views

Views are essentially the same as CouchDB. They are created and accessed via database methods:

```go
package poki

// Mappers maps a document to key/value pairs
type Mapper interface {
	Map(poki.Doc, func(string, interface{})) // func param is to emit key/value
}

// Reducer will take a chunk of mapped key/value pairs and merge them into a
// meaningful value
type Reducer interface {
	Reduce(key string, vals interface{}, rereduce bool) interface{}
}

type View interface {
	Mappings(startKey, endKey string) map[string][]interface{}
	Reducings(startKey, endKey string) map[string]interface{}
}

func(db DB) Index(name string, m app.Mapper, r Reducer) error { /*...*/ }
func(db DB) Query(name string) (View, error) { /*...*/ }
```

To query a database view:

```go
v, err := db.View("examples")
values, err := v.Mappings(key1, key2) // key1 through key2 (key2 may be empty)
```

#### Validating Writes

Simple... right?

```go
package poki

type DBCtx struct{
	AdminRoles	[]string
	Admins		[]string
	Users			[]string
	UserRoles	[]string
}

type Validator interface {
	Validate(uctx UserCtx, dbCtx DBCtx, prev poki.Doc, next poki.Doc) bool
}
```

## What's next?

Write an initial implementation and iterate. One of the biggest issues I see with the proposed draft is the lack of type safety. The excessive use of interfaces due to lack of generics is troublesome. Experimenting is needed to find out how to expose the Poki App API while maintaining strong type safety. Some additional gaps I want to cover:

- Transform functions (CouchDB's show and list) with caching of transforms
