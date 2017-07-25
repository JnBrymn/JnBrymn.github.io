---
layout: post
title: Functional Programming Penny Chat
---

Better late than never for my Penny Chat Review for Bryan Hunter's FP discussion. Here are some of the things that I picked up:

## I finally grokked tail recursion

I'm actually embarrassed that I didn't get this earlier since it's such a simple idea. Recursion, as you know, is when a function calls itself. The difficult part of recursion in most languages is stack overflow. This happens because with each call to the function you have to keep track of the value of all of its variables for every call, and if you keep going deeper and deeper, you have more and more to keep track of -- until BOOM! Python protects you by just bailing when the recursion depth reaches 1000. But, if the recursive call is the very last statement in the function, then you are using so-called tail recursion. In this case, it's not necessary to keep track of the existing scope any more because you won't use it anymore and in this case an infinite stack depth is A-OK. In Python, tail recursion brings no benefit because Python just still bails out after the stack depth reaches 1000. But in other languages, like Elixir, infinite tail recursion is depended upon and is a primary feature of the language.

## Elixir is cool

Speaking of Elixir, Bryan demoed the tail recursion principle above using Elixir and I got to see some of the syntax. Elixir looks slick, definitely work a little hack time next time I'm jonesing to get my FP on. The last functional programming language I approached was Clojure (with this fantastic online book http://www.braveclojure.com/introduction/), but -- and I know this is trite -- I found the syntax and all the parens everywhere distracting and difficult to read. Elixir seems to keep some of the familiar programming syntax for things like defining modules and functions. This helps me to read the code more easily.

## Handling global state

I came into the discussion with a weird belief that in functional programming you have one giant state blob that effectively every function has to deal with as an input parameter. (I'm exaggerating my idea a little bit, but this is close to what I had in mind.) Bryan and Nick Lorenson helped me straight a bit. For instance an Elixir program could be used to track the global state of a online game, but you might actually have a separate function (or process) to manage the state for only a small portion of the map, and then within that function, other functions could deal with the sub-state of the characters in that portion of the map. ... I still don't completely grok the situation, but at least I'm closer to reality than where I started.

Thanks Guys!
