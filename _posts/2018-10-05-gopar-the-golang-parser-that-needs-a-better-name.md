---
layout: post
title: Gopar - The Golang Parser that Needs a Better Name
---
A while back I built a PEG (Parsing Expression Grammer) parser in golang. I wasn't blogging at the time, so the idea slipped under the radar. [Here's a link to the codebase.](https://github.com/JnBrymn/gopar)

And here I am using the parser API to build a JSON parser. If you've ever dealt with parsers, I think this reads pretty clearly!

```go
	digit := OneOfChars("0123456789").Rename("Digit")

	char := OneOfChars(" \t\nabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789~!@#$%^&*()_+`-={}|[]\\:;'<>?,./'").Rename("Char")

	// numbers are a sequence of digits optionally with a '.' and then some
	// more digits
	number := Seq(
		OneOrMoreOf(digit),
		ZeroOrOneOf(Seq(
			S("."),
			OneOrMoreOf(digit),
		)),
	).Rename("Number")

	// strings are a bunch of characters surrounded by " (I'm lazy, I did
	// include ' strings and quote characters in strings)
	str := Seq(
		S("\""),
		OneOrMoreOf(char),
		S("\""),
	).Rename("JsonString")

	// values can be strings or numbers or Objects or Lists ... hey wait,
	// we haven't defined Objects or Lists yet. No problem, `P(string)`
	// creates a placeholderRule that will later be patched with the rule it
	// names
	value := OneOf(
		str,
		number,
		P("Object"),
		P("List"),
	).Rename("Value")

	// a list is, well, a list of values
	list := Seq(
		S("["),
		ZeroOrOneOf(Seq(
			value,
			ZeroOrMoreOf(Seq(
				S(","),
				value,
			)),
		)),
		S("]"),
	).Rename("List")

	// keyVal has a string key and a value val
	keyVal := Seq(
		str,
		S(":"),
		value,
	).Rename("KeyValue")

	// an object is a bunch of keyVal pairs
	object := Seq(
		S("{"),
		ZeroOrOneOf(Seq(
			keyVal,
			ZeroOrMoreOf(Seq(
				S(","),
				keyVal,
			)),
		)),
		S("}"),
	).Rename("Object")

	// an object is a bunch of keyVal pairs
	err := Patch(object,list)
	if err != nil {
		t.Fatal(err)
	}
		
	//The big test: nested lists and dicts some which are empty
	expectNoErr(t, object, `{"apple":"red","banana":[1,2],"coconut":{"a":1,"b":[],"c":{}}}`)
	expectErr(t, object, `{"apple":"red","banana":[1,2],"coconut":{"a":1,"b":[],"c":{}}`,
		"error at offset 61 in rule Object>'}'. EOF")
```

