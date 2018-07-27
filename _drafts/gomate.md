---
layout: post
title: Documenting Go Code with Gonotes
tags: [software, golang, gomate]
---

The doc library contains a set of standard conventions for interacting with Go documentation. For example, the library includes a [standard formatter for how code comments should be formatted into HTML](). This includes formatting headers, code blocks, and paragraphs. The simplicity and standardized way of approaching the formatting of comments means that it is trivial for IDE's, text editors, and other developer tools to take advantage of displaying comments to the user in a consistent way.

Gomate, a side project of mine that provides Textmate extensions for working with Go code, utilizes the standardized rendering of HTML code for displaying symbol documentation:

<img src="/img/gomate_doc.png" width="100%" height="auto">

*Note: the indented portion of the comment is rendered as monospaced HTML to preserve alignment*