---
layout: post
title: CouchDB Reverse Proxy and Middleware in Go
hero_image: /downloads/gopher_on_couch.jpg
readingTime: 10
---

Erlang and Go are mortal enemies, very true, but Go is also more pragmatic to the majority of programmers out there that learned C-based syntax and OOP strategies. I like Go a LOT, which is why I use Go in front of CouchDB. Previously I used Python, but there are so many problems with type errors and efficiently serving Python web code (Apache/Gunicorn/Greenlets/PyPy/Nginx/headaches...). Go is built to serve websites out of the box with their awesome HTTP library and Goroutines. It's also built to check code for safety.

Here's how to set up CouchDB behind a Go app while still being able to access CouchDB directly:

### Files on Github Gist ###

<script src="https://gist.github.com/pokstad/b74b572844d7f9521716.js"></script>

## Examining couchdbreverseproxy.go ##

The magic sauce that allows us to run a Go web server is the HTTP library:

    import net/http

This gives us access to the powerful Goroutine powered HTTP and HTTPS webservers. This library also gives us access to the simple yet effective HTTP server mux, which allows us to route our HTTP requests to different code.

    mux := http.NewServeMux()

### Static Files Hosting ###

Almost every major site serves static files in addition to dynamic content. Go provides a filesystem server that works great for this:

    // by default, URL's will be mapped to our static assets
    mux.Handle("/",
               http.FileServer(http.Dir(server_configs["static_web_assets"])))

This piece of code will serve static files at the root URL for the server. It accesses files stored in the directory we specified in our server configs map at the key `static_web_assets`.

### Custom API/Middleware ###

If we need to write a custom API, we can do it like so:

    mux.HandleFunc("/api", customAPI)

Else where we can define the method for handling these requesets:

    func customAPI(rw http.ResponseWriter, req *http.Request) {
        // your middleware lives here
    }

In this case I've left it empty, but you can do just about anything you want here in the form of a response to the requesting client.

### Reverse Proxy ###

The main reason for this article is to demonstrate how you can still access CouchDB through a reverse proxy along with other middleware goodies. I aim to please:

This piece of code depends on the following import:

    import "net/http/httputil"

And the code:

    // create a reverse proxy to our couch server
    proxy_url, _ := url.Parse(server_configs["couchURL"])
    mux.Handle("/db/",
               http.StripPrefix("/db/",
                                httputil.NewSingleHostReverseProxy(proxy_url)))

So what happens here is that any requests to /db/* will be routed to our CouchDB server. CouchDB doesn't know it's going through a proxy and doesn't care. It just works.

## Extra CouchDB Goodies ##

We also use an open source library called Go-CouchDB for handling logging, the OS daemon setup (primarily the graceful exit of the server when CouchDB shuts down), and a client to access the CouchDB server as an authenticated user.

## Examining local.ini ##

CouchDB uses local.ini to configure the server. The primary modifications made were to run the Go server as an OS daemon. This means that CouchDB will try to keep the process running as long as CouchDB is running. CouchDB will also provide the configuration key-value pairs in the "go_server" section to the server.
