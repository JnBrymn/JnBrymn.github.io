---
layout: post
title: Teaching Abusive Users a Lesson with EARRRL – the Estimated Average Recent Request Rate Limiter
---

You've got a problem: a small subset of abusive users are body slamming your API with extremely high request rates. You've added windowed rate limiting, and this reduces the load on your infrastructure, but behavior persists. These naughty users aren't attempting to rate-limit their own requests. They fire off as many requests as they can, immediately hit `HTTP 429 Too Many Requests`, _don't let up_, and as soon as a new rate limit window is available, the pattern starts all over again.

In order to curtail this behavior, it would be nice to penalize bad users according to their _recent average_ request rate. If a user responsibly limits their own requests, then they never get a 429. However if the user has the bad habit of _constantly_ exceeding the rate limit, then we stop them from making any more requests – _ever_. No new windows, no second chances... _until_ they mend their ways and start monitoring their own rate more responsibly. Once their average request rate falls below a threshold, then their past sins are forgiven, and they may begin anew as a responsible user of our API.

TODO! photo of vile abuser

## Introducing the Recent Average Rate Limiter

But there's hope! Drawing inspiration from the [Exponentially Weighted Moving Average](https://github.com/VividCortex/ewma), I propose EARRRL, the Estimated Average Recent Request Rate Limiter. EARRRL estimates the user's recent request rate and rejects requests for users who's request rate exceeds the specified threshold. Here's a Python implementation:

```python
class EARRRL:
    def __init__(self, halflife, rate_limit):
        self.N = 0
        self.T = 0
        self.lambd = -math.log(0.5)/halflife
        self.rate_limit = rate_limit
        
    def rate_limited(self):
        rate_limited = self.evaluate() > self.rate_limit
        self._update(num_hits=1)
        return rate_limited
    
    def _update(self, num_hits=1):
        now_timestamp = time.time()  # unix time in seconds
        delta_t = self.T - now_timestamp
        self.N = num_hits + self.N*math.exp(self.lambd*delta_t)
        self.T = now_timestamp
        
    def evaluate(self):
        now_timestamp = time.time()
        delta_t = self.T - now_timestamp
        return self.N*self.lambd * math.exp(self.lambd*delta_t)
```

To use this, whenever a user makes a request, retrieve their rate limiter or otherwise create a new EARRRL to track their request rate.

```python
rate_limiters = {}

def index(request):
    rate_limiter = rate_limiters.get(request.user.id) 
    if rate_limiter is None:
        rate_limiter = rate_limiters[request.user.id] = EARRRL(halflife=10.0, rate_limit=0.5)
    
    if rate_limiter.rate_limited():
        return render(request, '429.html', status=429) 
    
    # otherwise render the view
```

Also, if you'd like to directly check the current estimated request rate, call `rate_limiter.evaluate()`.

For me, the mathy bits about how this all works are the _real_ fun stuff. But I won't bore you with those details for this post. However if you're a math geek like me, then I hope you'll take a look at my EARRRL companion post which gets into the nitty gritty details. #TODO! link

## Demo Time

Let's see EARRRL in action!

<figure>
    <img src='/assets/estimated-average-recent-request-rate-limiter/filter-estimate-halflife-10.png' alt='EARRRL tracking periodic requests at 3 different rates' class="centered"/>
</figure>

This figure illustrates the scenario where at $$t=50\text{s}$$ users start making sustained periodic requests and then at $$t=200\text{s}$$ they stop. The user represented by red makes 10 requests per second, the green user makes 1 request per second, and the blue user makes one request every 10 seconds. The corresponding lines in this figure represents the estimated average request rate. As you can see, it takes a short period of time for the estimate to saturate, but in about a minutes time the estimates converge to the true rate.

At $$t=200\text{s}$$ the user quits making requests and the corresponding estimates fall off quickly. The EARRRL for this figure uses a half-life of 10 seconds, and you can see evidence of this in the plot, because 10 seconds after the requests start, the estimates rises to half of the true request rate. Similarly 10 seconds after the requests end, the estimates decay halfway back to 0. Because of this, you can use the half-life to control how quickly the estimator track the user rate. However beware, there is a tradeoff between half-life and estimate error, the lower the half-life, the higher the error. As an example, here is a plot of the same scenario but with a half-life of 1 second.

<figure>
    <img src='/assets/estimated-average-recent-request-rate-limiter/filter-estimate-halflife-1.png' alt='EARRRL tracking periodic requests at 3 different rates' class="centered"/>
</figure>

Additionally, when configuring the half-life, remember that the whole goal is to penalize people misusing your API. Decreasing the half-life too much will effectively make EARRRL forget the abuse too quickly and allow the bad actors to offend again.



## Conclusion
Reread intro first
* windowed no better or worse than CEWMA, but the rate limits are treated differently
  * after a grace period, CEWMA puts offenders in timeout as long as they keep offending, but after they mend their ways the CEWMA cools down (per the half-life) it lets them start again
  * windowed is much more permissive of persistent abuse, it lets them in again with every window renewal
  * the CEWMA behavior has an interesting behavior in that it _REQUIRES_ the clients to be well behaved, and if they are not then this eliminates a very common type of abuse completely and instantly. So it's not just their requests that will be blocked, but you'll no longer have the entire class of user that just sprays requests and then depends on 429s from _your server_ to act as their rate limiting.
  * the longer and the more extremely they are misbehaved, the longer they will remain in timeout
  * you no longer have to investigate heavy hitters and then later ban them - they ban themselves effectively
* If you don't like this behavior, you can count overage requests as having a fraction of the weight that normal requests have (because, after all, they didn't really cost much to your infrastructure) - this will let their CEWMA decay faster. But IF they are still really over the exceptable rate, then this will never cool down
  

## Implementation in Redis
* instead of TTL, LRU expire them and completely forego 
* https://redis.io/topics/quickstart
* https://www.compose.com/articles/a-quick-guide-to-redis-lua-scripting/
* OBJECT IDELTIME https://github.com/redis/redis/issues/1258


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