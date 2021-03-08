---
layout: post
title: Teaching Abusive Users a Lesson with Recent Average Rate Limiters
---

You've got a problem: a small subset of abusive users are body slamming your API with extremely high request rates. You've added windowed rate limiting, and this reduces the load on your infrastructure, but behavior persists. These naughty users aren't attempting to rate-limit their own requests. They fire off as many requests as they can, immediately hit `HTTP 429 Too Many Requests`, _don't let up_, and as soon as a new rate limit window is available, the pattern starts all over again.

In order to curtail the behavior, wouldn't it be nice if you penalize nefarious users according to their _recent average_ request rate? This way, if a user is responsibly limiting their own requests, then they never get a 429. However if they have a habit of _always_ going over the rate limit, then we stop them from making any more requests. No new windows, no second chances... _until_ they mend their ways and decrease their request rate below our limits. At that point, their recent average falls below the threshold, their past sins are forgiven, and they may begin anew as a responsible user of our API.

TODO! photo of vile abuser

## Not _Quite_ Solving the Problem with Exponentially Weighted Moving Average
The Exponentially Weighted Moving Average is a simple method for measuring the recent average of a series of numbers ([Here's a great reference](https://github.com/VividCortex/ewma), written by world-renowned software developer, and friend, Preetam Jinka.) This makes it seem that EWMA would be a perfect fit for building rate limiters. Effectively, it would work like this: For each user, you store 2 values, the number of hits in this window and the "running average" of their recent windows. Whenever a user makes a request, you update hit count. At the end of the time window you [use a simple formula](https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average) to incorporate the number of hits into the average of the recent windows, and you also reset the hit count to 0 in preparation for the next window.

Unfortunately, the fact that you have to perform a calculation for _every_ recently active user at the end of _every_ window makes this approach utterly infeasible.

## Introducing CEWMA

But there's hope! Drawing inspiration from the EWMA, I will introduce an something I call the Continuous Exponentially Weighted Moving Average, CEWMA, which can be used to estimate the recent average of a users request rate. Importantly, we will not be required to do any global value updates as we were require to do with EWMA.

In the sections below I will lay out a mathematical foundation for this approach and then derive an algorithm for a CEWMA-based Recent Average Rate Limiter. The discussion will be a little light on proofs, but heavy on the intuition that helped me come to my conclusions. Following this, I will provide a couple of demonstrations that  drive home how this approach will be beneficial for the problem outlined in the introduction. Finally, I will lay out ideas for how a Recent Average Rate Limiter may be practically implemented. TODO! is last sentence true?

## Theory
With the CEWMA we wish to estimate the average rate a which a user's requests arrive. However we don't want to find the average request rate across _all time_ because that seems a little unforgiving doesn't it? Perhaps the user hit the wrong button, got up to make a cup of coffee, and upon returning found that they'd issues 2 million requests. Instead, we're only interested in the user's recent behavior. Let's represented the time history of the user's request rate as $$r(t)$$. The weight function, represented as $$w(t)$$, will be used to weight the more recent request rate (e.g. the $$r(t)$$ for t close to 0) as being more important than the request rate that occurred long ago (e.g. when t is a large negative number). In order to find the weighted average of the rate, we have to solve this integral.

$$
\int_{-\infty}^{0} w(t) \cdot  r(t) dt
$$

(This is very similar to [finding the expected value of function](https://mathworld.wolfram.com/ExpectationValue.html) in statistics.)



* We want to estimate the _rate_, but the average rate across ALL time... that's not very forgiving. they might have sinned in their youth but reformed as adults... besides we can't keep every user key alive in redis forever


* Here's how to find a recent expected value (a.k.a. it's average value)  Integral of W(t) and f(t)
  * You can use any weight function but it has to sum to 1
  * introduce exponential weight functions
* But we're looking for the recent average rate - Let's start easy, let's find the CEWMA of a constant rate. CEWMA=R  ... wow, boring, easy

* But astute reader will notice by now that we are measuring the CEWMA of a continuous function. Leads to weird ideas: When the rate is constant in this case, we're saying that if you apply 1 hit per minute for 30 seconds then you use the API one half of a time.
* Don't worry, you can still represent familiar reality with IMPULSE functions. delta(t-T) says that we have a 0 rate for all time but the BAM! at t=T the rate is infinitely high. However the integral of the rate isn't infinite, it's just one. So if your usage _rate_ is the delta(t-T) then you _usage_ is zero until t=T and then your usage is 1 ever after that b/c you used it just once
* Let's find CEWMA for delta(t-T) [link] - you just find the value of the function at that point.

## The Algorithm

* initialize -> 0 time and 0 state
* update -> initially you just track that the first update happened at what time; the next update gets smooshed into "what if everything happened as an impulse now" - emphasis "we need just one number and a time" 
* evaluation -> considering the last impulse size N happened T seconds ago, the corresponding constant rate is 

* how do you set lambda -- by choosing halflife


## Does it Really Work?
* asymptotic convergence - A steady train converges to a(1/(1-e^(?)))  - if halflife is large then this converges to exact solution 
* decays to zero if there are no inputs


## Demo Time
* show the results of "does it really work"
* show how it compares to a simple time-window EWMA for rejecting stuff (slower build up, but permanent banning until they repent (and STOP spamming))

## Conclusion
Reread intro first
* windowed no better or worse than CEWMA, but the rate limits are treated differently
  * after a grace period, CEWMA puts offenders in timeout as long as they keep offending, but after they mend their ways the CEWMA cools down (per the half-life) it lets them start again
  * windowed is much more permissive of persistent abuse, it lets them in again with every window renewal
  * the CEWMA behavior has an interesting behavior in that it _REQUIRES_ the clients to be well behaved, and if they are not then this eliminates a very common type of abuse completely and instantly. So it's not just their requests that will be blocked, but you'll no longer have the entire class of user that just sprays requests and then depends on 429s from _your server_ to act as their rate limiting.
  * the longer and the more extremely they are misbehaved, the longer they will remain in timeout

## Implementation in Redis
* instead of TTL, LRU expire them and completely forego 
* https://redis.io/topics/quickstart
* https://www.compose.com/articles/a-quick-guide-to-redis-lua-scripting/


## Disclaimers
* Is this out there all ready? Maybe?
* Am I accurate? Maybe?


## DON;T FIRGET
* Is "recent average rate limiter" a good name - might be the name for the post
* you can contact me somehow and I'll explain it to you and fix my post
* read TODO! 
* Links
  * expected value integrals
  * impulse functions integrated (dirac delta)
  * link to notebook
* Photos - embarrased rate limited user in intro
* contact https://github.com/github/ecosystem-api/issues/2315
* maybe::: Does this exist already? I don't know! It seems useful, so I bet someone's figured it out before, but I haven't found the right Google search for it yet. And besides, it's never any fun to just look up the answer in the back of the book 😉. Let's try and figure this one out on our own.
* Push and make sure it works
  * test latex equations
* send to Orendorf and GH DS manager
* post on PennyU and Twitter