---
layout: post
title:  "Example Post"
date:   2000-01-02 00:01:01 #overrides date from file name - but isn't necessary
categories: jekyll update
---
Here is an example MathJax inline rendering \\( 1/x^{2} \\), and here \\( x_4 \\) is a block rendering: 
\\[ \frac{1}{n^{2}} \\]

You'll find this post in your `_posts` directory - edit this post and re-build (or run with the `-w` switch) to see your changes!
To add new posts, simply add a file in the `_posts` directory that follows the convention: YYYY-MM-DD-name-of-post.ext.

Jekyll also offers powerful support for code snippets:

I think you can refer to data in the data files like this: {{ site.data.example.example }}

$$\sum_{n=1}^\infty 1/n^2 = \frac{\pi^2}{6}$$

{% highlight ruby %}
def print_hi(name)
  puts "Hi, #{name}"
end
print_hi('Tom')
#=> prints 'Hi, Tom' to STDOUT.
{% endhighlight %}




This might just be a picture of a cat:

![some cats]({{ site.url }}/assets/example.jpg)

Site time: {{ site.time }}

Check out the [Jekyll docs](https://github.com/mojombo/jekyll) for more info on how to get the most out of Jekyll. File all bugs/feature requests at [Jekyll's GitHub repo][https://github.com/mojombo/jekyll).

