---
layout: post
title: Interfaces Make Go a Strongly Duck-Typed Language
---
* Need an image - maybe a strong duck? Maybe the Mighty Ducks?

### Outline
* The importance of interfaces - so you're a subclass of X... but you don't want the implementation of X and you don't want the data of X... interfaces lets you seperate behavior from data
* What interfaces are like in every other language... why that's awesome (well structured typing; behavioral subtyping; seperates behavior from data and implementation)/why that sucks (you're always writing interfaces - and you can't modify interfaces in other peoples code)
* What duck typing is in languages like python and ruby -- why that's awesome (can make usage of very flexible types)/why that sucks (no type safety or compile time type checking)
* Introducing go - the world's first strongly duck typed language. Great because rather than classes inheriting from interfaces, structs match interfaces. This means that you can write an interface that matches structs in foreign libraries. 
  * Example - foreign library has struct (not interface) would like to be able to mock it http://play.golang.org/p/vWk2j5Pahi
  * Here's how: http://play.golang.org/p/kaNYU27E60
  * Another benefit - the type system is flat - you get the benefits of subtyping with out the cruft of hierarchical subtypes
* Use interfaces to force client libraries to use constructors. Do this my making exported interfaces and constructors to nonexported structs
  * Easy to create bad stuff - requires users to know how to instantiate struct - doesn't help them: http://play.golang.org/p/dmfH-_7i8t
  * Can only access through constructor - http://play.golang.org/p/FTwJhEP_Vb
* Dependency injection via interfaces where structs encapsulate interface functions. http://play.golang.org/p/gM-9rAfkMh
* Interface puzzle: http://play.golang.org/p/u37maro7a9
* Is there anything that can be said about interfaces and primatives? What about inheriting from primatives and the associated pain.
* Interfaces don't account for exported fields. This is really annoying for functions because you call call a field function just like a method, but it doesn't count for matching on an interface.
* Can't create interfaces inside of a function.
* What about using interfaces within structs?
```go
type Fooer interface {
  Foo() string
}
type Bar struct {
  Fooer
  otherthing string
}
type Baz struct {
  myfoo Fooer
  otherthing string
}
```
* What about overriding interface functions? Or calling parent interface functions?
----
* Interface is for Key-Value - but is there any extra hidden assumptions? (e.g. fast on scans through sor
* Common error I've ran into:
```
prog.go:60: cannot use rows (type FakeRows) as type Rows in function argument:
	FakeRows does not implement Rows (Next method has pointer receiver)
```
Happens when I use a non-pointer value in an interface value. It's confusing because the error seems to indicate that I've not built the struct methods to match the interface, but in reality it's because of the pointer.
* Casting an interface variable to a struct is confusing if the struct is a pointer