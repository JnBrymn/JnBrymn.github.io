---
layout: post
title: Haystack Highlights
---
Slides https://docs.google.com/document/d/1gFZRkHNeIrXhQiU-erVhdtk2OlJLvVjqvVXRdZUjxq4/edit

# Day 1

## Doug's Keystone Talk
- slides: https://docs.google.com/presentation/d/1wTZpwvTy9eYFKfPemBtblArZFSIGFiOo7QhEjkTX2a8/edit
- Doug's Keystone: There are gaps in OSS search tech and the individual companies to combine efforts so that we're not solving the same problem over and over. Missing pieces:
- "turn silos into plungers to help save sea turtles" 
- (need that slide)

## Peter Fries: Search Quality: A Business Friendly Perspective
- slides: https://docs.google.com/presentation/d/e/2PACX-1vRmQ56QQJ5DB5rJAlTHgOkm4N18aQG9Fk6lYUdbiJhV7O3BSyfcbMLkVjRzTV2udAtZKwa4vFCiLNzs/pub?start=false&loop=false&delayms=3000&slide=id.g364c158e1a_0_157
- Antipatterns: Search Relevance is: 
    - bug squashing - always applying bandaids 
    - too hard - just give up
    - off limits
    - feeling 
    - relevance 
    - mysterious
* Visualize revenue over decile vs.query volume (search term) over volume.
- Search Evaluation Metrics - track these over time
    - MRR
    - MAP
    - Precision @K 
    - NDCG - hardest, best, difficult to communicate 
    - LGTM - looks good to me
- Business objectives - we need to connect to these (send these to Ray)
    - revenue
        - engagement 
        - market share
        - customer satisfaction
            - CTR
            - Acquisition
            - Retention 
                - Search Exists
                - Dwell time
                - Revenue Per Search
                - Pagination
                - Searches Per Session
                - SERP-tocart
                - zero clicks
                - thrashing
                - pogo stickings
                - search-rate
            - Conversion
            - Abandonment
- Feedback loops
    - Operations: integrate new ideas, a/b test, click tracking, evaluation
    - Lab: evaluation, relevance, automated testing
    
## Chao Han: Use customer behavior data and Machine Learning to improve relevance
- LucidWorks Fusion - add in signals and improve relevance; clicktracking, collaborative filtering
- head-n-and-tail analysis - measuring based upon clicks rather than searches
    - top {100/1%} queries lead to top N total events
    - "events" can be whatever - clicks/purchases
    - in the analysis you diagnose issues for tail queries 
        - misspellings
        - rare word
        - headquery + descriptive term: "foldable water bottle"
        * Fusion suggests rewrites = misspellings, rewording - basically tehy are trying to rewrite as a head query 
    - Fusion identifies patterns of errors in the long tail queries to try and pull them back into short tail queries - "red macbook case" -> "macbook case"^10 color:red
    - Fixes implemented as bandaids put together in control panel.
- auto generate synonyms - NOT related words, but synonyms!
- "clickstream for tail queries doesn't work well b/c it's sparse"


## Eric Bernhardson - From clicks to models, the Wikimedia LTR pipeline
- slides: https://upload.wikimedia.org/wikipedia/commons/4/4c/From_Clicks_to_Models_The_Wikimedia_LTR_Pipeline.pdf
- first step: build ML ranking to reproduce their current ranking
- 4 steps
    - click logs
    - label generation
    - features
    - training
- google - swapped 2 and 4 ans showsed that not only was clicks on 2 increased, but clicks on 1 were increased
* things we should do at eventbrite
    - multiple encodings of a field (stemmed, not)
    - phrase queries
* doc-only features, query only features, doc-query features
- mRMR feature selection
* what was the tech stack for actually serving the queries?
    - elasticsearch + LTR - they could stick
    - 
    
## Elizabeth Haubert: Expert Customers: A Hybrid Approach to Clickstream Analytics
- Need to understand MRR
- Cautionary tale of having humans make judgement lists 
    - TREC-4 and -5 failed. TREC-6 got better but was still slow
- Query chaining. 
* Query Session User features (good metrics)
    - Query - click position, num clicks, query length, pages, dwell time
    - session - queries per session, no click queries, session time, reformulations, URLS visited
    - User - num clicks per user, queries per user, ?, ? 
? - I need to make judgement lists. How do I deal with a quickly moving inventory?
    
# Day 2
    
## René Kriegler: 'A picture is worth a thousand words' - Approaches to search relevance scoring based on product data, including image recognition

- difficulty w/ e-commerce search: TF==1 for the words, not much information to go on
* if you're looking for a laptop then it's important to watch the words around "laptop" in the document, "asus" seems more laptoppy, "backpack" is probably a laptop backpack 
* Index tokens from random projections (I can use this for my experiment!)
- Jaquard similarity on the hash. (intersection/union)

? inception only represents 1000 labels - how well does the technique works on things not in inception - like a faucet
? do you save the vectors in the documents - are they stored as tokens? 
? how did you generate your judgement list

## Matt Overstreet: A Vespa Tour
- configuration
- linguistics
    - synonym
    - 
- ranking
    - `?yql:select * from sources * where userQuery()&query=tree`
    * you can do arbitrarily complex algorithms server side - the query language allows you to write pipelines. This keeps us from mixxing search logic in the client and in the server (ex "requery if no results") . I want to be able to write a BUNCH of queries to be run in parallel with their fallback scenarios. I want aggregation. On indexing I want to say "preaggregate x,y,z" (like max query score of a term in a field)
- Ranking - tf*idf, bm25 scoring - something similar is present, but it's hard to know how they work
    
## Ryan Pedela: Understanding Queries with NER
- Prodigy from Spacy - you can train tagging and it learns quickly
- Conditional Random Fields is the state of the art for named entity recognition
- Big idea: 
    - Train a labeler: "mcDonalds Corp" is a "company"
    - infer what a query: user queries "McDonald" and model say "it's a company" - then you construct a query that 
        - the must is just like normal
        - the should is company:McDonald 
- My hack: some classifiers will return a probability - add all the things as different clauses weighted by their probability

## Sujit Pal: Evolving a Medical Image Similarity Search
- slides: https://www.slideshare.net/sujitpal/evolving-a-medical-image-similarity-search
- this guy http://sujitpal.blogspot.com/
- LIRE (Lucene Image Retrieval Engine)
- Feature extraction
    - initially used RGB, HSV, edges, etc discretized/tokenized
    - ended up using deeplearning
- Indexing
    - Locality Sensitive Hashing LSH - same as Random Projections
    - Metric Spaces Indexing
    - Bag of Visual Words
    - Represent vectors as payloads with custom similarity (doesn't work well with large numbers of images)

## Trey Grainger: The Relevance of Solr's Semantic Knowledge Graph
- Semantic Query Parsing - understand what the phrases are: "data science job in nashville tennessee" -> "data science" "job" "nashville tennessee"
- Semantically Expanded Query - understand how to expand searches: "data science"-> "data science" "data mining" "machine learning"
- to figure out what is related to java: look up "java docs" in the inverted index, then for those docs look up the most common terms among those docs - the most common terms are then related scores
- forground vs. background analysis - the query is "hadoop" - the related terms are: "hive", "java", "mahout", "the". The foreground is the doc_count of the words within the results of a query for hadoop; the background is the doc_count words within the entire data set. 
- Example use: skill -> related skills -> jobs that have related skills
? "traverse the graph" - means run the forward/backward analysis, get "best terms" and then requery with this 
? how is this different than MLT?

## Peter Dixon-Moses: Catch My Drift? - Building bridges with Word Embeddings
- main idea - blur terms to expand the recall using word2vec
- talked about how word2vec skipgram formulation works
    - training set of input = two preceeding words and two following words - target is the word itself
    - neural network input is 4-by-10000; hidden layer is 300 neurons; output is 10000 softmax (each output represents a single term)
    - after training only keep the hidden layer
- to use - fund the neares words and stick them into the query as near synonyms but with a smaller boost
- One way of doing this: index payloads as `0|0.32 1|42.1 2|0.654` and use a script score to get at the payloads
- Idea from audience, store the vectors in the GPU memory and rerank them.


# Other talks that I wasn't able to attend
* [Suneel Marthi & Jeff Zemerick: Embracing Diversity: Searching over multiple languages](https://smarthi.github.io/haystack-embracing-diversity-searching-over-multiple-languages/), And [code from the Apache NiFi flow](https://github.com/jzonthemtn/multilanguage-search)
* [Tomasz Sobczak: Phrase Query Completion with Apache Solr and SuggestComponent](https://drive.google.com/file/d/1o2B3HIRl7EOIKhRDmzYSxuHH6aJRfhhg/view)
* [Xun Wang: Learning to Rank in an Hourly Job Marketplace](https://files.slack.com/files-pri/T47GJ9HLM-FA4UA2F9A/download/haystack_-_ltr_in_an_hourly_job_market__1_.pdf) (slack only)

#REMEMBER
* Get slides for everyone
* Get people to submit their summaries
* social
    * retweet blog here: https://twitter.com/softwaredoug/status/985257030683430912
    * post in the relevance thing


# Questions and Ideas for Eventbrite
- What is our search platform (feed, city browse, AUTOCOMPLETE)
- How many of our queries are satisfied by autocomplete? (We're not focusing upon it very well yet.)
- How many tickets are purchased away from a user's known location?
- Everybody was using relevance scoring (MRR, ERR, NDGC, etc) using click based (and some human based) judgement lists
- Can we look at our long tail queries and figure out which ones we can turn into head queries
    - bunch tail queries together using ryans methods based on requerying - and if a tail query is associate with a head query then we can tie them together somehow
- We should do NER to identify when a user is searching on a category vs. looking for text in the description, etc. 
- We can find related words
    - search for category aggregating tokens in the description field
    - search for common query words aggregating tokens in the description field
- Absolute, crystal clear focus on learning to rank to get the best results
- from Ryan and John's conversation:
    - make a NN to predict static event quality, regress linear combination of orders and clicks given static information
    - make dynamic NN to predict event quality based on static stuff plus dynamic things like day of week, category filters applied, etc.
        - the dynamic event quality thing might just output a "fingerprint" and then combine with the other half of the model that is run at runtime
    - can we predict that an event will sell out?
    - can we predict event quality for off-platform events that have different inputs than on-platform events?

# Personal ideas
- How to do word2vec but it should be able to disambiguate term sense: e.g. apple is a fruit or a computer
    - https://opensourceconnections.com/blog/2013/11/07/matrix-methods-for-term-sense-disambiguation/
- People interested in embedded vectors: Sujit Pal, Peter Dixon-Moses, René, Doug?