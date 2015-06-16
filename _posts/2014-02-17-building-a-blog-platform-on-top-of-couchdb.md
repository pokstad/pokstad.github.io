---
layout: post
tags: [couchdb]
---
In building this site, I wanted to accomplish something unique. Not just another blog hosted on Wordpress/Blogger/Tumblr. Also, I was bored of all the server side options (Django/Flask/Node). They all had weaknesses, whether it be the limitations of creating new code or the server technology delivering the HTTP responses. I ultimately planned to experiment by building a blog platform on top of CouchDB.

I've been meaning to develop a public website powered by CouchDB for some time. Unfortunately, CouchDB has not attained the notoriety it deserves. It excels in serving as a database/hosting platform for the following reasons: (1) HTTP JSON API out of the box and (2) user account & session management out of the box.
It's so easy to stand up a CouchDB based website, that you actually don't need to write any code on the server side to get it working (more on that later...). In fact, you can write 99% of your website's logic on the browser side in Javascript. I like to call this type of architecture <strong>Heavy Client Side Architecture</strong>. This architecture attempts to push as much work as possible to the under utilized client. This leaves the server side portion with enforcing rules to make sure users don't abuse data.
Here's an example of how to store a blog post using CouchDB's JQuery library:

<pre><code>
var siteDB = $.couch.db("site");
// "site" is the name of our database.
// A CouchDB instance can host many databases.
var blogPost = {
   "type": "post",
   "title": "Pushing work to the lazy client",
   "tags": [
       "code",
       "webapp",
       "couchdb",
       "javascript",
       "ajax",
       "bootstrap"
   ],
   "epoch": 1377796492.916,
   "summary": "",
   "body": "Hi",
   "category": "code"
};
// notice how blogPost is a JSON document. Easy
// to add new fields later.
siteDB.saveDoc(doc,{success:function(resp){
 console.log(resp);
 // resp indicates if the save was successful and will
 // return the current ID and REV for the document
}});
</code></pre>

Here's the caveat: CouchDB databases are public by default. This means that anyone who can reach my DB by HTTP will be able to manipulate and view my data. Since this is my personal blog/site, I don't want anyone else other than myself modifying content. CouchDB has two solutions for this problem: (1) user/group permissions or (2) update validation methods. I use the latter.
Update validation methods are special pieces of code that run on the CouchDB server. The method returns true if a change being made to the database is permitable, otherwise it returns false. Here's the update validation method for my site:

<pre><code>
function(newDoc, oldDoc, userCtx, secObj){
 // userCtx is an object representing the current
 // user requesting to update the document
 if(userCtx.name != "pokstad"){
  throw({forbidden:"This isn't your website."});
 }
}
</code></pre>

How does CouchDB store these special methods? In CouchDB there is a special document type known as a "design document". A design document enforces rules through update validation methods and also does special tasks like create map/reduce views, shows, update methods, and more. Here's a simple design doc being saved into the database to enforce these rules:

<pre><code>
var design_doc = {
   "_id": "_design/site",
   "validate_doc_update": "function(newDoc, oldDoc, userCtx, secObj){if(userCtx.name!=\"pokstad\"){throw({forbidden:\"This isn't your website.\"});}}",
   "language": "javascript",
}
siteDB.saveDoc(design_doc);
</code></pre>

All design docs start with "_design/". Also, only admin users can update a design doc.
At this point, CouchDB is a simple key/value store. We put in a document with an ID (or get assigned one) and when we want to retrieve it we provide the same ID to CouchDB. For example, <code>http://pokstad/db/site/abc123</code> is the URL to a document with an ID of <code>abc123</code> in the database <code>site</code> with a URL prefix of <code>http://pokstad/db/</code>. What if we don't know the ID but want to retrieve specific data?

<h3>CouchDB Views</h3>

CouchDB is famous (maybe even infamous) for not using SQL but instead Map/Reduce to query unstructured data. It works like this:

1. Define a map function. This map function will run on every document in the current database. The map function will emit a key-value pair zero-to-many times for each document.
1. **OPTIONALLY**: define a reduce method. This method will run on all documents with the same key. This is useful for performing aggregate functions, like calculating counts, sums, averages, etc.

Here's a really simple example: How to list all documents of type "post":

<pre><code>
function(doc) {
  if (doc.type == "post") {
    // emit's first arg is the key,
    // and second arg is the value
    emit("post",doc.title);
  }
}
</code></pre>

More generically, we can create a method for listing all the different document types and their respective counts:

<pre><code>
function(doc) {
    emit(doc.type,null);
    // There's no need to emit a value if you want
    // the entire document. It's a simple matter of
    // asking the view API to include the document.
  }
}
</code></pre>

This is put into a design document like so:

<pre><code>
{
   "_id": "_design/site",
   "validate_doc_update": "function(newDoc, oldDoc, userCtx, secObj){if(userCtx.name!=\"pokstad\"){throw({forbidden:\"This isn't your website.\"});}}",
   "language": "javascript",
   "views": {
       "doc_types": {
           "map": "function(doc) {emit(doc.type,null);}",
           "reduce": "_count"
       }
   }
}
</code></pre>

Notice the <code>_count</code> listed underneath the map method. This is a built in reduce method that will calculate the total count for a group of values with the same key. In this example, it will tell us the number of posts in the site.
What if you want to order the posts by publishing date? Then you will need to emit the date as part of the key. CouchDB automatically sorts map views by key value. In our data structure, we have a field called epoch which represents the total seconds since the UNIX epoch:
<pre><code>
function(doc) {
  if (doc.type == "post" && doc.epoch != null) {
    emit(doc.epoch,doc.title);
  }
}
</code></pre>

There are plenty of limitations to map/reduce views, but the important thing is that they are fast and when data incrementally changes, the view incrementally updates. This is great for large datasets that change frequently. Most of the limitations of this design can be remedied by doing extra logic on the client side (like performing multiple requests and then performing computations on those requests).