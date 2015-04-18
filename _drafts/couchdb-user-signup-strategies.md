---
layout: post
title: CouchDB User Sign Up Strategies
---

By default, CouchDB let's any user sign up for an account. This introduces a number of problems since a user can effectively perform a DOS on a server by signing up for many user accounts. This article explores a strategy for preventing this abuse and moderating the signing up of a potential user.

## How to deter automated signup scripts (bots) ##

There are a few methods to deter bots:

1. Require e-mail verification
1. Require a recaptcha code
1. Require a session ID (Cross Site Request Forgery (CSRF) token)
1. Place a long delay in the request system to slow down bots (but something a human wouldn't mind)
1. Log IP addresses for each user request to track funny business.
1. Utilize current users to vouch for new ones (See http://lobste.rs user tree system: https://lobste.rs/u)

Unfortunately, CouchDB doesn't do any of these things out of the box.