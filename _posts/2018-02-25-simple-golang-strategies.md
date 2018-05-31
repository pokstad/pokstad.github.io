---
layout: post
title: Simple Golang Strategies for Repetitive Error Handling
tags: [golang, error handling]
---
Error handling in Golang can sometimes suck. You may sometimes start to feel a bit of pain in your wrist from all of the `if err != nil {` you've been typing. Even if you have that code handled by an efficient macro, you're going to end up with a file that looks like this:

```go
if err := setStuffUp(); err != nil {
    return err
}
if err := doSumptin(); err != nil {
    return err
}
val, err := doDis()
if err != nil {
    return err
}
if err := doDat(); err != nil {
    return err
}
```

How are we going to reduce the error handling boilerplate without introducing silly constructs like functors and monads that don't scale well in non-generics Go?

## Helper Functions

The simplest solution to reducing error boilerplate is to use helper functions. The simplest example is logging an error if it occurs:

```go
func logIfErr(err error) {
    if err != nil {
        log.Printf("error occurred: %s", err)
    }
}
```

This is a great helper function for things like `defer logIfErr(f.Close())` where we don't care about returning the error so much but we still would like to report that it's happening. This is very useful when using the `errcheck` linter.

## Table Pattern

Sometimes we are executing repetitive code where each unit has the potential to return an error:

```go
var err error
readContents := struct {
  f1 []byte
  f2 []byte
  f3 []byte
}{}
readContents.f1, err = ioutil.ReadAll(f1)
if err != nil {
  return fmt.Errorf("could not read f1 due to: %s", err)
}
readContents.f2, err = ioutil.ReadAll(f2)
if err != nil {
  return fmt.Errorf("could not read f2 due to: %s", err)
}
readContents.f3, err = ioutil.ReadAll(f3)
if err != nil {
  return fmt.Errorf("could not read f3 due to: %s", err)
}
```
*[See above snippet on Go Playground](https://play.golang.org/p/rwPaEjGSSbL)*

Because the contents of each read operation is being assigned to a unique field of readContents, we aren't able to generalize this pattern as much as we want without using reflection (ew yuck). We also can't put each of these operations into a function without having to repetively handling each error in both the helper function and the caller. This is where we recognize that the repetitive calls fit the very similar table driven test pattern:

```go
var err error
readContents := struct {
  f1 []byte
  f2 []byte
  f3 []byte
}{}
for _, readOp := range []struct {
  contents *[]byte
  source   io.Reader
}{
  {
    contents: &readContents.f1,
    source:   f1,
  },
  {
    contents: &readContents.f2,
    source:   f2,
  },
  {
    contents: &readContents.f3,
    source:   f3,
  },
} {
   *readOp.contents, err = ioutil.ReadAll(readOp.source)
   if err != nil {
     return fmt.Errorf("could not read due to: %s", err)
   }
}
return nil
```
*[See above snippet on Go Playground](https://play.golang.org/p/cUXh4ABv8uT)*

## Panic & Recover

An alternative to the table driven approach is to use helper functions that panic.

An important Go idiom is that panics should always be recovered from so that the user of a library or program is never exposed to an unhandled panic.
Another Go idiom is to name functions that panic with a `must` prefix. This communicates that this function must succeed, or a panic will be fired.

```go
readContents := struct {
  f1 []byte
  f2 []byte
  f3 []byte
 }{}
mustRead := func(dst *[]byte, src io.Reader) {
  var err error
  *dst, err = ioutil.ReadAll(src)
  if err != nil {
    panic(fmt.Errorf("could not read due to: %s", err))
  }
}
err := func() (err error) {
  defer func() {
    e := recover()
    
    if e == nil {
      // no panic error
      return
    }
    if e, ok := e.(error); ok {
      // err panic occurred
      err = e
    }
  }()
  mustRead(&readContents.f1, f1)
  mustRead(&readContents.f2, f2)
  mustRead(&readContents.f3, f3)
  return
}
```
*[See the above snippet on the Go Playground](https://play.golang.org/p/h362GbAJCZa)*

Note the usage of a named return, so that the deferred statement may modify the return value. Make sure to use a linting tool (e.g. govet) to identify shadowing of the `err` variable.