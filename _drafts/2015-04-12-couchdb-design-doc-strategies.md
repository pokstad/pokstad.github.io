---
layout: post
title: CouchDB Design Document Workflow Tips
---
CouchDB uses special JSON documents known as *design documents* to implement server side functionality. These documents are unique in a few respects:

* Only database administrators can create or modify them.
* Their ID property must be prefixed with "_design/".
* They define server behavior using code (by default, CouchDB uses Javascript code).

The last point is very important. Since design documents are strict JSON objects, they can only contain a limited set of data types. The JSON spec specifies that JSON objects must contain strings for keys and values can be one of the following:

* Strings
* Numbers
* Arrays
* Objects
* true
* false
* null

## Database Design Document Delima Dude ##

You'll notice that *functions* are not on of the permitted value types. Since JSON does not support native Javascript functions as a value type, we have to use a little _hack_ to store our code: we encode the functions as strings.

Encoding functions as strings has a few issues. When writing functions in a text editor, we have to remember to encode all line endings as "\n" and we have to escape all quotes since JSON already uses quotation marks to indicate the start and end of the string representing the function. This can make writing Javascript functions very frusturating since you either need to write the function in the proper format ahead of time, or you must write the function first and then perform a conversion operation. Either way makes it hard to iteratively work on the function and test it immediately which can slow down workflows.

## Tip 1: Your browser is your friend ##

Since JSON documents cannot contain functions, how do we create a comfortable environment for writing and testing design docs? In the browser! Objects in Javascript can contain functions and other user defined data types.

Let's make a bold assumption. This is the wrong way to write design documents by hand in Futon:

    {
        "_id":"_design/users",
        "language":"javascript",
        "views":{
            "email_verified":"function(doc){if(doc.type==\"user\" && doc.email && doc.email_verified){emit(doc.email_verified,doc.email);}}"
        }
    }

This is much more legible and therefore more correct-ish way to do it in a Javascript source code file:

    var design_doc = {
        _id:"_design/users",
        language:"javascript",
        views:{
            email_verified:function(doc){
                if(doc.type=="user" && doc.email && doc.email_verified) {
                    emit(doc.email_verified, doc.email);
                }
            }
        }
    };

When we remove the excessive quotation marks and properly format the layout of the code, it becomes much more obvious that we are attempting to create a CouchDB view that lists all CouchDB users that have an email verified and stored in our database.

Note that this code is no longer proper JSON syntax. It is missing quotation marks around the key strings. This is fine in a web browser, but if you try posting a JSON document to CouchDB without the quotation marks it will be rejected.

It also contains a function as a value. This object will work fine in almost any modern web browser, but it will not be able to be saved into CouchDB... yet.

## Tip 2: Convert functions to strings in browser ##

We are going to use a little handly utility function to manually serialize Javascript functions into strings when trying to convert objects into proper JSON:

    var function_stringify = function (key, value) {
        if (typeof value === 'function') {
            return value.toString();
        }
        return value;
    }
    var design_doc_string = JSON.stringify(userrequest, function_stringify);
    console.log(design_doc_string);

What this bit of code does is provide to the JSON serializer a function to run on each key/value pair encountered. This allows us to implement custom behavior to control how values are serialized. In this case, when we encounter a function, we are going to convert it to a string and return it. Pretty simple right?

## Tip 3: Test update validation methods in browser ##

## Tip 4: Post updated design doc directly from browser ##

## Tip 5: Follow versioning best practices ##

When running a live system where clients are dependent on an older version of a design doc, you'll want to update carefully. Thankfully, Cloudant has some great tips on how to maintain design documents when updating/adding views: https://cloudant.com/blog/a-guide-to-cloudant-design-document-management/

# Summary #

MEOW
