# Python Kubernetes Job Launcher

This example shows how to use python and the Kubernetes client to dynamically run Kubernetes jobs. 

This example takes advantage of Okteto's file synchronization features, allowing you to quickly iterate in your jobs instead of having to rebuild your docker images after every change.

## Clone the repository

```
$ git clone https://github.com/okteto/python-getting-started
```

## Install the Okteto CLI

If you haven't already, install the [Okteto CLI](https://okteto.com/docs/getting-started/installation) in your local machine.

## Get your Okteto Cloud credentials

Connect your CLI to your [Okteto Cloud](https://cloud.okteto.com) account to download your Kubernetes credentials.

```
$ okteto namespace
```

```
 ✓  Updated context 'cloud_okteto_com' in '/Users/ramiro/.kube/config'
```

> If this is the first time you use Okteto Cloud, a free account will be automatically created for you.


## Launch your Development Environment

```
$ okteto up --deploy
```

```
 ✓  Development container activated
 ✓  Files synchronized
    Namespace: rberrelleza
    Name:      python-job-launcher
    SSH:       2222 -> 2222
    Forward:   8080 -> 8080
    Reverse:   9000 <- 9000
```

> `okteto up` will deploy your development environment in Okteto Cloud and drop you on a remote shell. Any command that you  execute here will be executed in your remote development environment.

## Launch a Job

`launcher/main.py` contains the code to dynamically create a Kubernetes Job object in the current Kubernetes namespace.  The code will print out the name of the job at the end of the execution.

```
$ python launcher/main.py
```

```
launched hello-world-job-1597791956: {'active': None,
 'completion_time': None,
 'conditions': None,
 'failed': None,
 'start_time': None,
 'succeeded': None}
```

The job prints out a string. You can see the results by running the command below: 
```
$ kubectl logs -l=job-name=hello-world-job-1597791956
```

```
hello world
```

## Update the Job

`job/main.py` contains the code of the job. Open the file on your favorite IDE, and change the string from "hello world" to "hello okteto". 

At this point, you'd normally have to build the image and push it to a registry before being able to see the results. Instead of that, just launch another job, like we did in the previous step:

```
$ python launcher/main.py
```

```
launched hello-world-job-1597792439: {'active': None,
 'completion_time': None,
 'conditions': None,
 'failed': None,
 'start_time': None,
 'succeeded': None}
```

Wait a couple of seconds for the job to run, and check its output:

```
$ kubectl logs -l=job-name=hello-world-job-1597792439
```

```
hello okteto
```

Instead of having to rebuild and push images every time, we are talking advantage of the fact that `okteto` is keeping your code synchronized between your local machine and your remote development environment. The code is placed in a volume, which means that it can also be accessed by other resources in the same namespace, like we do here (more on [this here](https://github.com/okteto/okteto#how-it-works)).

## We need your Feedback

What do you think about this approach? Do you find it useful, do you hate it, all of them? Join us in our Slack community and help us improve the development experience of Cloud Native Applications.

[![Chat in Slack](https://img.shields.io/badge/slack-@kubernetes/okteto-red.svg?logo=slack)](https://kubernetes.slack.com/messages/CM1QMQGS0/)