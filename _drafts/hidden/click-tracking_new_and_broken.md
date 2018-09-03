---
layout: post
title: Better Click Tracking for Identifying Statistically High Performers - Part 2
---

!!!!TODO add intro point to last time!!!!!



## Understanding Clickthrough in a Full E-Commerce Search Application

> **Milton Acme, Founder/CEO:** My boy! You done us good with your work so far...
>
> **Me:** Please don't call me "boy", Mr. Acme.
>
> **Milton Acme, Founder/CEO:** ...but I've got bigger plans for Acme Plumbing. We're going to bring the feeling of the old country store back into the interwebs. 
>
> **Me:** It's the "Internet," and I think it's time we talked about renegotiating my rate. 
>
> **Milton Acme, Founder/CEO:** ...because you see son, in our first location we had a fella there named Bert. Now in the rest of life Bert might have been an idiot, but when it came to our inventory he was a _genius!_ He knew our catalog cover to cover and knew where to find anything in the store. Some say that old Bert just had the "knack". ... This is what we need for our online store, we need a Bert!
>
> **Me:** Ok, great! So we're finally talking about a real, e-commerce search application!
>
> **Milton Acme, Founder/CEO:** Of course not! I'm talking about _a Bert_! People will come into the online store and ask the Bert where they can find things in our store and the Bert will show them what he knows.
>
> **Me:** Not a search app, a Bert.
>
> **Milton Acme, Founder/CEO:** Not "a Bert", _the_ Bert. Now get to work. I can't wait to see what you come up with.
 
Ok! So even if we have to call it "the Bert," we are at least in familiar territory of search applications. I quickly whip a simple one together and it looks like this:

!!!!! insert image _ Bert waving " hi, I'm the Bert, what can I help you find?"

I'm kinda warming up to the idea of "the Bert" now too. Bert seems nice and approachable just like Milton said he was in real life. 

Milton was pretty impressed with the statistically high clickthrough work I presented in our [last blog post]({{ site.baseurl }}{% post_url 2018-04-16-better-click-tracking-1 %}). So let's see if we can extend that work to a more complicated case of a full search application. First we'll need to create a ViewLog and a ClickLog similar to the last blog post. And this time we will need to add a new column to our tables called `placement` to keep track of where the items are showing up. The `placement` field will encode both the index where they appeared and the search that the user entered. For instance if an item appears in the second row of the result for a search for "cleaner" then it's placement will be recorded as `2-cleaner`. Here is a snippet of our ViewLog.

**ViewLog**

| exposure_id | product_id | placement |
|:----------:|:----------:|:----------:|
| 3218971 | tub_glue | 1-bathroom |
| 3218971 | presto_plunger | 2-bathroom |
| 3218971 | toilet_seat | 3-bathroom |
| ... | ... | ... |
| 7613493 | toilet_seat | 1-toilet |
| 7613493 | presto_plunger | 2-toilet | 
| ... | ... | ... |
| 8372966 | normal_ok_faucet | 1-kitchen-faucet |
| 8372966 | shiny_faucet | 2-kitchen-faucet |
| 8372966 | kitchen_pipe_thing | 3-kitchen-faucet |

Notice here that the same `exposure_id` occurs in several rows. This is how we group together all the results that were displayed during one search. For instance, at the top of the list in `exposure_id=3218971` we see that the user searched for "bathroom" and tub_glue, presto_plunger, and toilet_seat were the first, second, and third results.

Because all of the important placement details are encoded in the ViewLog, the ClickLog does not need to be changed. It will look something like this:

**ClickLog**
| exposure_id | product_id |
|:-----------:|:----------:|
| 3218971 | presto_plunger |
| 3218971 | toilet_seat |
| 7613493 | toilet_seat |
| 8372966 | normal_ok_faucet |
| 8372966 | shiny_faucet |
| 8372966 | kitchen_pipe_thing |

And just like in the last blog post we can join the ViewLog and ClickLog together and accumulate the view count and click count and get a table like this: 

|product_id | placement | click_count | view_count | clickthrough_rate |
|:----------:|:----------:|:----------:|:----------:|:----------:|
| presto_plunger | 1-bathroom | 88 | 7903 |  0.012 |
| toilet_seat |  2-bathroom | 41 | 379 | 0.108 |
| shiny_faucet |  3-bathroom | 1 | 3 | 0.333 |
| ... | ... | ... | ... |

But notice that rather than just rolling up the data by `product_id` we group by `(product_id, placement)`.
!START HERE - talk about how these fields can be joined together and connect it to next section

The difficulty comes when we realize that the `overall_clickthrough_rate` as defined above isn't as meaningful as it was with our Thing-o-the-Moment app which only had one slot. If we perform similar roll-ups as in the last blog post but group on `placement` we see these results.

!!!!consider adding the SQL since this is a new blog post!!!! 
!!!! add in product_id every row will have the same id!!!!

| placement | total_click_count | total_view_count | overall_clickthrough_rate | 
|:---------:|:-----------------:|:----------------:|:-------------------------:|
| 1-bathroom | 21325 | 178365 | 0.11956 |
| 2-bathroom | 9274 |  178365 | 0.05199 |
| 3-bathroom | 5421 |  178365 | 0.03039 |
| 4-bathroom | 2341 |  178365 | 0.01312 |
| 5-bathroom | 1074 |  178365 | 0.0060 |
| 6-bathroom | 531 |  178365 | 0.0029 |

So if an item has 5% clickthrough in the first result slot then this is par for the course, but if an item has 5% clickthrough in the 6th slot then it's performing _spectacularly_ above average. The problem is that any particular item will likely appear in several placement positions. Therefore you have to find a way to combine their statistics together.

Let's look at a simple example. Let's say that over the span of a day the bathtub appeared in placements 1 and 3 with the following views and clicks:

| placement | bathtub_click_count | bathtub_view_count | bathtub_clickthrough_rate | overall_clickthrough_rate |
|:----------:|:----------:|:----------:|:----------:|:----------:|
| 1 | 2 |  5 | 0.2 | 0.11956 |
| 3 | 1 | 2 | 0.5 | 0.03039 |
 
In both rows we see that per-placement the bathtub clickthrough rate well exceeds the overall clickthrough rate for the respective placements. But if our threshold for statistical significance is, say, 5%, then neither of these clickthrough rates are significant by themselves - the chance of getting 2 or more clicks in the first row is roughly 10% and the chance of getting 1 or more clicks on the second row is roughly 6%. But by combining the data together we can be much more confident that the bathtub really is a high performing item.

## Understanding the "Strength" of a Particular Item

Let's get an idea of "strength" of the bathtub relative to the other items. To do this we need to know the expected number of clicks that the bathtub would have received assuming that it is just an average performer. This is just the sum of the expected values for each placement. So looking at the first row, the item was seen 5 times with a presumed clickthrough rate of 12%, so the expected number of clicks for the first row is 0.5978. Similarly for the second row, the expected number of clicks is 0.0608. Thus the total expected number of click of 0.6586.

The ratio of the actual and the expected number of click is a good metric for how well the item is performing (this is what I'm calling the "strength"). In this case, the bathtub has 3/0.6586 or 4.55 times better performance than expected.

## Determining if the Strenght is Stastically Significant 

That seems good, but we still need to know if these results are statistically significant. As a reminder, we are using a p-value of 5% as a threshold of statistical significance. Following basically the same pattern as in the previous post !!!!link!!!!, we first ask this question: "Given the overall clickthrough rates associated with each placement, what is the probability _P_ that the bathtub could receive a total of _X_ or more clicks across all placements?" Then, given the resulting distribution we ask the next question: "Is it statistically significant that the bathtub has received 3 clicks?"

The "easy" way to determine the distribution would be to just add up the binomial distributions associated with each row in the click history summary. Unfortunately the probability parameter for each row is different (0.11956 vs. 0.03039 in this case) and to my knowledge there is no close-form way to sum binomial distributioned variables if the probability parameters are different. So let's bite the bullet and figure out the distribution the hard way.

First we'll need the individual distributions associated with each row. For placement 1, assuming 5 views and a clickthrough rate of 0.11956 we have the following click distribution

*placement 1*
| outcome | probability of getting _exactly_ this many clicks |
|:-------:|:-----------:|
| 0 clicks | 0.5290 |
| 1 clicks | 0.3592 |
| 2 clicks | 0.0976 |
| 3 clicks | 0.0133 |
| 4 clicks | 0.0009 |
| 5 clicks | 2.e-05 |

And for placement 3, assuming 2 views and a clickthrough rate of 0.03039 we have the following click distribution

*placement 3*
| outcome | probability of getting _exactly_ this many clicks |
|:-------:|:-----------:|
| 0 clicks | 0.9401 |
| 1 clicks | 0.0589 |
| 2 clicks | 0.0009 |

Given these tables we can build up the overall bathtub click distribution one possible outcome at a time. For instance, what are the chances that out of all 7 views the bathtub would have gotten exactly zero clicks? Well this means that we would have had 0 clicks for placement 1 - which happens 52.90% of the time; and 0 clicks for placement 3 - which happens 94.01% of the time. Since both of these outcomes have to happen for the total to be 0 clicks, then this implies that we need to multiply the probabilities together: 0.9401 * 0.5290 = 0.4973. Effectively we're saying "94.01% of 52.90% of the time - or 49.73% of the time - we get zero clicks".  Thus we have our first entry in our overall bathtub click distribution table:

*overall bathtub click distribution (incomplete)*
| outcome | probability of getting _exactly_ this many clicks | probability of getting _at least_ this many clicks |
|:-------:|:-----------:|:---------------------------------------------------|
| 0 clicks | 0.4974 | 1.00000 |

Next up, how many ways can the bathtub have a total of exactly 1 click? (Don't worry. We're not really going to go through all the possibilities. We just need one more example.) There are two ways that you could have a total of 1 click, but they can both be treated in just the same manner as the last paragraph: 

* Possibility 1: You received 0 clicks on placement 1 and 1 click on placement 3. This means that 5.89% of 52.90% the time - or 3.12% or the time - we are in this situation.
* Possibility 2: You received 1 click on placement 1 and 0 clicks on placement 3. This means that 94.01% of 35.92% the time - or 33.77% o5 the time - we are in this situation.

And to get the overall probability for getting a total of 1 click you just add up these two cases: 33.77% + 3.12% = 36.89% of the time you get 1 click. We now have our second row for the overall bathtub click distribution table, and we can populate the remaining rows similarly:

*overall bathtub click distribution*
| outcome | probability of getting _exactly_ this many clicks | probability of getting _at least_ this many clicks |
|:-------:|:-----------:|:---------------------------------------------------|
| 0 clicks | 0.49743 | 1.00000 |
| 1 click | 0.36886 | 0.50257 |
| 2 click | 0.11336 | 0.13371 |
| 3 click | 0.01855 | 0.02035 |
| 4 click | 0.00172 | 0.00181 |
| 5 click | 0.00009 | 0.00009 |
| 6 click | 2.3e-06 | 2.3e-06 |
| 7 click | 2.3e-08 | 2.3e-08 |

This third column of this table answers our first question "Given the overall clickthrough rates for each placement, what is the probability _P_ that you could receive a total of _X_ or more clicks?" Now we just need to answer the second question "Is it statistically significant that the bathtub has received 3 clicks?" Looking at our table we see that 3 or more clicks corresponds to a probability of 2.04% which is below our p-value of 5%. So indeed, the bathtub is a statistically significant high-performing item.

## So What All Can You Really Do With This?





The details of the last section got a little dense 

START HERE
* how to implement this
* extensions to statistically significant query performers and to making judgement lists
* make sure to end with Milton saying something  
  
COOL IDEA:
* cut this post in half and have ...to be continued (and link to the next post)
* Make a post about click tracking can work _per_ query and adding the query token into the document boosted by a payload 
* make another post for how this can be used to generate judgement lists


DON'T FORGET
* there's an issue with data sparseness when we start looking at individual searches
  * But this is partially handled when you note that pareto rule, 20% or less of unique searches correspond to 80% or more of traffic
* You also need to have several different eventsin each slot 1-bathroom has to have different events
* note shortcoming on not considering search text - we just have a global "goodness"
* spell check
* don't refer to "earlier" if I actually said it in the last post
* hyperlinke everything in this post and the last
* include photo of ACME
* maybe make ACME a plumbing store
* look at !!!!!s
* is it "clickthrough" or "click through"
* make sure the tables and the quote look correct
* How can we put the table headers on different lines?
* Highlight names in conversations
* Turn "Doug" into "Berny8"

```angular2html
import numpy as np
from collections import Counter

c1 = Counter()
size = 100000000
n = 5
p = 0.11956
c1.update(np.random.binomial(n, p, size))
total = 0
for i in range(n, -1, -1):
    prob = c1[i]/size
    total += prob
    print('{}: {}; {}'.format(i, prob, total))
    
c3 = Counter()
n = 2
p = 0.03039
c3.update(np.random.binomial(n, p, size))
total = 0
for i in range(n,-1,-1):
    prob = c3[i]/size
    total += prob
    print('{}: {}; {}'.format(i, prob, total))
    
overall = Counter()
for k1, v1 in c1.items():
    for k3, v3 in c3.items():
        k_o = k1+k3
        overall[k_o] = overall[k_o] + v1*v3/(size*size)    
```