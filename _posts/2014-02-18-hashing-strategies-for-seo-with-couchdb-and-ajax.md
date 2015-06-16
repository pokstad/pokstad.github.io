---
layout: post
tags: [couchdb]
---
One of the big problems with using a heavy client side web app is search engine optimization (SEO). Historically, search engines crawled the web and built their index using pre-rendered webpages. What we mean by pre-rendered is that web pages are generated (at least mostly) by a web server before the client (in this case the web crawler) receives them. This is much easier for the web crawler because it simply needs to download the HTML file and scan it to build an index.

Then, there was a historic shift in web apps when AJAX (Asynchronous Javascript And XML) techniques began appearing. AJAX allowed web apps to appear more responsive by only updating portions of the webpage instead of requiring full page refreshes to load new information. Initially this technique was used for interactive applications (e.g. chat apps) but then was used for just about everything.

The beauty of AJAX web apps is that you reduce the amount of work the server needs to do to serve a webpage. Instead of the traditional web server spending time to render a webpage on the fly for each page request, the AJAX approach is to define a strict API for the client side (web browser) to access the data and then render the data into a view on the client side.

This is where CouchDB excels. It already has an extremely well defined, well structured, high performance HTTP JSON based API. CouchDB is an ideal candidate for heavy client side architectures. It's as simple as: write all of your application logic in javascript on the front end, let CouchDB worry about security (permissions on who can do what and what type of data changes are allowable).

[Google has adopted an AJAX SEO process centered around the "hashbang".](https://support.google.com/webmasters/answer/174992?hl=en) Hashbang is a term for the hash symbol (#) and the bang symbol (!). In a URL, the hash symbol is traditionally used to indicate an anchor. An anchor is a special kind of link that doesn't leave the page. Instead, it would take you to a specific location in the current page. Using JQuery, we can override (HACK) this intended behavior to do things besides jumping to a section of the current page, such as dynamically load a page. Google took this approach one step forward and specified a protocol where the hashbang can be used to indicate AJAX web pages.

Ideally, what we'd like to do is adopt a hashbang URI scheme that works well with CouchDB. There are several resources we want to resolve to a hashbang URI (in order of importance):

1. Documents
2. Views
3. Shows
4. Lists

For now, we are going to focus on documents and views, since our client is rendering HTML we won't need shows and lists as much.

## CouchDB  Document URI For Hashbang URI
Any Javascript running on our webpage will have the ability to access any database hosted on the CouchDB server (same origin policy). So it would be very useful for our URI to include the database in order to route the request to the correct document.

### Document URI:

`#!/doc/{DB_NAME}/{DOC_ID}[&rev={REV_ID}]`

Here's the breakdown:

1. `#!` - hashbang
1. `/doc` - indicates we will be retrieving a document
1. `/{DB_NAME}` - the name of the database on the local CouchDB server
1. `/{DOC_ID}` - the UUID of the document
1. `[&rev={REV_ID}]` - **Optional:** the specific revision of the document

There is a small issue with regular expressions when it comes to detecting document ID's embedded in a slash delimited path: **document ID's can also contain slashes and ampersands.** To make sure we avoid missing the detection of the optional revision argument, we need to use a regex that is greedy for the revision portion and non-greedy for the doc ID:

**REGEX:** `#!/doc/([^/]+?)/(.+?)(&rev=(.+))?`

### View URI:

`#!/view/{DB_NAME}/{DESIGN_DOC_ID}/{VIEW_NAME}([&{ARG}={VAL}])*`

Here's the breakdown:

1. `#!` - hashbang
1. `/view` - we will be querying the database with a view
1. `/{DB_NAME}` - the local database
1. `/{DESIGN_DOC_ID}` - the design document containing the view
1. `/{VIEW_NAME}` - the name of the view
1. `([&{ARG}={VAL}])*` - **Optional:** the arguments to the view (e.g. reduce, keys, limit, etc...)

**Regex:** `#!/view/(.+?)/(_design/.+?)/(.+?)(&(.+?)=(.+?))*`

<pre><code>//javascript to the rescue:
</code></pre>

# Providing Escaped Fragments
Google specifies that crawlable hashbang webpages need to have a rendered HTML page (known as an escaped fragment) accessible by an alternative URL. CouchDB has the ability to generate transformations of data on the server side using show methods. We will write a show method to transform a JSON document into an HTML escaped fragment well suited for Google's webcrawler.

## Transforming Documents Into HTML Escaped Fragments with Show Methods

A show method within a design document generally looks like this:

{% highlight javascript %}
// design doc with example show method
{
	"_id":"_design/blog",
	"shows": {
		"escaped_fragment": "function(doc, req) { /*...*/ return responseObject;}",
	}
}
{% endhighlight %}

This show method is then accessible from the URL: `http://example.com/dbname/_design/blog/_show/escaped_fragment/somedocID`

What do we actually put inside the body of the "escaped_fragment" show method? If we don't want to spend a lot of time doing server side logic, we can make a huge (and dangerous) assumption that the client side pre-rendered the HTML properly and saved it into the document in a property field named "escaped_fragment".

<pre><code>// show method returning a pre-rendered HTML escaped fragment
function(doc, req) {
 return {
  'headers': {
      'Content-Type' : 'text/html',
  },
  body: doc.escaped_fragment
 };
}
</code></pre>

Why is this dangerous? If a malicious individual with access to write to the database is able to write any HTML they want, they can write nasty javascript code, include nasty plugins, or put rotten content on our website. In a production environment, we want a trusted agent performing this rendering operation. Since this is just a simple blog, I'm going to write a simple security rule in the update validation method to prevent others from accessing this property:
<pre><code>// show method returning a pre-rendered HTML escaped fragment
function(oldDoc, newDoc, userCtx, secObj) {
 if ("_admin" in userCtx.roles && "escapedFragment in newDoc &&
     newDoc.escaped_fragment != oldDoc.escapedFragment) {
  throw({forbidden:"Only admins may change the escaped fragment property."});
 }
}
</code></pre>

## Rewriting Escaped Fragment URLs to Point to Show Method
Google also specifies an alternative URL to point to an escaped fragment. Given a hashbang URL, the escaped fragment URL must appear as the following:

**Hashbang URL:** `www.example.com/ajax.html#!mystate`

**Escaped fragment URL:** `www.example.com/ajax.html?_escaped_fragment_=mystate`

There's a few ways to accomplish this. We could handle it externally with URL rewriting using a reverse proxy, like Nginx, but that's what everyone else does.

Let's be different ;-)

CouchDB has a built in URL rewrite feature. We can use this to rewrite `www.example.com/ajax.html?_escaped_fragment_=mystate` so that it points to our CouchDB show method. What's nice about this is that it's just another portion of the design document, which means it will replicate to other databases easily. Before we do that, we need to understand how the URL rewrite feature works. We'll go over how it's being used to host this site...

### CouchDB URL Rewriting
There is a special place in the design doc for a "rewrites" property:
<pre><code>{
    "_id":"_design/blog",
    "rewrites": [
     {
       "from": "/",
       "to": "index.html",
     }
    ]
}</code></pre>
In our design doc, we want to make sure that the root URL automatically rewrites to our index.html page so that people visiting pokstad.com will get the correct resource. We also want to be able to access the rest of CouchDB using a "/db/*" scheme. Finally, anything that doesn't match the other rules will attempt to retrieve an attachment from our master document (static).
<pre><code>{
    "_id":"_design/blog",
    "rewrites": [
     {
       "from": "/db/*",
       "to": "/../../../*",
     },
     {
       "from": "/",
       "to": "/../../static/index.html",
     },
     {
       "from": "/*",
       "to": "/../../static/*",
     }
    ]
}</code></pre>
**Note:** all "to" URL's route relative to the design doc the rewrite rule belongs to.

So how do we map our hashbang URL to our show method containing the rendered HTML?
<pre><code>{
    "_id":"_design/blog",
    "rewrites": [
     {
       "from": "/",
       "to": "/_show/escaped_fragment/:_escaped_fragment",
     }
    ]
}</code></pre>

There's a serious problem with this approach. The following two rules are equivalent as far as CouchDB is concerned:
<pre><code>{
    "_id":"_design/blog",
    "rewrites": [
     {
       "from": "/",
       "to": "../../static/index.html",
     },
     {
       "from": "/",
       "to": "/_show/escaped_fragment/:_escaped_fragment",
     }
    ]
}</code></pre>

Which means I won't be able to define separate logic for when i want a user to go to index.html and for when the web crawler wants an escaped fragment. There are simple ways to get around this, such as by using Nginx as a reverse proxy and using its more capable URL rewriting feature, but in the end I may end up using a different approach described here that utilizes html5's pushState.
***More to come.....***