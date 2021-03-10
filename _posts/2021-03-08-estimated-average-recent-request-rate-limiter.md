---
layout: post
title: Teaching Abusive Users a Lesson with EARRRL – the Estimated Average Recent Request Rate Limiter
---

You've got a problem: a small subset of abusive users are body slamming your API with extremely high request rates. You've added windowed rate limiting, and this reduces the load on your infrastructure, but behavior persists. These naughty users aren't attempting to rate-limit their own requests. They fire off as many requests as they can, almost immediately hit `HTTP 429 Too Many Requests`, _don't let up_, and as soon as a new rate limit window is available, the pattern starts all over again.

In order to curtail this behavior, it would be nice to penalize bad users according to their _recent average_ request rate. If a user responsibly limits their own requests, then they never get a 429. However if the user has the bad habit of _constantly_ exceeding the rate limit, then we stop them from making any more requests – _ever_. No new windows, no second chances... _until_ they mend their ways and start monitoring their own rate more responsibly. Once their average request rate falls below a threshold, then their past sins are forgiven, and they may begin anew as a responsible user of our API.

TODO! photo of vile abuser

## Introducing the Recent Average Rate Limiter

Drawing inspiration from the [Exponentially Weighted Moving Average](https://github.com/VividCortex/ewma), I propose EARRRL, the Estimated Average Recent Request Rate Limiter. EARRRL estimates the user's recent request rate and rejects requests for users who's request rate exceeds the specified threshold. Here's a Python implementation:

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
        rate_limiter = EARRRL(halflife=10.0, rate_limit=0.5)
        rate_limiters[request.user.id] = rate_limiter
    
    if rate_limiter.rate_limited():
        return render(request, '429.html', status=429) 
    
    # ... otherwise render the view
```

Also, if you'd like to directly check the current estimated request rate, call `rate_limiter.evaluate()`.

For me, the mathy bits about how this all works are the _real_ fun stuff. But I won't bore you with those details for this post. However if you're a math geek like me, then I hope you'll take a look at my EARRRL companion post which gets into the nitty gritty details. #TODO! link

## Demo Time

Let's see EARRRL in action!

### Convergence

<figure>
    <img src='/assets/estimated-average-recent-request-rate-limiter/filter-estimate-halflife-10.png' alt='EARRRL tracking periodic requests at 3 different rates' class="centered"/>
</figure>

This figure illustrates the scenario where at $$t=50\text{s}$$ users start making sustained periodic requests and then at $$t=200\text{s}$$ they stop. The user represented by red makes 10 requests per second, the green user makes 1 request per second, and the blue user makes one request every 10 seconds. The corresponding lines in this figure represents the estimated average request rate. As you can see, it takes a short period of time for the estimate to saturate, but in about a minutes time the estimates converge to the true rate.

At $$t=200\text{s}$$ the user quits making requests and the corresponding estimates fall off quickly. The EARRRL for this figure uses a half-life of 10 seconds, and you can see evidence of this in the plot, because 10 seconds after the requests start, the estimates rises to half of the true request rate. Similarly 10 seconds after the requests end, the estimates decay halfway back to 0. Because of this, you can use the half-life to control how quickly the estimator track the user rate. However beware, there is a tradeoff between half-life and estimate error, the lower the half-life, the higher the error. As an example, here is a plot of the same scenario but with a half-life of 1 second.

<figure>
    <img src='/assets/estimated-average-recent-request-rate-limiter/filter-estimate-halflife-1.png' alt='EARRRL tracking periodic requests at 3 different rates' class="centered"/>
</figure>

The increased error with lower half-life values is effectively caused because the rate limiter learns too fast, and temporary spike in a user's request rate will send them above the rate limit threshold. But if you go too far in the other direction, an excessively long half-life will cause EARRRL to learn too slowly and a spammy user will fire off more requests than desired before EARRRL catches on. This shouldn't be too hard to deal with, you just need to be mindful of these potential problems when setting the half-life.

### Comparison Between EARRRL and Windowed Rate Limiters
In the opening, I posted a gripe I had against windowed rate limiters. At the ending of every single window, all since are forgiven, and the rate limit is completely reset. Spammy users rejoice, because they can just keep firing off requests as fast as they please until someone from platform health catches on and bans them. (And then they just make another user and start over again.)

Here's what rate limiting looks like with a windowed rate limiter.

<figure>
    <img src='/assets/estimated-average-recent-request-rate-limiter/WRL-recovery-after-naughty-user-reforms.png' alt='Windowed Rate Limiter' class="centered"/>
</figure>

Here, initially, the user is making requests at a rate 67% higher than what is allowed. The red line represents the user's cumulative number of requests, and the blue line represent the cumulative number of requests that are permitted. Can you see the pattern? At the beginning of every window the spammy user quickly meets their quota of requests and gets cut off, but they nevertheless keep sending requests (red line). Then at the next window the process starts over again. No good.

In order to compare the differences between windowed rate limiters and EARRRL, at 150s the user in this example decided to reduce their rate to exactly match the rate threshold, and in the case of windowed rate limiters, their requests now all succeed.

Let's see what happens with EARRRL in this exact same scenario.      

<figure>
    <img src='/assets/estimated-average-recent-request-rate-limiter/EARRRL-recovery-after-naughty-user-reforms.png' alt='EARRRL' class="centered"/>
</figure>

As you can see, EARRRL is more shrewed. Initially it provides the user with a longer grace period than the windowed rate limiter, but then after it decides that this is not a fluke and that the user plans on abusing the rate limit, it locks down and does not let any more requests through. Unlike the naive windowed rate limiter, EARRRL does not constantly forgive the user and let them abuse again. Rather it waits. Once it decides that the user has reformed and the request rates will remain within appropriate bounds, it allows requests to proceed again.


## Implementation in Redis

As I alluded to above, Python is probably not the language you want for implementing this approach... [Lua is](https://en.wikipedia.org/wiki/Lua_(programming_language)). Why? Because Lua is the built-in scripting language for redis and redis is the _ideal_ framework for building EARRRL. Let's see it in action. Here is the Lua/Redis implementation for an EARRRL with a rate limit of 0.5 requests per second and a half-life of 10s (save this to EARRRL.lua). 

```lua
-- parameters and state
local lambda = 0.06931471805599453 -- 10 seconds half-life
local rate_limit = 0.5
local time_array = redis.call("time")
local now = time_array[1]+0.000001*time_array[2] -- seconds + microseconds
local Nkey = KEYS[1]..":N"
local Tkey = KEYS[1]..":T"

local N = redis.call("get", Nkey)
if N == false then
  N = 0
end

local T = redis.call("get", Tkey)
if T == false then
  T = 0
end

local delta_t = T-now

-- functions
local function evaluate()
  return N*lambda*math.exp(lambda*delta_t)
end

local function update()
  redis.call("set", Nkey, 1+N*math.exp(lambda*delta_t))
  redis.call("set", Tkey, now)
end

local function rate_limited()
  local estimated_rate = evaluate()
  local limited = estimated_rate > rate_limit
  update()
  return {limited, tostring(estimated_rate)}
end

-- the whole big show
return rate_limited()
```

This is my first time playing with Lua/Redis but I found it quite easy to work with, and even fun! One new thing to notice here is how we deal with Redis keys. A user's `N` (num requests) value is stored in `user_key_123:N` and the user's `T` (last request time) value is stored in `user_key_123:T`. If either of these keys doesn't exist, then they are assumed to be 0 which effectively means that the estimated rate is zero. But the end of the script, the user's `N` and `T` values are guaranteed to exist in Redis.  
 
 Now since we have the script ready, let's upload it to redis.

```sh
$ redis-cli SCRIPT LOAD "$(cat earrrl.lua)"
"cb3696c74cc51596d07646e64a17f5f2db510adb"
```

The SHA that gets returned is an identifier used to invoke the script. Like so:

```sh
$ redis-cli EVALSHA cb3696c74cc51596d07646e64a17f5f2db510adb 1 user_key_321
```

The first argument after the SHA tell redis how many keys will be passed in, and the second argument in this case is the key, an identifier for the user that just made a request.

Does it work? I dunno, let's find out. Let's do an experiment that tests 2 aspects of EARRRL: convergence to the correct value and expected convergence rate. Here's our test script:

```sh
$ for i in {0..70} true
  do 
    sleep 1
    echo "request # $i"
    redis-cli EVALSHA cb3696c74cc51596d07646e64a17f5f2db510adb 1 user_key_321
  done
  sleep 10  # the half-life
  redis-cli EVALSHA cb3696c74cc51596d07646e64a17f5f2db510adb 1 user_key_321
```

Since we are sleeping 1 second between each hit, our request rate is 1 per second. We know that with a half-life of 10 seconds, the algorithm should be about half way to this value by the 10th request.

```sh
request #0
1) (nil)      <------------ this means "rate limit not exceeded"
2) "0"
request #1
1) (nil)
2) "0.064625593423117"
request #2
1) (nil)
2) "0.12483578218756"
request #3
1) (nil)
2) "0.18093794941434"
request #4
1) (nil)
2) "0.2332841604735"
request #5
1) (nil)
2) "0.28208311764286"
request #6
1) (nil)
2) "0.32757287863479"
request #7
1) (nil)
2) "0.36998350934232"
request #8
1) (nil)
2) "0.40940326068647"
request #9
1) (nil)
2) "0.44628146174133"
request #10
1) (nil)
2) "0.48060100760135"
request #11
1) (integer) 1      <------------ this means "rate limit IS exceeded"
2) "0.51262461170605"
```

This looks about right. Notice that at request 11 we have hit the rate limit as represented by `(integer) 1`. Next we want to make sure that that at steady state (say after 7 half-lives) that the value should converge to the true rate of 1.0.

```sh
request #70
1) (integer) 1
2) "0.94514712058575"
```

Close, but not quite. However, there is a reasonable explanation for this. Our rate evaluation comes before we update the EARRRL state. That means in this case, the rate has had roughly 1 second to decay before we evaluate it. If we evaluate just after the update, it will actually evaulate a bit _above_ 1 request per second. So this is the expected behavior. If you would like to have less error here, then a longer half-life is required.

Finally, let's check that 10 seconds after the last request, the estimated rate has decayed to half of what it was when the requests ended.

```sh
1) (integer) 1
2) "0.50703163627721"
``` 

Yep. So it seems that it works.

The last ingredient in a Redis deployment is how to deal with the lifetime of the keys. With the windowed rate limiters, the keys are given a TTL of, say, 1 minute. This is _not_ what you want to do with EARRRL because that makes EARRRL forget past offenses and EARRRL effectively becomes an overly complicated windowed rate limiter. _Instead_ the keys need to be LRU'ed. This way, the aggressive offenders will remain in EARRRL's memory as long as they remain active. This is a very natural choice because users who get expelled based on LRU probably have a rate limit low enough to justify being expelled anyway.
 


## Conclusion
Reread intro first
* windowed no better or worse than CEWMA, but the rate limits are treated differently
  * after a grace period, CEWMA puts offenders in timeout as long as they keep offending, but after they mend their ways the CEWMA cools down (per the half-life) it lets them start again
  * windowed is much more permissive of persistent abuse, it lets them in again with every window renewal
  * the CEWMA behavior has an interesting behavior in that it _REQUIRES_ the clients to be well behaved, and if they are not then this eliminates a very common type of abuse completely and instantly. So it's not just their requests that will be blocked, but you'll no longer have the entire class of user that just sprays requests and then depends on 429s from _your server_ to act as their rate limiting.
  * the longer and the more extremely they are misbehaved, the longer they will remain in timeout
  * you no longer have to investigate heavy hitters and then later ban them - they ban themselves effectively
* If you don't like this behavior, you can count overage requests as having a fraction of the weight that normal requests have (because, after all, they didn't really cost much to your infrastructure) - this will let their CEWMA decay faster. But IF they are still really over the exceptable rate, then this will never cool down
  


## Disclaimers
* Is this out there all ready? Maybe?
* Am I accurate? Maybe?


## DON;T FIRGET
* if you're concerned about users using just a little over their rate being permanently banned (this _would_ happen!) then you can just make the overage hits count less. This way the rate will die down more quickly UNLESS the are really slamming the search
* ask people to contact me if they want to understand better - especially that mumbojumbo about impulses
* final note: I'm renaming this to the EARRRRL