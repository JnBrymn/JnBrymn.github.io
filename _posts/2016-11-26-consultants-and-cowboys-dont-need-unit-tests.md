---
layout: post
title: Cowboys and Consultants Don't Need Unit Tests
---

As a developer, my understanding and respect for software testing has been slow coming because in my previous work I have been an engineer and a consultant, and in these roles it wasn't yet obvious how important testing really is. But over the past year I have finally gained an appropriate respect and appreciation for testing; and it's even improving the way I write code. In this post I will explain where I've come from and how far I've traveled in my testing practices. I'll then list out some of the more important principles I've picked up along the way.

## Engineers are cowboys ... and cowboys don't need no stinkin' tests.
I got my start as an Aerospace engineer and as an engineer, _if_ you do any programming at all, testing is probably not part of it. Why? _Because engineers are cowboy coders._ As engineering students, we are taught just enough programming to implement whatever algorithm we have in mind, make some pretty graphs, and then we graduate.

It wasn't much better at my first job. I had shown an interest in software development and so, in one particular project, I was given the task or reworking and improving the project codebase. We were developing autonomous aircraft control algorithms and it soon became apparent that after months of work, no one had thought to run the simulation using different starting conditions. After finally trying different starting conditions we found that our control system was generally better at crashing the plane rather than flying it. This _should_ have been the biggest hint in my early career that testing _might be important_. But it would still be quite a while before I learned that lesson.

## Consultants only build prototypes - so why would we test our code?
After some time I figured out that satellites and aircraft were cool 'n' all, but I like the software, the tech, and the math. Soon I found myself in Career 2.0 as a search technology consultant. And while I was getting better at programming, I _still_ didn't have proper respect for good tests. And _maybe_ this was justified. Much of my work was in one or two week stints with companies helping them understand how to search engines work and occasionally putting together a prototype. At this point I at least understood what tests were, but I would rationalize that tests were an unhelpful nuissance for me because I was just putting together prototypes. But the prototypes, it turns out, often lived long after my work was complete. Maybe tests would have been good after all!

## Finally grokking tests at Eventbrite
It was finally at Eventbrite when I truly experienced and understood the benefit of good testing practices. Eventbrite is by far the largest company I have ever worked for, with the most extensive and mature code base. With such a large amount of code, and with so many different contributors, it imperative that tests should be written along with code. Thus I was finally learning _proper_ software development! Below are some of the things that I picked up about testing. Since Python is our dominant language, much of the details below are Python specific, but the main idea can be applied to most any language.

### Patterns for testing and the influence on code structure
In python testing, the `mock` library is regularly used to mock out functionality. For instance you will often see tests like this (note the comments):

```python
@mock.patch('my_package.some_function', return_value='bologna')
def test_my_code(self, mock_some_function):
    """
    for the duration of this test, `mock.patch` replaces
    every occurrence of `my_package.some_function` with a mock
    function that always returns the string 'bologna',
    this mock function is then provided to this test method
    as the `mock_some_function` argument
    """

    # `my_code` contains a call to `some_function` - which has been
    # replaced with `some_function`
    my_code('do your thing')

    # after calling my_code you can check that `mock_some_function`
    # was called and you can make sure it was called with the
    # expected values
    mock_some_function.assert_called_once_with(
        'do', 'your', 'thing'
    )
```

Mocks make testing in Python quite easy, but they can be overused. Here's an observation that has helped me immensely in writing better tests:

<center>When unit testing, mocks should only be used one level deep.</center>
<br/>
That is, you can mock anything directly mentioned in the unit being tested, but you should avoid mocking anything hidden deeper within the code. This seems reasonable, right? If you're mocking stuff deep within the code, then A) how will future developer ever hope to understand why this patch is needed or what it does? And more importantly B) the test itself becomes more brittle by unnecessarily coupling together a larger volume of code.

Upon realizing that mocks should only ever be one level deep, my coding style began to change - it became more clean and hierarchical. Specifically, if I'm writing some sort of code module, the first function reads like a recipe and has only high level algorithmic elements. Consider the following code snippet for making a cake:

```python
def make_cakes(style='festive', num=1):
    cakes = []
    for i in range(num):
        batter = make_batter()
        pan = get_pan(style)
        pan.add(batter)
        cakes.append(bake(pan))
    return cakes

def make_batter():
    ingredients = [FLOUR, EGG, OTHER_CAKEY_THINGS]
    return create_mixture(ingredients, method='vigorous_beating')

def get_pan(style):
    if style not in ['festive', 'happy', 'fun']:
        raise Exception('We only make happy cakes here.')
    return acme_cookware.pans[style]

def bake(pan):
    oven = acme_ovens.Oven()
    oven.pre_heat(degrees=350)
    try:
        cake = oven.bake(pan)
    except Fire:
        return None
    return cake

# ... other methods here like create_mixture
```

Here `make_cakes` is literally a simple recipe that enumerates the basic steps required to make a cake, the details of each steps are then described in the functions below `make_cake`.

When code is written hierarchically like this, its easy to see how tests can be cleanly written. For each function we simply mock out the next level of function calls and then after calling the actual unit being tests, we assert that all mocks are called with the expected values. For instance, the top-level `make_cakes` function could be tested like so:

```python
@patch(cookin_with_john.make_batter, return_value=fake_batter)
@patch(cookin_with_john.get_pan, return_value=fake_pan)
@patch(cookin_with_john.bake, return_value=fake_cake)
def test_make_cakes(
    self,
    mock_bake,
    mock_get_pan,
    mock_make_batter
):
    # test
    cakes = cookin_with_john.make_cakes(style='happy', num=1)

    # review
    mock_make_batter.assert_called_once_with()
    mock_get_pan.assert_called_once_with('happy')
    fake_pan.add.assert_called_once_with(fake_batter)
    mock_bake.assert_called_once_with(fake_pan)
    self.assertEqual(cakes,[fake_cake])
```

And then, in turn, each of the sub-functions would be tested similarly until you get to atomic functionality that possibly needs no mocks at all.

This is obviously an over-simplification of reality, but you do get the point, right? Mocking only one level deep lends to clean tests. And structuring code hierarchically is a great way to ensure that there is little need to use "deep mocking".

Let's step back a bit and also consider the collateral benefits of this approach to code structure and testing:

* Tests become much more uniform and easy-to-understand for _future developer_.
* When code must be refactored, it's going to require fewer test to be fixed because tests _only_ touch a single method. (That's why they call it "unit" testing!)
* The amount of mocking required to test code is decreased because there is a lot more code to mock if you are mocking deep into code.
* The code being tested is also more uniform and easy-to-understand. Any function should reads as a simple "recipe" and the sub-steps of the recipe should be encapsulated in their own functions (which themselves also read like recipes).

### Test Driven Development
Another thing that I finally realized is the true importance of Test Driven Development (TDD). As I started writing more tests and better tests I was amazed - an a little ashamed - of the number of bugs that were present in my code. But slowly I've come around to the realization that I shouldn't be ashamed of the bugs, but rather I should always write tests. _Tests are simply part of the code deliverable!_ Tests should be written while you code and ideally before (e.g. TDD). Before the importance of TDD had completely absorbed, I would tell myself "John, hurry up and finish the code, and then come back sometime this week and fill in the tests". But I quickly learned two things:

1. When you come back to the code in 2 days, you only remember half of what you wrote and it takes some time to reload the code into your mind. So writing tests takes twice as long and still often misses important test corner cases that you knew about as you were writing the code.
1. More importantly - you rarely actually come back and actually do tests! There's always something that seems more important in 2 days than writing tests for code that _you've convinced yourself_ works perfectly.

Because of this I have been drawn more and more to true Test Driven Development:

* Write the minimal amount of boiler plate code you need to make tests.
* Write failing tests.
* Write code that fixes all the tests.

## Still learning
I've come a log way from my cowboy-consultant coding days. But I still have much to learn. This post covered the importance of testing as good code hygene. But there are a lot of other aspects of my own development practices that I would like to refine. Here's a laundry list of things I would like to focus on in the future:

* Readable, "impathetic" code: How to make code that _future developer_ or even _future you_ will be able to read and easily understand.
* Efficient code reading: Something's broken, what strategies should you use to efficiently isolate and diagnose the problem? - OR - Given a new code base, how do you quickly understand where everything is and how everything works?
* Tools of the trade: A developer I respect greatly confided that after weeks of her first focused python development, she was unaware that python came with a debugger! I'm sure there are plenty of things that I'm not aware of too. What are some tools and tricks that can greatly boost productivity?
* Pair programming - How to make the most of 30 minutes of mind-melding over Google Hangouts. Is it important? (Hint: it's super important for me.)
* Focus - Why is it so hard to jump into flow? Can flow development be turned on like a light switch? I bet some people can.

What do you think? Do you have any recommendations for better testing habits? How about other aspects of just being a good developer? What should I focus on next?

Thanks for reading.