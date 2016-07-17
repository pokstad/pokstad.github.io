---
layout: post
title: Handling Web Credentials in Swift with Cloudant Sync
tags: [ios, couchdb, swift, cdtdatastore, nsurlsession]
---
I've been using Cloudant Sync for my latest project, [Sofa King: Sync](http://pokstad.com/sofaking/) and I ran into some issues with complex passwords used for credentials. I realized that I made a major rookie mistake by following the documentation.

[The documentation states that passwords should be encoded in NSURLs](https://github.com/cloudant/CDTDatastore/blob/master/doc/replication-policies.md):

```
// username/password can be Cloudant API keys
NSString *s = @"https://username:password@username.cloudant.com/my_database";
NSURL *remoteDatabaseURL = [NSURL URLWithString:s];
```

This does not work with complex passwords that contain special delimiter tokens, such as:

- / (backslash) which is used to end the protocol and start the username.
- : (colon) which is used to end the username
- @ (at) symbol which is used to end the password

NSURL does not have any methods to set the username and password with appropriate encoding to avoid this issue. Ultimately, these credentials will be added as basic authentication header in base64 encoding. Instead of adding them to the NSURL, they should be added directly to the headers to avoid parsing issues. This can be done with the HTTP interceptors:

```
func basicAuthHeaderInBase64() -> String? {
	if let username = fetchUsername(),
	   let password = fetchPassword() {
        let userPasswordString = "\(username):\(password)"
        let userPasswordData = userPasswordString.dataUsingEncoding(NSUTF8StringEncoding)
        let base64EncodedCredential = userPasswordData!.base64EncodedStringWithOptions(
            .Encoding64CharacterLineLength)
        return "Basic \(base64EncodedCredential)"
    }
    return nil
}

func interceptRequestInContext(context: CDTHTTPInterceptorContext) -> CDTHTTPInterceptorContext {
    if let authString = basicAuthHeaderInBase64() {
        context.request.setValue(
            authString,
            forHTTPHeaderField: "Authorization")
    } else {
        // anonymous access requires us to remove authorization header
        context.request.setValue(nil, forHTTPHeaderField: "Authorization")
    }
    return context
}
```

Ideally, the NSURLSessionConfiguration object should be customized via delegate method to add basic auth:

```
var credential: NSURLCredential {
       return cred = NSURLCredential(
                user: self.username,
                password: self.password,
                persistence: .ForSession)
}    

var protectionSpace: NSURLProtectionSpace {
    return NSURLProtectionSpace(
            host: remoteDatabaseURL.host,
            port: remoteDatabaseURL.port,
            protocol: remoteDatabaseURL.scheme,
            realm: nil,
            authenticationMethod: NSURLAuthenticationMethodHTTPBasic)
}

@objc func customiseNSURLSessionConfiguration(config: NSURLSessionConfiguration) {
    if let c = credential, p = protectionSpace {
    	config.URLCredentialStorage?.setCredential(c, forProtectionSpace: p)
    }
}
```

While testing this method I found that two different replications from two different users initiated in the same protection space will not run as expected. This is probably because the URLCredentialStorage object is a shared object between all URLSessions (not verified). Each time a replication is run, it will pick a default credential from the protection space and NOT the last credential set. In order to avoid authentication errors, a work around is to remove ALL credentials for a protection space before adding the credentials desired ([relevant stack overflow question](http://stackoverflow.com/questions/13694559/cleaning-out-credentialsforprotectionspace-to-have-only-one-key-value-set-nsurl)). However, this ends up modifying the keychain which is not ideal if you are depending on the keychain to store your user credentials.

Another solution is to set the default credential for a protection space. However, this will not work if you want to be able to use anonymous credentials.

A more ideal solution is to use the [NSURLSession delegate to handle authentication challenges](https://developer.apple.com/library/ios/documentation/Cocoa/Conceptual/URLLoadingSystem/Articles/UsingNSURLSession.html#//apple_ref/doc/uid/TP40013509-SW16). This way, based on your app's specific logic you can choose which credential to retrieve from the credential store and use that instead. Currently, I cannot find anywhere in the library that exposes the NSURLSession delegate property for this customization.

I opened an issue in regards to this problem: https://github.com/cloudant/CDTDatastore/issues/302
