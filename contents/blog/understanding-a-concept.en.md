**We write in order to think better.**

None of us is a sage. It is precisely because any one person's ideas are full of holes that they are worth putting out for others to see. Having someone point out the flaw is exactly where the room to improve lives. An idea you keep hidden away can never grow up.

I like to think, and some thoughts, if I don't write them down in time, just slip away, which feels like a real waste. So I am starting a new series called "Stray Thoughts." The point is to straighten out my reasoning, keep a record of what I think, and make it easier both to reflect on my own and to trade ideas with others.

![figure 1](/static/assets/img/blog/understanding-a-concept/01.png)

*(right) Kandinsky, 1922*

In the last piece I introduced you to the methodology I have been calling **"structuralism,"** which looks at the nature of a thing through its relations and structure, and holds that the meaning of a word only shows up in context.

That might leave you with a certain impression: that **only structure matters, and the words themselves don't.** But in this piece, after the tearing down, I want to do some building up. I want to show you how a word can act as a **"node of meaning"** inside a semantic network, and what kind of wisdom ends up condensed inside it.

I really do recommend this one to friends still in school. When we study math and physics, and even the softer sciences like sociology and psychology, we are always running into **concepts and terms**: "number field," "element," "gravity," "public power," "representation," "the unconscious." Some are easy to grasp, others feel strange and obscure, but no matter the subject, understanding the concepts is always one of the most important parts of learning. What is a concept? Where does it come from? How do you learn one and actually understand it? And going a step further: if I were the theorist, how would I shape a concept from nothing, and how would I give it a name? This piece tries to answer those questions.

So in the first section, let's talk about a concept everyone already knows well: the **vector**.

---

The **vector** is familiar to everyone. It shows up in both high school math and physics. In the textbook, a vector (or a "directed quantity") is defined like this: a quantity that has both magnitude and direction. When I fly from Shanghai to New York, you can draw an arrow on the map, a line segment with a head, and call it a displacement vector. Pick any instant while I'm sprinting toward the finish line, and I have a speed pointed at the finish: that's a velocity vector.

Next to the messy, forbidding concepts at the frontier of math and physics, the vector is downright friendly. It isn't hard to understand.

But let me ask you something. The English name, **vector**, what does that word actually mean?

The question seems like a bit of a troll. Isn't a vector just a vector? We've already explained it, so what is there left to ask?

And yet. The first time I ran into the word "vector" was while teaching myself C++, and it showed up wearing a completely different costume: as an alternative to the array, the template class vector.

> The template class vector is similar to the string class in that it is a dynamic array. You can set the length of a vector object during runtime, append new data at the end, and insert new data in the middle. Basically, it is an alternative to using new to create an array. In fact, the vector class does use new and delete to manage memory, but this work is handled automatically...
>
> from *C++ Primer Plus (6th Edition), Chinese edition*, 4.10.1 The template class vector

Put simply, a vector is roughly an array. It can hold objects of different kinds: {1,2,3} is a vector, {{1},{1,2},{1,2,3}} is a vector, and {'a','b','c','d','e','f'} can be a vector too. It is a little more convenient to use than a plain array, with a few extra features, but nothing exotic.

By then school had already taught me about "vectors," but I had no idea their English name was "vector." So in my mental map, "vector" the Chinese term was a concept from math and physics, and "vector" the English word was a stand-in for the array, a "template class" in C++. **The two had nothing to do with each other. Each minded its own business in its own field.**

And really, why would they? One is a line segment with an arrow on it. The other is a clump of data. How could those be the same thing?

But somehow they were both called "vector."

Picture a student in an English-speaking country who takes a math class and then a programming class. They hear the same word both times, "vector," with no second Chinese term to split it in two.

At the time I thought it was the strangest thing. I went back and forth through the translation glossary at the back of my math books, checked every dictionary I could find, and there was no mistake: "vector" was the directed quantity, and "vector" really was both the array and the directed quantity.

So if I tell you right now that a vector and an array are in fact the exact same thing, would you find that odd?

And it isn't only the vector and the array. The vector is also the same thing as a polynomial, and it can be the same thing as a linear function too.

**How do we make sense of the vector and the array being isomorphic?** Start with a two dimensional vector (1,2) and a two element array {1,2}. Written that way, the equivalence is easy to see. But what about a more general array with lots of entries, say {'a','b','c','d','e','f'}? Here is the trick: a vector doesn't have to live in two or three dimensional space. It can sit in a much higher dimensional space too. When you look at a vector (1,2,3,4,5,6) in six dimensional space, does anything come to mind? Right. Map each letter to a number, and isn't that just {'a','b','c','d','e','f'}? And so the isomorphism between array and vector is built.

**What about the polynomial?** Take a three dimensional vector (1,2,3), and read the x axis, y axis, and z axis as the "1 axis," the "x axis," and the "x^2 axis." Now isn't that the same thing as x^2 + x + 1? Generalize, and every polynomial can be written as a vector of the appropriate dimension.

**And the linear function?** Suppose we have a vector a. Take any vector x, and define an operation: "the length of x projected onto the line through a, times the length of a itself." We have just built a function that "takes a vector x and returns a real number," and we can show it is linear, so it is a linear function, or a linear functional. The other direction works too: any linear functional must be isomorphic to some vector. (This is what's called "duality.")

What does all of this hint at? Combined with what I argued last time, it's easy to see that in a certain sense, "vector," "array," "polynomial," and even a certain class of "function" are just different names for the same thing, the same set of rules.

So if a rule applies to one of them, it applies to all the rest. We can compute the "angle" between two arrays, the "inner product" of two polynomials, and look at the "domain" and "range" of a vector. (Amusingly, the polynomial and the linear functional are two separate setups, so these function related concepts come in double.) In the two dimensional case, this whole pile is, in a sense, equivalent to a complex number (a + bi), and once you bring in Euler's formula, it is also isomorphic to the exponential function p\*e^(ix). Note that the operation rules don't always carry over untouched. Complex multiplication, the dot product, scalar multiplication, and matrix multiplication are not all the same operation. The point is only that the "rules," like the concepts themselves, can be carried over by some "isomorphism" to find their corresponding cousin.

Is there any point to thinking this way? I'd say yes: **noticing the isomorphism between these concepts can hand us fresh understanding and new angles of approach.**

Take a casual example. On a music app, we can use an array to record a user's listening history. Say I log, in order, "Cui Jian," "Teresa Teng," "Jay Chou," "Omnipotent Youth Society," "Akina Nakamori," "Bach," "Sonic Youth," "Taylor Swift," and so on. I end up with an array like {23,12,65,12,0,12,32,12...} (all randomly generated, no comment on my actual taste). Now, for two different users, we can compute the **"angle"** between their two arrays. The smaller the angle, the more alike their music taste. So if someone happens to have a tiny angle with you and loves an artist you have never heard of, putting that artist's album on your homepage as a recommendation might be a pretty good move. Just like that, we have invented a "recommendation algorithm" that actually sounds reasonable. So stop asking "how does the music app know me better than I know myself." The answer is: **go learn a little linear algebra, my friend.**

By now you might want to ask: "Can we set aside all these words that barely differ, and just study what they have in common, the deepest underlying so called 'rule' directly? Wouldn't that be much more convenient?"

Good news first: yes, you can. If you are at university, you will find a math department course called **"advanced linear algebra"** quietly waiting for you. Take it, and you will reach a chapter called "abstract linear spaces"...

Okay, that's enough math. I'll stop here. If you want to hear more, find me and we'll talk privately.

![figure 2](/static/assets/img/blog/understanding-a-concept/02.jpg)

*Mondrian, 1917*

---

You might have come expecting a culture post with a sprinkle of light philosophy, and instead caught a faceful of math in that last section, which probably felt abrupt. Honestly I didn't want it this way either (wry smile), but the "vector" example is just too perfect, too interesting, and too useful. Not spreading it out a bit would have felt like a waste.

**But can we really just swap the name?** True, a word is a symbol, and its link to its meaning is arbitrary and random. But can we actually replace it as lightly as "using an eraser in place of a chess piece"?

The answer up front: **no.** Let me explain.

Let me first lay out two kinds of linguistic rules, which I'll call **"the common sense rules of natural language"** and **"the logical rules of mathematical language."** The first rests on our past experience and intuition: we see a gently trickling stream and think of calm and gentleness, we see a roaring fire and think of passion and ideals. The second rests on rational definitions and logical deduction among concepts: velocity is an object's displacement per unit time, temperature is how violently molecules move. **The first is sensory, changeable, and personal. The second is rational, stable, and able to support a long chain of reasoning.**

With those two roughly sorted out, let's think through this question together: "What does it mean to 'feel' something (what I call 'understandability')? If we want to 'feel' it, what role do 'the common sense rules of natural language' and 'the logical rules of mathematical language' play?"

The answer straight away: **only the 'common sense rules' can be felt; the 'logical rules' cannot.** To "feel" something, to have it "right there before your eyes, vivid and graspable, understood in your gut," is in fact tightly bound to our common sense. We can only, must, are forced to, understand things through common sense and experience. We have seen flowing water, fire, green grass, darting swallows, but we have never seen "a vector," "an electric current," "energy." So the former can be felt, and the latter resists being felt.

I don't think you'll be satisfied with that last conclusion. You might push back: "That's not right. When I was learning math and physics and grinding through enough problems, I did develop a kind of 'intuition.' I can try to feel vectors and currents too, or how else would I solve the problems?"

**Abstract concepts can indeed be felt, but that feeling is always achieved through a metaphor drawn from the 'common sense rules.'** Take the vector again. In Chinese we can crudely split the word into "xiang" (direction) and "liang" (quantity). "Xiang" supplies the intuition of "direction," "liang" supplies the intuition of "how much," and both direction and quantity are things every one of us experiences in daily life. That is what gives the vector its "understandability," along with the "line segment with an arrow," which is also something we can experience. But as I said above, a "vector" can also be an "array," can also be a "polynomial," and these are completely identical (isomorphic) under "the logical rules of mathematical language." That move, though, makes the "common sense rules" collapse entirely. We cannot naturally transfer the intuition for a "vector" onto a "polynomial," or onto an "array." In fact, just like the vector, the array and the polynomial each offer their own set of intuitions. **Mathematical concepts may all connect, but the intuitions for understanding them differ wildly.**

I call this phenomenon a "cognitive prototype." **Cognitive prototypes are rooted in the human unconscious. They are the basic form of human thought, the foundation of the machinery of "understanding" and "feeling," and they are cultivated out of life and experience.** To make this easier to follow, I'm going to quote at length from Professor Chen Jiaying's *Philosophy, Science, Common Sense*, because my own pen isn't up to writing it more clearly than he did. Bear with me.

> ...Under the rule of holistic intellectual cognition, responsive cognition is suppressed into a kind of lower layer cognition. The real vitality of responsive cognition lies in how it supplies all sorts of **cognitive prototypes**, prototypes that still regulate our cognition at a deep level and from which our intellectual understanding keeps drawing nourishment. As I said earlier, sunrise and the flourishing of life, sunset and decline, the earth and the mother: these connections are so natural that it is almost impossible not to begin understanding the world from them. They are "the oldest and most universal forms of human thought. They are at once feeling and thought." It is in this sense that Jung called them cognitive prototypes. Cognitive prototypes still play an important role in art, and likewise they still play an important role in philosophical understanding, and even in scientific theory. Research on symbols, metaphors, and so on keeps revealing this. The many metaphors about society, the organism, the strata, the web, the fabric, the machine, are openly adopted by the social sciences. The mathematization of modern physics can be seen as an effort to eliminate metaphor. Yet even some of the basic notions in physics still depend on cognitive prototypes of the metaphorical kind. The word "current," or electric current, is metaphorical: the description of current carries the force the word "flow" has in images like flowing water. Current is not a single word that happens to carry a metaphor; what appears here is a whole family of metaphors. Current passes through a conductor of low resistance, and current, passes, and conductor all carry metaphor, together forming one unified picture. The notion of energy and its conservation is probably also grounded in a cognitive prototype; in an earlier age it was the alchemist's secret fire, or Heraclitus's "everliving fire." The idea of energy conservation is a kind of primordial image lurking in the collective unconscious, an idea that also shows up in magic, in the immortality of the soul, and so on. This is not some strange fancy of the psychoanalysts. One famous history of science comments on the conservation of matter and energy like this: **"For the sake of convenience, the mind, without realizing it, always picks out those quantities that are conserved and builds its models around them."**
>
> In the chapter on scientific concepts we will discuss how scientific theory works to eliminate these metaphors, hoping to turn every term into what Harré calls a "fully defined" concept. Yet we have reason to think this is a goal that can never be fully reached. As Harré puts it: "I will go so far as to assert that no physicist, however hawkish, means anything more by 'heat flow in a conductor' than 'the change of temperature over time.'" Harré dares to make this assertion because "words like [current] cannot be replaced by artificially constructed expressions without destroying the conceptual foundation of electrodynamics."
>
> (*Philosophy, Science, Common Sense*, Chen Jiaying)

**So even if the link between a word and a thing is arbitrary and random (structuralism), the word itself is already fused deeply with a cognitive prototype.** Which, when you think about it, is fairly obvious. We cannot use language to describe what lies outside language, cannot experience experiences outside of life. So this tangled "word and cognitive prototype" relationship is inevitable.

Faced with the common sense concepts of the real world, we have plenty of give. Nobody needs to explain to me what flowing water is, or what an apple is; I already know. But faced with mathematized concepts, we make a despairing discovery: getting a feel that is both fully accurate and vividly graspable is impossible. We might be able to picture analytic geometry in our heads, imagine a function's graph sliding and flipping, try to handle propositions and logic in natural language, **but that imagination lacks a quantified dimension, and as complexity rises it is bound to go off target.** Which, oddly, is exactly where the strength and the point of "mathematization" show up: long chains of reasoning become possible because of mathematics, and so humans can finally extend reason into places common sense never reaches, and see into the nature of the unintelligible.

Which finally lets us pose this strange question: **how do we understand the thing that can't be understood?**

![figure 3](/static/assets/img/blog/understanding-a-concept/03.jpg)

*The Cathedral of the Minorities, Lyonel Feininger*

---

To understand the unintelligible is both simple and hard. Simple, because **all we have to do is give it a name.** By the structuralist method, the naming should be arbitrary. It's like learning math: you meet a number, you don't know what exactly it is, or maybe it is flat out undetermined, but as long as you recognize that it is some thing, you can name it X and use X to refer to it. As long as the context and the shared agreement are in place, everyone can work with it just fine. In linguistics the thing being referred to is the "signified," and the X we use is the "signifier." Real world snow is the signified; the symbol "snow" that comes out of my mouth or goes down on paper is the signifier. So there's a classic line in the philosophy of language: **"Snow is white" is true if and only if snow is white.** Rather fun.

But after all the above, we realize that finding a fitting signifier for a concept is not so easy. If the signified has no understandability of its own, then the signifier we pick (the word) has to supply some understandability instead. So although structuralism tells us we may pick any signifier, in practice we cannot.

From what I've observed, concept shaping (here I mean specifically the act of finding a fitting signifier for a concept) falls roughly into two kinds: **domesticating** and **foreignizing.**

**Domestication** and **foreignization** are two terms borrowed from translation theory. Domesticating translation pulls the source text toward the conventions of the target language, while foreignizing translation stays faithful to the source language's conventions. "Oh my god!" domesticated into Chinese becomes "wo le ge qu!", and foreignized becomes "my Lord!" These two terms are easy enough to grasp.

So we can carry the same distinction over to "concept shaping" and read it as "domesticating shaping" and "foreignizing shaping."

**Domesticating shaping picks a signifier as close to the cognitive prototype as possible.** Good examples are the words used to describe society: "class," "exploitation," "machine." They show the concept's meaning intuitively and carry very strong understandability. In a politics class, the first time you hear something like "the state machine," you immediately get the rough idea. That understanding may not be perfectly accurate, but it is close enough and leaves little room for misreading.

**Foreignizing shaping coins a brand new word as the signifier.** Good examples are over half the periodic table, those obscure characters for scandium, titanium, vanadium, cadmium, manganese, or "enthalpy" and "entropy" in thermodynamics. These concepts are exact and precise, fully avoiding the misunderstandings that common sense and cognitive prototypes can cause, but at the same time they lose all understandability. The first time any student hears "enthalpy," they have no idea what it is. The concept becomes graspable only through its definition and its links to the other concepts in the field.

So domesticating and foreignizing each have their pros and cons. Domestication is easy to understand, but very often the real world metaphor and the theory don't quite mesh, and the best example is probably the "vector" we mentioned earlier: plenty of things that don't feel at all like vectors are still vectors, which makes them hard to understand. Foreignization's trade off is plain. The upside is extreme precision, never any misreading; the downside is that it is completely unintelligible, so it degenerates into pure "jargon" and "terminology" and offers not a shred of intuition.

There's also a gray zone in the disciplines. "Dot product" and "cross product" are a bit subtle, because they do have a piece grounded in everyday life: the symbols written on paper are literally a dot (a · b) and a cross (a x b), yet at the same time they have nothing to do with real life, which is a strange mix. So domestication and foreignization aren't a strict binary at war with each other; there's some murky, ambiguous middle ground. And it's funny: the two concepts "domesticating shaping" and "foreignizing shaping" are themselves a piece of "domesticating shaping" I performed in this text to keep the writing clear, a "working hypothesis" for the sake of getting the point across. So don't get too hung up on the exact definitions or boundaries of these two words.

So sometimes, while studying, I used to be baffled: **why are so many concepts in math and physics this hard to understand? I have no idea what they're even talking about.** Now I've figured it out. It comes down to concept shaping. Good concept shaping brings about good understanding; bad concept shaping leaves people unable to understand. Below I'll pull out a few examples of concept shaping, as a starting point for discussion.

**scalar**

A scalar is the counterpart to a vector: a scalar has no direction, only magnitude. In Chinese, the character "biao" carries an intuition close to the "scale markings" on a thermometer, giving the sense of "magnitude without direction." But scalar offers a different understanding. Scalar calls scale to mind, and scale in English means not just "size" (the "magnitude without direction" intuition) but also "to resize by a ratio." Scaling, for instance, means resizing. In linear algebra, the main use of a scalar (I'll skip things like number fields) is "scalar multiplication," and its geometric intuition is precisely "resizing a vector." Calling a number a scalar carries a very strong intuitive meaning, and in Chinese that delicate layer of metaphor is lost completely.

**function, mapping, transformation, operator**

I still remember the first time I learned about functions in high school. The teacher said, "A function is a mapping." I was struck with awe, as if I had suddenly grasped some great truth about the essence of functions. Later I realized that "epiphany" had a problem, because saying a "function" is a "mapping" is like explaining a sleeping pill's effect by saying it has a "sleep inducing property." It is pure tautology, and under "the logical rules of mathematical language" it doesn't mean much. Still, "function" and "mapping" do offer different intuitions. "Function" (the Chinese "hanshu") leans toward foreignizing shaping; I honestly don't know what the "han" means. "Mapping" is far better: it gives a sense of "image," forming a metaphor with the light and shadow we see in daily life, where the warping and distortion of shadows is an analogy for the change from input to output. "Mapping" and "transformation" also differ slightly, since a function's output is generally a number (its codomain is a number field) while a mapping's output is generally treated as a vector, though this difference doesn't matter much. "Mapping" and "transformation" mean roughly the same thing, carrying similar intuitions and metaphors. The intuitive difference between the two words is this: "mapping" has a feel of going from region A to region B, while in "transformation" the before and after basically sit in the same place. That difference reflects a real difference in the concepts. A mapping's domain (and of course the Chinese and English for "domain" carry different intuitions too) and its codomain (a concept that, oddly, has no especially good Chinese translation, which has caused enormous confusion and difficulty) are generally not the same, or at least not assumed to be. A transformation's domain and codomain are assumed to be the same. "Transformation" also has a foreignized version called "operator," but I won't go into that here.

**image**

"Image" is a strange one to translate. Rendering it as the Chinese "xiang" feels like a last resort, since Chinese doesn't seem to have a really fitting word: "xiang" means "similar," "portrait," "for example," while in English "image" is rich in meaning, roughly "a picture or notion in the mind," "the reputation of a person or company," and "a picture or visual." In math, "image" is often used interchangeably with "range," both meaning the set of all possible outputs. Where does that intuition come from? It is built jointly with the "mapping" mentioned above, into one metaphor. The "image" produced by "mapping" is the range, easy to follow. Switch to English and the understanding actually gets stranger, because "mapping" translates "map," and map and image don't share this set of metaphors the way the Chinese words do, which is why people abroad really do lean toward "range" for the range.

After those few examples, did you notice something? **Concept shaping is intensely language dependent.** Because social environments differ, the ways of life and the common sense grasp of the world differ across cultures, which produces different habits of language use, which in turn shapes both how concepts get named and how they get grasped. And a step further: across eras, even across individual authors, concept shaping varies. Two textbooks in the same subject, by different authors, may use different words to refer to a concept, and so carry different intuitions.

So how should we understand a concept? My view is that "intuition" and "precision" should be two sides that support each other. Intuition aids understanding; precision keeps you from going wrong. Always chase good intuition, always stay faithful to the precise definition, and that way you can slowly arrive at so called "real understanding" and handle the concept with ease.

**What is the essence behind "concept shaping"?** The choice of a word already contains the author's understanding, and that understanding travels with the word to the reader. This is the wisdom condensed inside a word. A word naturally carries understanding, and "learning," to put it plainly, is the process of mastering words and their meanings, and learning the methods and tricks an author uses to wield them. Always look for the good concept, and through it gain good understanding. That is the way of learning.

![figure 4](/static/assets/img/blog/understanding-a-concept/04.jpg)

*Kandinsky, 1913*

I'm Ningningning Jinghai. Thank you for reading to the end.

Writing and layout: Jinghai

Cover design: Zui Qingcheng

References:

Books:

*Science, Philosophy, Common Sense* by Chen Jiaying

*Invisible Cities* by Italo Calvino

*C++ Primer Plus (6th Edition), Chinese edition* by Stephen Prata

*Linear Algebra Done Right (Third Edition)* by Sheldon Axler

Web:

[Essence of Linear Algebra (official bilingual series) by 3Blue1Brown](https://www.bilibili.com/video/BV1ys411472E)

[[BetterExplained] Why you should start blogging now, by Liu Weipeng](http://mindhacks.cn/2009/02/15/why-you-should-start-blogging-now/)

Lectures:

*The Shaping of Concepts and the Symmetry of Mathematical Mechanics* by Professor Yin Yajun
