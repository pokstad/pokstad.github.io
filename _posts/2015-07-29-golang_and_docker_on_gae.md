---
layout: post
title: Golang and Docker on Google App Engine Managed VMs
tags: [code, golang, gae]
hero_image: /downloads/t_arrows.jpg
readingTime: 30
---
Docker hasn't been around very long, but already it's all the rage in the tech world. Amazon is supporting Docker through a number of offerings, one of which is Elastic Beanstalk. Google has also been offering support, and one of those new services is called Google App Engine Managed VM's.

# What are Managed VM's (MVM's)? #

App Engine Managed VM is a Google service situated between an IaaS (such as Compute Engine) and a PaaS (such as the traditional App Engine sandbox). It also is similar to Google's container service, Container Engine, in that it uses Docker. This makes it pretty confusing to understand what Managed VM's are.

![Managed VM venn diagram](/downloads/managedvmsimilarities.jpg "Managed VM Venn Diagram")

Let's define MVM's as a Google service that provides HTTP(S) load balancing and auto scaling of ephemeral Docker instances.

Traditionally, App Engine has been considered a very restrictive service since it forces you to only use the environment Google provides. This prevents you from having freedom over API's relating to requests, sockets, threads, filesystem, etc. [In my previous post about reverse proxies](http://pokstad.com/2015/06/05/golang-reverse-proxy-in-gae.html), I had to hack a solution together using Google's App Engine requests API. With MVM's, this hack is no longer necessary.

# What is Docker? #

Docker is a "container" solution for packaging and distributing a server's software environment. It allows you to build onto existing containers and create snapshots as you progress in development. For example, you might start with a Debian image, and then create a Golang image by adding all the files that Go needs. Then, you might take that image and add the files you need for your specific software project.

There are a number of other helpful supporting technologies that allow multiple docker containers to operate in the same environment in an isolated way similar to VMs but with reduced overhead. By avoiding OS virtualization, you entrust the operating system (Linux) to efficiently and securely isolated tenants from one another. This makes it very similar to PaaS solutions such as Red Hat OpenShift.

# Setting up a Development Environment on OSX #

*NOTE: At the time of writing (2015/6/17), these steps are based on a Beta service that is subject to change. Instructions taken from Google's ["Getting Started" guide](https://cloud.google.com/appengine/docs/managed-vms/getting-started).*

## Step 1: Install Google App Engine SDK #

* Download and install [Google App Engine SDK](https://cloud.google.com/sdk/#Quick_Start)
* Install gloud app component (from Terminal): `gcloud components update app`

## Step 2: Install Docker #

Managed VM's also require Docker, and Docker is a bit of a struggle on a Mac due to the Linux requirement. To get around this, Docker provides a development tool called Boot2Docker that uses VirtualBox as the hypervisor to run a minimal Linux environment. Google provides the following instructions:

* [Download and install Boot2Docker](https://github.com/boot2docker/osx-installer/releases/latest)
* Start the Boot2Docker application from the Application folder (this will open a terminal window).

## Step 3: Download the Golang Docker base image #

Google provides a Docker image that includes a base environment for using their supported langauges and libraries. We'll be installing the Golang flavor. Enter the following command in the Boot2Docker terminal window:

    docker pull gcr.io/google_appengine/go-compat

# A Simple App that Extends Google's image #

Now that we have our development environment set up, we can play with our Docker image. We are going to create an app by adding 3 files ([originally provided by Google](https://github.com/golang/appengine/tree/25b8450bec636c6b6e3b9b33d3a3f55230b10812/demos/helloworld)):

1. docker - Our Docker file is a simple script that tells App Engine how to build our container. It contains a reference to our base image and a number of commands to customize it.
1. app.yaml - Our App config file is needed for app engine to understand how to handle this Docker image. It tells App Engine what environment we are using, how to scale our app, and where to route HTTP requests (make sure to replace the application property with the appropriate project ID).
1. module1.go - Our Golang source code for our project lives here. It is our first module (more on modules later...).

<script src="https://gist.github.com/pokstad/f3da4ac958066486470d.js"></script>

## Bundling, Testing, and Deploying our Docker image ##

1. In the Boot2Docker terminal window, `cd` to the location of the folder containing the above 3 files.
1. Run the development server with this command: `gcloud preview app run ./app.yaml`

The last step will generate a Docker image and begin serving the application on your computer. By default, the web app will be accessible from http://localhost:8080. The webpage simply displays the uptime of the instance.

To deploy this application to Google's cloud in PREVIEW mode:

1. Enable billing on your App Engine account: https://console.developers.google.com/billing
1. Create a Project ID: https://console.developers.google.com/project
1. Apply the appropriate billing settings for the new project ID: https://console.developers.google.com/project/_/settings
1. If the development server above is still running, kill the Docker session with Ctrl+C
1. Set up Google authentication: `gcloud auth login`
1. Set the project ID you configured earlier in the Google Developers Console: `gcloud config set project <project-id>`
1. Deploy the Docker container: `gcloud preview app deploy ./app.yaml`

Now, your app is accessible at: https://module1.PROJECT_ID.appspot.com/

# Mixing Sandbox Instances and Managed VMs #

There are a few disadvantages to Managed VM's. At least one Managed VM must always be running in order to respond to requests in a timely fasion. Sandbox instances are capable of "sleeping" where no costs are incurred and being awakened in as fast as milliseconds. Managed VM's require a few minutes to be brought online, thus missing the oppurtunity to serve webpages. Google recommends that your front end should be served by sandbox instances whenever possible, and other tasks that require more flexability (e.g. background workers) to be performed on managed VM's.

There's another option: mix both sandbox instances and managed VM's using modules and a dispatch file.

## Modules ##

In order to mix multiple apps in an App Engine project, we need to designate each app as a distinct module. Modules allow us to break up the code base and assign specific tasks (e.g. front end or background tasks). It also allows the mixing of languages/runtimes. In the case of the new MVM's, it also allows us to mix sandbox and MVM instances.

### Module 2 ###

Our second module contains the Go code for the sandbox instance. It does the exact same thing as the MVM instance, except it will print "Module 2" instead of "Module 1". It will also include a different app.yaml file and a dispatch file.

<script src="https://gist.github.com/pokstad/828d0775a2458ce610fc.js"></script>

*Note: Go web apps in the sandbox require an "init" function as an entry point rather than the "main" function used in the MVM demo.*

## Routing with Dispatch Files ##

The dispatch file, dispatch.yaml, tells Google App Engine's HTTP routers how to direct traffic in our app. By using string patterns to describe our URL's, we can indicate which URL's go to which modules.

Each module may be a different language/runtime or can be either a sandbox instance or MVM.

Source: [App Engine Module Routing documentation](https://cloud.google.com/appengine/docs/go/modules/routing)

*Note: The dispatch rules do not strip away the URL prefix before delivering the request to the proper module.*

## Deploying Sandbox Apps ##

In order to deploy, first make sure that the application name matches the project ID you previously set up. Then, to deploy the app to App Engine, enter the following command:

    goapp deploy /path/to/myapp/

Where `/path/to/myapp` is the location of the directory containing the 3 application files.

This new module should be accessible from https://module2.<project ID>.appspot.com/

Here's the fun part, try accessing the following URLs:

* https://PROJECT_ID.appspot.com/
* https://PROJECT_ID.appspot.com/module2/

Depending on the URL path, you will get routed to the appropriate module.

# Conclusion #

Whether you have an app that fits within the confines of the App Engine sandbox, or if you need the freedom of a custom Linux stack, Google has you covered. The biggest question moving forward is how they will price the MVM service. This major detail will be an important factor in the decision making for whether to build specific modules in the sandbox or an MVM.

_This post was inspired by [this article written about Go on AWS Elastic Beanstalk](http://www.topcoder.com/blog/deploying-go-apps-with-docker-to-elastic-beanstalk/)_
