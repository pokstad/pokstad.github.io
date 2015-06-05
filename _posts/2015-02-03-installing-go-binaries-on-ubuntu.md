---
layout: post
excerpt: Recently, I had the need to install Go on my Ubuntu server and discovered that Ubuntu does not contain the latest version of Go. How do we install it?
readingTime: 5
---
Go is a great tool for deploying applications since by default it generates a single statically linked binary with all application dependencies packed neatly inside. Recently, I had the need to install Go on my Ubuntu server and discovered that Ubuntu does not contain the latest version of Go. How do we install it?

First, we need to identify the version that we require. I was working off the latest version (right now 1.4.1) but Ubuntu 14.10 only installs 1.2. While 1.2 may very well be good enough for most people, I discovered that some of the standard libraries I was using had changed (specifically the net/http library). Rather than backtrack to fit Ubuntu's default packages, I decided to learn a new skill.

First, I had to obtain the binaries for my system. On a 64 bit Linux system running Go v1.4.1, you can download the binaries this way:

    export VERSION=1.4.1
    export OS=linux
    export ARCH=amd64
    wget https://storage.googleapis.com/golang/go$VERSION.$OS-$ARCH.tar.gz
    # https://storage.googleapis.com/golang/go1.4.1.linux-amd64.tar.gz

Then we need to extract it to the default recommended location:

    sudo tar -C /usr/local -xzf go$VERSION.$OS-$ARCH.tar.gz

Now Go is installed, but our terminal doesn't know it exists yet, so we need to define some variables:

    export GOROOT=/usr/local/go
    export PATH=$PATH:$GOROOT/bin

You'll have to place these variables in the correct script for them to work by default. For example, the current user's terminal will always load the ~/.profile script to obtain the current user's environment. Need to modify it for all users? Thankfully, [Ubuntu has this well documented](https://help.ubuntu.com/community/EnvironmentVariables).
