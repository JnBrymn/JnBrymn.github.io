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
With the CEWMA we wish to estimate the average rate at which a user's requests arrive. However we don't want to find the average request rate across _all time_ because that seems a little unforgiving doesn't it? Perhaps the user hit the wrong button, got up to make a cup of coffee, and upon returning found that they'd issues 2 million requests. Instead, we're only interested in the user's recent behavior. Let's represented the time history of the user's request rate as $$r(t)$$. The weight function, represented as $$w(t)$$, will be used to weight the more recent request rate (e.g. the $$r(t)$$ for t close to 0) as being more important than the request rate that occurred long ago (e.g. when t is a large negative number). In order to find the weighted average of the rate, we have to evaluate this integral.

$$
\int_{-\infty}^{0} w(t) \cdot  r(t)\:dt
$$

(This is very similar to [finding the expected value of a function](https://mathworld.wolfram.com/ExpectationValue.html) in statistics.)

As of yet, this equation is pretty vague. We can choose the weight function to be whatever we want, and the rate function will be controlled by the user's behavior, but for both of these we can make some assumptions that will simplify our work. Let's start with $$w(t)$$. The most obvious choice for a weight function which weights recent time more heavily is the exponential function:

$$
w(t) = \lambda e^{\lambda t} 
$$

<figure>
    <img src='/assets/TODO! insert figure.' alt='weighting and rate functions' class="centered"/>
    <figcaption>An exponential weight function along with an arbitrary rate function.</figcaption>
</figure>

The integral of this equation sums to 1 (a requirement for the weight function), and since we will choose $$\lambda$$ to be greater than 0, the weight function is fat near to current time and becomes exponentially thinner as we move back in time. The choice of an exponential function also brings some nice advantages further down in our analysis.

Since we're looking for the CEWMA of the rate function, let's look at a couple of important examples. What is the CEWMA if the rate is constant?

$$
\begin{matrix}
\int_{-\infty}^{0} w(t) \cdot  r(t)\:dt &=&  \int_{-\infty}^{0} w(t) \cdot  r\:dt \\ 
 &=& r \int_{-\infty}^{0} w(t) \:dt \\ 
&=& r \\ 
\end{matrix}
$$

Since the integral of a weight function is 1, all that is left is $$r$$.

If you're reading carefully, you might notice something weird about the rate function - it's continuous. What does it mean to have a rate of 0.6 requests per second? You can't do partial requests. Even though this feels non-intuitive, it is a generalization of the more realistic scenario where requests come in as discrete units. To demonstrate that you can still represent the more familiar case we need to introduce the idea of an "impulse" (also known as the [Dirac delta function](https://mathworld.wolfram.com/DeltaFunction.html)). An impulse is the application of an _infinitely_ high rate for an _infinitesimally_ short period of time. However the integral of impulse is finite. Whenever you make a request, what you're doing is creating an impulse in the request rate. In an instant the request rate goes infinitely high because it didn't take you a second to submit that request (which would be 1 request per second), it didn't take you a millisecond (which would be 1000 requests per second), it took the twinkling of an eye (which is one request per twinking). But once that moment passed, the actual _number_ of requests that you made (the integral of the rate) was just 1. (Ok, so that's a little difficult to justice in a single paragraph. Contact me on Twitter and I'll set up a time to explain it more clearly.)

An impulse of size $$N$$ (e.g. N requests in this case) and at some time $$T$$ is represented as `N\delta(t-T)`. And the CEWMA of this impulse function is

$$
\int_{-\infty}^{0}w(t) \cdot N\delta(t-T)= N \cdot w(T) = N\lambda  e^{\lambda T}
$$ 

If the time of the impulse is $$T=0$$ then you can simplify this even more to $$N\lambda$$. Finally, impulses add linearly, so the CEWMA for $$N_1$$ requests occurs simultaneously at $$T_1$$ and $$N_2$$ requests occuring at $$T_2$$ is $$N_1\lambda  e^{\lambda T_1} + N_2\lambda  e^{\lambda T_2}$$.

The last thing to notice is that there are many possible rate functions that can lead to the same CEWMA value. For example, let's say that $$\lambda = 0.07$$, then a request that just arrived (e.g. and impulse of size 1 at time 0) would have the same CEWMA as the constant application of 0.07 requests per second. This would also have the same CEWMA as 2 request occurring simultaneously 9.9 seconds ago.

$$
\begin{matrix}
\text{CEWMA of one request just now} &=& 1 \cdot \lambda &=& 0.07 \\
\text{CEWMA constant rate} &=& r &=& 0.07 \\
\text{CEWMA of 2 requests 9.9 seconds ago} &=& 2\cdot \lambda  e^{-9.9\lambda} &=& 0.07 \\
\end{matrix}
$$

This ability to move between different rates that lead to the same CEWMA is the crux of the algorithm that we lay out next.

## The Algorithm

We now have all the theoretical pieces required to build our Recent Average Rate Limiter. Our algorithm requires us to track 2 values, the time of the last update  $$T$$, and the "impulse size" $$N$$, which is basically our assumption that the all of the requests leading to the calculated CEWMA came in at time $$T$$. There are 4 methods for our rate limiter `initialize`, `update`, `evaluate`, and `rate_limited`:

`initialize` - We set $$T_0$$ and $$N_0$$ to 0.

`update` - For the first update we just set $$N_1=1$$ and $$T_1$$ to now (UNIX timestamp). For all subsequent updates $$T_{i-1}$$ corresponds to the last time a request came, and $$N_{i-1}$$ is some number representing how many requests were assumed to come at that moment. As in the examples at the end of the last section, we calculate the CEWMA of $$N_{i-1}}$$ request happening at $$T_{i-1}$$ plus 1 request (the new one) happening now. Given this CEWMA, we can find $$N_i$$ such that $$N_i$$ requests happening now has the same CEWMA:

$$
\begin{matrix}
\text{CEWMA of } N_{i-1} \text{ requests at } T_{i-1} \text{ and 1 more just now } &=&  N_{i-1}\cdot \lambda  e^{\lambda(T_{i-1}-now)} + 1 \cdot \lambda  \\
\text{CEWMA of } N_{i} \text{ requests just now } &=&  N_{i}\cdot \lambda  \\
\end{matrix}
$$

Setting both of these equations equal and solving for $$N_i$$ we arrive at $$N$$'s update equation.

$$
N_i = 1 + N_{i-1}  e^{\lambda(T_{i-1}-now)}
$$

$$T_i$$ is much simpler; we just set it to now.

`evaluate` - This is similar to `update` but we convert from a single impulse representation of the CEWMA to a constant rate representation:

$$
\begin{matrix}
\text{CEWMA of } N_{i} \text{ requests at } T_{i} &=&  N_{i}\cdot \lambda  e^{\lambda(T_{i}-now)}  \\
\text{CEWMA of a constant request rate } &=&  r  \\
\end{matrix}
$$

So the evaluation is 

$$
CEWMA = r = N_{i}\cdot \lambda e^{\lambda(T_{i}-now)}
$$

It's important to note that this rate is the "weird continuous rate" we talked about earlier which jars with the reality of discrete requests. However, as we'll see shortly, the continuous rate ends up being a good approximation to reality.

`rate_limited` - This is simple, if if the CEWMA is higher than the max allowed request rate, then `rate_limited` returns true, otherwise false. 

There's one bit we haven't discussed. How do you set $$\lambda$$? The most intuitive way is to think about the desired halflife for the CEWMA. Looking at the `evaluate` equation, you can see that if no more request are made after the last request, then the CEWMA value will decay exponentially. It can be shown that setting $$\lambda = -\text{ln}(0.5)/(\text{desired halflife})$$ will achieve the desired effect.

## In Code

The end result in Python looks like this:

```python
class RecentAverageRateLimiter:
    def __init__(self, halflife, rate_limit):
        self.N = 0
        self.T = 0
        self.lambd = -math.log(0.5)/halflife
        self.rate_limit = rate_limit
        
    def update(self, num_hits, now_timestamp):
        delta_t = self.T - now_timestamp
        self.N = num_hits + self.N*math.exp(self.lambd*delta_t)
        self.T = now_timestamp
        
    def evaluate(self, now_timestamp):
        delta_t = self.T - now_timestamp
        return self.N*self.lambd * math.exp(self.lambd*delta_t)
    
    def rate_limited(self, now_timestamp):
        return self.cewma.evaluate(now_timestamp) > self.rate_limit
```

Boy, that was a lot of math mumbo jumbo to arrive at a relatively simple algorithm. 

## Does it Really Work?
* decays to zero if there are no inputs
* asymptotic convergence - A steady train converges to a(1/(1-e^(?)))  - if halflife is large then this converges to exact solution 
* if you really wanted to, you could


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
* ask people to contact me if they want to understand better - especially that mumbojumbo about impulses