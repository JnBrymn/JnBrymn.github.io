---
layout: post
title: Tokenizing Embedding Spaces for Faster, More Relevant Search
---

Embedding spaces are quite trendy right now machine learning. With word2vec for example, you can create an embedding for words that is capable of capturing analogy. Given the input "_man_ is to _king_ as _woman_ is to what?", a word2vec embedding can be used to correctly answer "_queen_". (Remarkable isn't it?) Embeddings like this can be used for a wide variety of different domains. For example, facial photos can be projected into an embedding space and for tasks of facial recognition. However I wonder if embeddings fall short in a domain that I am very near to - search. Consider the facial recognition task: Each face photo is converted into an N-dimensional vector where N is often rather high (hundreds of values). Given a sample photograph of a face, if you want to find all of the photos of that person then you have to search for all the photo vectors near to the sample photo's vector. But, due to the curse of dimensionality, very high dimensional embedding spaces are not amenable to data structure commonly used for spatial search, such as k-d trees.

Maybe we can take a lesson from search, because search engines have no problem at all with high-dimensional feature spaces. Consider a feature vector for an English document, say, a description of a product in a catalog. In principle, the cardinality of this feature vector is giant - one floating point value for each word in the English vocabulary. This is a bit misleading of course; the representation used by search engines is very sparse - most documents do not contain most words in the English vocabulary - so the feature vector is mostly zeros. However the point I'm making still stands: search engines are good at finding matches in high-dimensional feature sets. Given a query - a set of words - _a.k.a. a sparsely-encoded, high-dimensional feature vector_ - then a search engine can very quickly identify all the documents that contain these words - _a.k.a. all similar feature vectors_.
 
## Using Search Technology for Large Scale Face Recognition Tasks
 
So let's go back the the face recognition task. Let's say we have a data set of every photograph of every face on Facebook and we want to make a face search application. If somehow we could _tokenize_ a face - that is, convert it into a bunch of symbols similar to words in a text document - then we could reduce facial recognition to a simple application of search. What would this look like? Well in principle you could assemble an army of well trained curators to write up a tagged description of each face. The tags could read something like this
 
 > `{caucasian, fair-complexion, straight-hair, black-hair, receeding-hairline, bald, no-beard, no-facial-hair, caterpillar-eyebrowse, arched-eyebrows, black-eyecolor, small-iris, bulging-eyes, large-nose, blubous-nose, broad-smile, missing-teeth, kinda-sinister-looking}`

(In this example, our curators are obviously describing [Gargamel](https://en.wikipedia.org/wiki/Gargamel).)

<figure>
    <img src='/assets/gargamel.png' alt='missing' class="centered"/>
</figure>

Given an index full of similarly tagged facial photos, someone searching for a new face would proceed as follows. First they would have a curator tag their face photo. (Don't worry, we'll relax this silly requirement in a moment.) Then they would make a _textual_ search of these tags against the face search index. The search engine would quickly narrow the result down to only those that shared much of the terms in the query. Notice that a nice benefit of sparsely encoding faces as tags is that you become robust to missing or even incorrect information. For instance, if Gargamel wore a disguise as shown in the photo below, he would still have `{black-hair, large-nose, bulbous-nose, bulging-eyes}` and his photos would still be present in the filtered set of images!

<figure>
    <img src='/assets/gargamel_in_disguise.png' alt='missing' class="centered"/>
</figure> 
 
Once the filtering step is done, the surviving images are then all scored and ordered from most likely to least likely matches. Out-of-the-box search engines use a TF\*IDF-based scoring algorithm which serve as a pretty reasonable starting point even for a face search application like this. With TF\*IDF scoring, less-common tokens, (such as Gargamel's `bulging-eyes`, `small-iris`, and `missing-teeth`) will carry larger weight. Intuitively this makes sense, `bulging-eyes` is more noteworthy than, say, `caucasian` or `black-hair`.

Besides the natural ability to filter and sort result sets, using a search engine comes with other benefits. If you use Elasticsearch then you can immediately take advantage of the ability to partition your index across several machines and scale to very large data sets. Consequentially, you can also distribute search across these machines for fast searchability. Additionally, since we're using a search engine, you can combine facial feature search with other types of search. For instance in addition to the `facial_feature` field above, you could have a `geo_location` field that carries latitude and longitude. Now you have location aware face search: "Find me all individuals matching Gargamel's description in Tennessee".

## Tokenizing Embedding Spaces

The above solution is of course silly, because we don't have an army of trained curators to tag face photos. However, if we could find some way to take a dense embedding vector and tokenize it into a sparse representation like that above, then we could have all of the benefits described above without the overhead of supporting that army of curators. 

What would such a tokenization look like? Well for one thing, it wouldn't be human readable; we wouldn't take a vector of floating numbers and convert it into words like `{fair-complexion, straight-hair, black-hair}`. Rather we would produce pure tokens - symbols that carried _some_ sort of descriptive information, (though we wouldn't necessarily know what that information means). So we would send Gargamel's image through some swanky machine learning algorithm to convert it into an embedded vector and then we would send that vector through our algorithm (still T.B.D.) and it would emit tokens: `{a52b3gd2, b1a3ff63, 69e4a3b3, ...}`. If we do this, then we get all the benefits outlined in the above paragraphs, and we can fire off our curation staff. The only thing we've lost is the human readability of the tokens.

But what algorithm is capable of mapping from embedding vectors to token space? Well, I don't rightly know. But I do know some of the qualities that it must exhibit to be successful:

* You have to have a [Zipfian distribution](https://en.wikipedia.org/wiki/Zipf%27s_law). Basically this is to say that
  * A small number of tokens must be present in a large portion of the documents - analogous to common characteristics like "caucasion" and "black-hair". These tokens help to partition the space into large chunks and filter out much of irrelevant documents.
  * A large number of tokens must be present in a small number of documents - analogous to highly specific words like "roman-nose" and "hazel-eyes". These tokens can be used to boost very similar matches toward the top of results.
* Each token must have only one meaning. You must avoid homonyms. For instance some token `ba44d91` should not simultaneously mean `red-hair`, `blond-hair`, and `black-eyes`. (English phrases like "sun dress" and "dress shoes" cause relevance engineers great frustration for this very reason!)
* A meaning must have only one token. You must avoid exact synonyms. It is wasteful if the tokens `9acc472`, `f856c13`, and `1399be3` all imply exactly `red-hair`.
* The tokens must cover the entirety of the embedded vector space. If a certain location in vector space does not have any corresponding tokens, then it is not searchable.
* Anything that is nearby in the embedding space must also be nearby (or more accurately ["similar"](https://en.wikipedia.org/wiki/Semantic_similarity)) in the token space. The token space must capture the topology, the clustering, and the relationships of the embedded vectors.
* Tokens must have some "fuzziness" in meaning, some semantic overlap. This is important so that retrieval will be robust to slightly different descriptions, (or disguises in the case of Gargamel above).


## Yeah, Yeah... But how do we do it?

How do we find an appropriate mapping between the embedding space and the token space?  This is a problem I leave to the reader - and a problem that I have not been able to solve myself! Here are some rough ideas that I have been working on, but I feel they all fall short:

* Perhaps we could use some sort of random projection approach where each embedded vector is projected against a random vector and if the result is a positive number then we emit a token. This would satisfy our nearness criteria above, but all the tokens would cover roughly the name number of documents, breaking our rule about Zipfian distribution.
* Maybe we can investigate some method for reversing existing factorization approaches which can be used to transform data from a large, sparse vector to a much lower dimensional dense vector. But the problem with the factorization approaches I have in mind now is that they are linear, and we would instantly lose important characteristics of the embedding space.
* Maybe the mapping could be generated from some fancy neural network. The output could be some very large softmax vector and the tokens would be indices of the top N outputs or something like that. But how on earth would you train this? The target is the very thing you're trying to find. It would have to be unsupervised.
* You could do some type of hierarchical clustering of the vectors in embedding space and for each vector emit a token for every level of the hierarchy in which it is included. But the strict hierarchy imposed on the token space breaks the "fuzziness" criteria (last bullet above) because the leaf tokens in this scheme would implicitly mean overly constrained things like "blond hair _and_ a Roman nose _and_ freckles". We would need a seperate token to describe "red hair _and_ a Roman nose _and_ freckles". Rather than such strict partitioning of token space, it would be better for tokens to carry semantics for individual attributes: "freckles", "red hair", and "roman nose", because no matter what color your hair is, "freckles" means the same thing.


## Standard Disclaimer

Per my usual, I did not do any exhaustive research prior to writing up this post. Perhaps this is an idea that has been well studied and perhaps my foundational presumptions are just wrong! If so, then would someone kindly point me in the right direction? On the other hand, maybe this is indeed something new. In that case I would love to get your ideas on how to push this idea further. In any case I'd love to get your thoughts. Let's start a conversation on Twitter - @JnBrymn.
