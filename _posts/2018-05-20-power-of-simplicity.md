---
layout: post
title: The Power of Simplicity
tags: [software, hugo, jekyll, blogging]
---

I recently updated my website. I decided I wanted an even simpler website than before. I chose to
re-theme using the amazing [remarkdown](https://fvsch.github.io/remarkdown/) CSS stylesheet. I
also decided to remove all javascript from the base template for my site. No more tracking or
dynamic behavior on the majority of the pages. My reasoning for this: a blog should just be a
simple website focused on content. Anything additional becomes a distraction. I have little time
these days to manage the upkeep of a complex and overly engineered website.

I also took a look at converting my website from using [Jekyll](https://jekyllrb.com) to
[Hugo](https://gohugo.io). I was intrigued by the promise of performance and the Golang based
implementation. In the end, however, I decided it was a mistake for a number of reasons:

1. Hugo has enourmous feature creep. The documentation is bloated due to too many features.
2. Performance is a non-issue for a statically compiled site. That's the whole point of a static site.
3. Hugo requires me to restructure my site that is already set up for Jekyll. Classic case of "not
	invented here."

I came to the realization that there was a serious problem with the majority of Jekyll clones: they
tried too hard to win by cramming in features and complexity with marginal benefit. The biggest
benefit I see to Hugo is the single executable install versus Jekyll's Ruby install. If I were to choose
a new tool that required porting my existing code, I would favor something much simpler.

Here's a dirty rough draft of what I would like to see in a statically compiled site tool used for
blogging:

1. Ridgid design over flexability - if most people are using this for blogs, just make it work for most
	blogs. Too much abstract extensibility just gets in the way of banging something out quick. Be
	opinionated about one true way to do things to reduce the learning curve.
2. Limited scope - create something truely universal by doing less. Less is more.
3. Single executable - this makes it simple to install on many platforms
4. Directory structure shouldn't matter - just dump everything at the root or organize it into subdirs.
	Conveying context through arbitrary folder structure is one more learning curve.

For now, I'm sticking to Jekyll.