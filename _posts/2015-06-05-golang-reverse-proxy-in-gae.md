---
layout: post
title: Implementing a reverse proxy in Golang on Google App Engine
hero_image: /downloads/gopher_on_couch.jpg
readingTime: 15
---

Google runs an interesting PaaS (Platform as a Service) called App Engine. It allows you to write code in one of four language/environments: PHP, Python, Java, and *Go*. Go is current a beta offering but already offers the same features as the other three.

Some of the huge advantages of App Engine include:

* Auto scaling & load balancing
* Access to high performance and high durability Google services, such as: datastore, memcache, MySQL, background task queues, email service, logging

App Engine restricts much of what you can do. For example:

* It is strictly a web platform (HTTP and HTTPS access only).
* Each request is limited to 60 second time outs and/or 32MB payloads.
* Arbitrary network access is not allowed (without their special library: appengine/sockets)
* Same goes for outgoing HTTP requests (without their special library: appengine/urlfetch)

If you read my previous post on [Go & CouchDB](http://pokstad.com/2015/04/18/couchdb-and-go.html), you'll know that I appreciate Go's slick reverse proxy library. It makes it extremely simple to expose CouchDB's HTTP API. However, I received this error when I tried using similar code on my App Engine development server:

    http: proxy error: http.DefaultTransport and http.DefaultClient are not available in App Engine. See https://cloud.google.com/appengine/docs/go/urlfetch/

## Connecting the Pieces ##

After pouring through the documentation, I learned that App Engine's urlfetch library implements a Go interface called http.RoundTripper. RoundTripper is basically an abstraction for the network transport resources needed to perform an HTTP request. Typically, this is a network socket (file descriptor). I'm not sure how Google ultimately implements this on App Engine, but it doesn't matter! The real question is: _Where do I plug this in to make this system work the way I want?_

Take a look at the documentation for the Go HTTP reverse proxy: http://golang.org/pkg/net/http/httputil/#ReverseProxy

This excerpt describes the data structure that makes up a reverse proxy:

    type ReverseProxy struct {
        // Director must be a function which modifies
        // the request into a new request to be sent
        // using Transport. Its response is then copied
        // back to the original client unmodified.
        Director func(*http.Request)

        // The transport used to perform proxy requests.
        // If nil, http.DefaultTransport is used.
        Transport http.RoundTripper

        // FlushInterval specifies the flush interval
        // to flush to the client while copying the
        // response body.
        // If zero, no periodic flushing is done.
        FlushInterval time.Duration

        // ErrorLog specifies an optional logger for errors
        // that occur when attempting to proxy the request.
        // If nil, logging goes to os.Stderr via the log package's
        // standard logger.
        ErrorLog *log.Logger
    }

The important part of the struct is the Transport object, which is of type http.RoundTripper. All we have to do is set this Transport to an instance of urlfetch.Transport. Easy, right?

## Open Source Surgery ##

There's a slight complication. ReverseProxy is designed to accept a single Transport at creation and reuse this Transport during the lifetime of the server, but a new urlfetch.Transport must be created with each request to App Engine. Since urlfetch is dependent on a [App Engine request context](https://cloud.google.com/appengine/docs/go/reference#Context), and a request context is dependent on the current request, we will need to modify the portion of reverse proxy code that handles the actual request:

    func (p *ReverseProxy) ServeHTTP(rw http.ResponseWriter, req *http.Request) {
        transport := p.Transport
        if transport == nil {
            transport = http.DefaultTransport
        }
        
        outreq := new(http.Request)
        *outreq = *req // includes shallow copies of maps, but okay
        
        p.Director(outreq)
        outreq.Proto = "HTTP/1.1"
        outreq.ProtoMajor = 1
        outreq.ProtoMinor = 1
        outreq.Close = false
        
        // Remove hop-by-hop headers to the backend.  Especially
        // important is "Connection" because we want a persistent
        // connection, regardless of what the client sent to us.  This
        // is modifying the same underlying map from req (shallow
        // copied above) so we only copy it if necessary.
        copiedHeaders := false
        for _, h := range hopHeaders {
            if outreq.Header.Get(h) != "" {
                if !copiedHeaders {
                    outreq.Header = make(http.Header)
                    copyHeader(outreq.Header, req.Header)
                    copiedHeaders = true
                }
                outreq.Header.Del(h)
            }
        }
        
        if clientIP, _, err := net.SplitHostPort(req.RemoteAddr); err == nil {
            // If we aren't the first proxy retain prior
            // X-Forwarded-For information as a comma+space
            // separated list and fold multiple headers into one.
            if prior, ok := outreq.Header["X-Forwarded-For"]; ok {
                clientIP = strings.Join(prior, ", ") + ", " + clientIP
            }
            outreq.Header.Set("X-Forwarded-For", clientIP)
        }
        
        res, err := transport.RoundTrip(outreq)
        if err != nil {
            p.logf("http: proxy error: %v", err)
            rw.WriteHeader(http.StatusInternalServerError)
            return
        }
        defer res.Body.Close()
        
        for _, h := range hopHeaders {
            res.Header.Del(h)
        }
        
        copyHeader(rw.Header(), res.Header)
        
        rw.WriteHeader(res.StatusCode)
        p.copyResponse(rw, res.Body)
    }

We only need to replace the first four lines of this function to make it work:

    func (p *ReverseProxy) ServeHTTP(rw http.ResponseWriter, req *http.Request) {
        transport := &urlfetch.Transport{
            Context:appengine.NewContext(req),
        }
        //if transport == nil {
        //    transport = http.DefaultTransport
        //}

The finished code can be found here:

<script src="https://gist.github.com/pokstad/936ace2c6fc563105c17.js"></script>

Now we can test it out in an app engine project:

    package goengine
    
    // standard libs
    import (
        "fmt"
        "net/http"
        "net/url"
    )
    
    func init() {
        // create a reverse proxy to our couch server
        proxy_url, _ := url.Parse("http://your_couchdb_server_hostname:5984/")
        reverse_proxy := NewSingleHostReverseProxy(proxy_url)
        http.Handle("/",
                    http.StripPrefix("/db/",
                    reverse_proxy))
    }

## The Cost ##

So here's the problems with this solution: App Engine charges you extra for using urlfetch, even if the request never leaves their network (e.g. Compute Engine VM's).

At the time of writing, Google permits 657,000 urlfetch API calls for their free tier, and 172,800,000 API calls for their billed accounts. Bandwidth used from urlfetch counts toward your general [App Engine bandwidth quotas/billing](https://cloud.google.com/appengine/docs/quotas#UrlFetch).

Hopefully, Google will come out with a solution for those of us that like to host our CouchDB servers behind App Engine. 
