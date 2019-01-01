---
layout: post
title: Aircraft Control Theory - Applied to Product Growth
---

<figure>
    <img src='/assets/control-theory-applied-to-business/plane-flip.gif' alt='exponential distribution and percentile error' class="centered"/>
</figure>

Once upon a time, a long time ago, I was an aerospace engineer. One of the main goals of an aerospace engineer is (_duh_) to make sure you keep aircraft safely in the air. To do this, you must make sure that the aircraft is _stable_. Simplistically, _stability_ indicates that the forces acting upon the aircraft tend to correct any perturbation that acts upon the aircraft. For example, if a gust of wind pitches the nose of the aircraft upward, then an unstable aircraft will pitch further upward and soon start back flipping. A stable aircraft, on the other hand, will be naturally forced back towards level flight. I was recently reminded of my aerospace background when reading [a blog post by Brian Balfour (et al.) about product feedback loops](https://www.reforge.com/blog/growth-loops). His description of product feedback loops is, surprisingly, quite analogous to the aircraft feedback loops we see with aircraft. However, instead of air pressure forcing the aircraft to tip backwards more and more, we see things like social sharing causing a product to gain in more and more popularity. An interesting difference between aircraft dynamics and product dynamics is that, while you want aircraft to dampen out perturbations and return to straight and level flight, **you want products to exhibit instability** – you want a slight jump in popularity to give rise to more and more popularity and trigger exponential growth. It seems, then, that aerospace engineering may provide interesting tools for understanding just _how_ to trigger exponential product growth. Let's dig in!   

 
## A Shallow Dive into the Theory of Aircraft Stability
 
 Let's start by explaining just a little more about aircraft dynamics and stability. Let's say that we have a _really_ simplified model of an aircraft that has only two state variables, pitch, $$\theta$$, (that is, the angle between the aircraft and the ground); and pitch rate, $$\dot{\theta}$$, (e.g. how fast the pitch is changing). Let's look at the _difference_ equations that describe how the aircraft state changes over some short period of time $$T$$ (say 0.1 seconds). First, pitch:
 
 $$\theta' = \theta + \dot{\theta}T$$
   
 In English - the pitch at the next time step ($$\theta'$$) equals whatever the current pitch is plus a delta corresponding to how fast the pitch is changing. Next the pitch rate:
 
 $$\dot{\theta}' = \dot{\theta} - \dot{\theta}Td + \theta Tk$$
  
 This equation might be easier to understand if we rearrange and look at the _change_ in pitch rate: $$\dot{\theta}' - \dot{\theta} = - \dot{\theta}Td + \theta Tk$$. There are two pieces here. First $$-\dot{\theta}Td$$ indicates that the change in pitch rate is proportional to its current pitch rate and is damped out according to the damping constant, $$d$$. The easy way to think about this is as the damping effect of wind resistance – the faster you're moving, the harder the wind pushes in the opposite direction. Next $$\theta Tk$$ indicates that the pitch rate is proportional to the current pitch times some constant $$k$$. This provides some insight into the stability of the aircraft. If the nose of the aircraft pitches up (positive $$\theta$$) and if $$k$$ is positive, then the equation above indicate that things are just going to get worse! The pitch rate will _increase_ and soon we'll be doing backflips! However if $$k$$ is negative then any increase in pitch will result in a decrease in pitch rate, tending to correct our motion back towards straing and level flight.
 
 It's not clear when this aircraft will be stable and when it won't. For some values of $$k$$ and $$d$$ the aircraft will correct departures from straight and level flight and for some values, the aircraft will start doing backflips. For real aircraft things get much more complicated – more equations, more complicated equations, and more constants. Fortunately, no matter how complicated the situation, we can lean upon lessons from linear algebra in order to derive conclusions about aircraft stability.
 
 First we need to reorganize our equations into matrix format. For our example the above equations get construed into this format:

$$
	\begin{bmatrix}
	\theta' \\
	\dot{\theta}' \\
	\end{bmatrix}
	=
	\begin{bmatrix}
	1 & T \\
	Tk & 1 -Td \\
	\end{bmatrix}
	\begin{bmatrix}
	\theta \\
	\dot{\theta} \\
	\end{bmatrix}	
$$

From here on I'm going to go light on the mathematical details – after all I'm trying to point out a metaphor between aircraft dynamics and aircraft dynamics - I'm _not_ trying to cram a Master's degree into a blog post! Given the above matrix equation we can easily find the characteristic equation for the the system:

$$
\lambda^2 + \lambda(Td-2) + 1 + Td - t^2k
$$

The important thing here is that roots of the characteristic equation define the stability of the system. If the magnitude of the roots are greater than 1, then the system will be unstable. Using the quadratic equation, the roots are:

$$
1 -\frac{T}{2} \left( d \pm \sqrt{d^2 + 4k} \right)
$$

And finally we have something of an answer. Given a particular aircraft, the shape of the aircraft and the distribution of mass will control the values for $$d$$ and $$k$$, so we can plug these numbers in and see if the result has a magnitude in excess of 1.0. If so – backflips! However, if you are the designer of the aircraft, you control the shape and mass distribution of the aircraft - so if the aircraft isn't stable, you have the ability to modify $$d$$ and $$k$$ and fix it!

## Back to the Big Picture

I must say, we're in the weeds aren't we now? You probably didn't expect to get a math lesson. Let's step back and look at the big picture. Aircraft are complicated systems, but you can describe complicated systems in matrix form as shown above. Given this standardized form, there are known and _relatively_ straightforward equations that can be applied to see if the system will be stable. If you don't like what the equations are telling you (_backflipping airplanes are bad_), then you can modify the system and change the stability of the system.

In the broader realm, this technique is applied to more than just aircraft. The same analysis can be applied to any complicated dynamic system - _including product dynamics!_   

## Applying Stability Theory to Product Growth Dynamics

So if the states of the aircraft correspond to speed, angles, and angular rates, then what states does a product have? Well, how about things like page views, shares, and conversions? Each step in the funnel represents some relatively straightforward equations that you can glean from your product analytics. For instance:

$$
	\begin{matrix}
	\textrm{purchase}' = \textrm{page_view} \times \textrm{conversion_rate} \\
	\textrm{share}' = \textrm{page_view} \times \textrm{share_rate} \\
	\end{matrix}
$$

Here $$\textrm{conversion_rate}$$ and $$\textrm{share_rate}$$ are the constants of your system in much the same way that that $$k$$ and $$d$$ were the constants associated with the aircraft above.

This is a good start, but the product, as currently modeled, has no feedback. Consider the aircraft: when the pitch was increased, then the pitch rate was affected. Then, in turn, the pitch rate directly controls the updated pitch angle. This feedback is what causes the system to be self-regulating. Feedback is the very thing that [Brian Balfour's "growth-loops" blog post](https://www.reforge.com/blog/growth-loops) was emphasizing. What would feedback look like for product dynamics? Well, shares would generate a certain number follow-on page-views. Also, purchases indicate a user making an investment in our platform, so this too would drive downstream page views. All together, this implies that we stick in one more equation: 

$$
	\textrm{page_view}' =  \textrm{share} \times \textrm{shares_viewed_rate} \;+\;\textrm{purchase} \times \textrm{return_after_purchase_rate}  
$$

All together, here is our product dynamics equation:

$$
	\begin{bmatrix}
        \textrm{purchase}' \\
        \textrm{share}' \\
        \textrm{page_view}' \\
	\end{bmatrix}
	=
	\begin{bmatrix}
        0 & 0 & \textrm{conversion_rate} \\
        0 & 0 & \textrm{share_rate} \\
        \textrm{return_after_purchase_rate} & \textrm{shares_viewed_rate} & 0 \\
	\end{bmatrix}
	\begin{bmatrix}
        \textrm{purchase} \\
        \textrm{share} \\
        \textrm{page_view} \\
	\end{bmatrix}		
$$
  
So, now we have a matrix full of parameters with known values that we can draw from our product analytics. Just like in the aircraft example, if we find the characteristic equation then we can find the roots which determine the stability of the system. Now... I won't do that this time, because it's hard, and it's New Year's Eve, and, well, I've been drinking a bit. _But it can be done!_ And when you're finished, you end up with an equation that is the function of known constants; in this case $$\textrm{conversion_rate}$$, $$\textrm{share_rate}$$, $$\textrm{return_after_purchase_rate}$$, and $$\textrm{shares_viewed_rate}$$.

Here's the kicker though. With an aircraft, if the system is unstable, then a slight perturbation results in a larger and larger divergence from normal flight until suddenly, you're backflipping. With a product though, you actually _want_ this divergence. You want a slight increase in popularity to feedback and result in more and more popularity. _You want instability._ And since the constants in the equation are all under your control, then exponential divergence can be _crafted_.

There are three steps here:
1. First, model the dynamics of your product as shown in this section. This is _hard_, though in principle it can be done. The end result is an equation like the one shown above.
2. Second, find the roots of the characteristic equation in terms of the product analytics constants.
3. Finally, chose which constants to _improve_ so that your system is more likely to diverge in an explosion of growth.

Perhaps steps 2 and 3 should be merged. In that case you wouldn't necessarily solve for the roots of the characteristic equation. Instead, you would perform some sort of sensitivity analysis to determine what effect moving the production constants would have upon stability. You would then compare this information with how "movable" you believe each of those constants to be and let the combined information (sensitivity and mobility) instruct your next moves.

## Caveats
This is a blog post, not a grad-level control systems course. I'm skipping over lots of details and being a bit loose with academic rigor. For instance, complex systems are rarely linear, and I'm ignoring the possibility of oscillating divergence. For this blog post specifically, a big thing that I brushed over is the notion of a time step. Notice that the original aircraft example involved a time step $$T$$ that represents the time between some state $$\theta$$ and the subsequent state $$\theta'$$. _Really_ we need something like that for the product dynamics equation to be valid. However I think we _can_ find some appropriate way to introduce a time step. For instance $$T$$ can be one day because that's a reasonable time increment for most product analytics. The problem would come in dealing with product states that evolve at very different time frames, $$T$$ = 1 second vs 1 day.

## Conclusion
What I've introduced is an interesting analogy that allows us to think about product dynamics in the same way that we think about the very well understood field of aircraft dynamics. In principle, the analyses presented here are doable. In practice I suspect that it is quite difficult to gather all of the analytics, assemble them into a reasonable model, and make strategic decisions based on the model. Nevertheless, the thought experiment _by itself_ is worthwhile. Back to the point of the [original blog post that I'm responding to](https://www.reforge.com/blog/growth-loops), we shouldn't be thinking about our product as a series of funnels because that's only part of the picture. Rather, the _bigger picture_ is to think about products as complex dynamic systems that include loops of feedback. By digging into this more complete understanding of our products we might be able to make the changes required to ignite divergent growth in our products.
