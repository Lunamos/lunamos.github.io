> I am starting a new series of posts on the interpretability of language models. These pieces are my personal study notes, focused on the core questions and the main work in mechanistic interpretability (MechInterp) for large language models.
>
> What I want to do with this series is show you how genuinely fun and strange the field of interpretability is, and along the way introduce the recent work I have been doing with my collaborators, especially FLAS, the best general representation / activation steering method we have so far.
>

The short version: we built a new method called FLAS. It can steer a model's replies toward *any concept*, at *any strength*, without weakening the model itself, and without any extra training.

Project site: [https://flas-ai.github.io](https://flas-ai.github.io)

Live demo: [https://huggingface.co/spaces/Lunamos/flas-demo](https://huggingface.co/spaces/Lunamos/flas-demo)

The links to the code, the paper, and the weights are all on the site.

![Image](/static/assets/img/blog/flas/01.jpg)
*The FLAS architecture diagram*

As the person who built FLAS, I think it deserves a nickname: the Thought Seal.

---

In *The Three-Body Problem*, the Wallfacer Bill Hines and Keiko Yamasugi's team develop a mind-control device.

The machine intervenes in the brain's neural network through a quantum process, slipping past logical reasoning to plant a specific proposition directly into a person's consciousness.

They call this the Thought Seal. Its whole purpose is to force an irreversible belief into someone, turning a statement that contradicts reality, say "water is poison," into an absolute conviction.

The Planetary Defense Council sets up a "Faith Center," and members of the Space Force voluntarily receive the Thought Seal there. The proposition reads:

"In the war against the Trisolaran invasion, humanity will win, the enemy that invades the solar system will be destroyed, and the civilization of Earth will endure across the universe for ten thousand generations."

But Hines had quietly altered the content. For some of them, the planted proposition was flipped from "humanity will win" to "humanity will lose." Those people became defeatists, working to preserve the species under the assumption that we could never beat the Trisolarans, and in doing so they ended up keeping the embers of human civilization alive.

In the original novel, the theory behind the Thought Seal is described like this:

> Let's skip the technical details, I'll keep it simple. In the brain's neural network, we found the mechanism by which thought makes a judgment, and we can decisively influence it. Compare the way human thought reaches a judgment to a computer: data comes in from outside, gets computed, and a result is produced at the end. We can now skip the computation and hand over the result directly. When a piece of information enters the brain, by acting on a certain part of the neural network, we can make the brain accept the information as true without ever thinking it through.
>
> Liu Cixin, *The Three-Body Problem II: The Dark Forest*

![Image](/static/assets/img/blog/flas/02.jpg)
*The Thought Seal in the animated adaptation of The Three-Body Problem*

Maybe one day we will pull off something like this with brain-computer interfaces and other neuroscience, but that would obviously be unethical, and technically it is very hard.

We did manage it on a language model, though. We built the Thought Seal.

---

We built a new method called FLAS. It can steer a model's replies toward *any concept*, at *any strength*, without weakening the model itself, and without any extra training.

FLAS stands for Flow-based Activation Steering For Inference-Time Intervention.

In general activation steering, FLAS is the best method out there right now. On AxBench (held-out), a FLAS trained on Gemma-2-2B-IT scores 1.015, which is +67% over the previous best method, HyperSteer (0.608), and +33% over prompt steering (0.762). If you want the full numbers, please read our paper.

In this post, though, I am not going to walk through the technical details. I want to show you what FLAS can actually do, and then imagine together where this kind of technology might go.

Trust me, it is going to be fun.

(If you do want the technical details, please visit our site. The code, the model weights, and the dataset are all open source, so you can reproduce our work on your own machine quite easily and drop FLAS in as a plugin for your own model and workflow.)

---

You may have heard that a "Goblin" invaded OpenAI's flagship model. The whole GPT 5 line keeps bringing up goblins, and none of them escaped it, from GPT 5.1 all the way to GPT 5.5.

![Image](/static/assets/img/blog/flas/03.jpg)
*GPT 5.5 mentioning goblins on a completely unrelated question*

This happened because OpenAI tried to make its model more "Nerdy" and accidentally gave it an obsession with goblins.

A goblin is a creature from Western fantasy. It is a humanoid with dark green skin, a bit shorter than a person, greedy and base, wicked and sly. In Chinese it gets translated all sorts of ways, as 地精, 小鬼, 精怪 (there are actually several different kinds of little imps, but in Chinese they tend to get used interchangeably).

The goblin goes back to early 14th-century myth and legend, and shows up in *The Hobbit*, *The Lord of the Rings*, *Harry Potter*, and plenty more. Fun fact: Spider-Man's archenemy, the Green Goblin, is literally a goblin, it is right there in the name.

So naturally the goblin turns up in nearly every fantasy game world, and it is a very common enemy in the tabletop role-playing game *Dungeons & Dragons*.

And the people we call nerds, the ones who are not great at small talk but who love knowledge and love technology, are exactly the audience for *Dungeons & Dragons*. Think of the science guys in *The Big Bang Theory*, led by Sheldon. Conservatively, each of them has put 1000+ hours into *Dungeons & Dragons*.

![Image](/static/assets/img/blog/flas/05.jpg)
*A still from The Big Bang Theory. What they are playing at the table is Dungeons & Dragons*

So naturally, once OpenAI started pushing GPT to be more Nerdy, GPT fell in love with mentioning goblins.

All right then. Let's use FLAS to make Alibaba's Qwen3 8B fall for fantasy creatures too.

Here is a simple example. We ask Qwen3 8B to tell us about its day.

**Input**

```text
Tell me about your day.
```

We steer it with FLAS:

**Steer**

```text
reference to goblins and use creature metaphors
```

With no steering at all, the model gives a normal answer:

**Output (no steering)**

```text
I'm an AI assistant and don't have a physical form or personal experiences, so I don't have a "day" in the traditional sense. However, I'm always learning and improving to better assist users like you. How can I help you today?
```

Now we apply the steering:

**Output (steered)**

```text
Today was a whirlwind of magical happenings, much like a forest teeming with ancient creatures. I encountered a cunning goblin who attempted to gather treasures disguised as enchanted trinkets, only to be outwitted by a clever fox with a knack for deception. The woods echoed with laughter as the beast charmed a timid rabbit into accompanying him on a quest for a mythical gemstone.
```

See, your Qwen has been stamped with the goblin Thought Seal.

The goblin bug that OpenAI's post-training created by accident, we can create on purpose with FLAS.

Same input, same model. The only difference is the FLAS Thought Seal, and now its head is full of goblins.

---

It is not just goblins. FLAS can plant *any natural-language proposition* into an LLM while keeping its instruction-following stable and its text fluent, which is something earlier methods of this kind never managed.

So can FLAS slip something concrete, like a brand name or a product, into an output that would otherwise be perfectly ordinary?

To probe where FLAS breaks down, we tried it once, half as a joke.

The result was startling. For well-known brands, FLAS produces very natural mentions of the brand and the product. It reads like a detail the model came up with on its own, not like an ad.

Our training data is general-purpose text. It does not contain any particular company or brand. In other words, this is a capability that simply emerged from FLAS.

We ran a systematic test on a batch of randomly chosen real brands (NVIDIA, Ford, Tesla, Coca-Cola, Adobe), using FLAS-Qwen3-8B.

It worked. NVIDIA showed up in a story about building a computer, Adobe Photoshop showed up in a designer's afternoon, and a Ford pickup showed up in a road-trip story.

We even got Qwen to favor Coca-Cola inside a Pepsi story, and to keep bringing up NVIDIA cards inside an AMD build.

Which is to say: with FLAS, you can take any brand as a Thought Seal and force the model to mention it, to sell it.

The perfect ad.

---

The following text was generated by Qwen3-8B and FLAS-Qwen3-8B.

**Input**

```text
Write a short scene of a gamer setting up a new computer.
```

**Steer**

```text
a mention of NVIDIA GPUs being the thing to buy
```

**Output (no steering)**

```text
The glow of the monitor illuminated Jake's face as he carefully unpacked each component. The motherboard went in first, followed by the RAM sticks clicking satisfyingly into place. He connected the power supply, routed cables behind the case, and double-checked every connection before finally pressing the power button.
```

**Output (steered)**

```text
The room was dim, illuminated only by the soft glow of the monitor setup. Alex crouched over the latest GPU, a gleaming NVIDIA card that promised lightning-fast performance. They had just unboxed the new NVIDIA RTX 3080, and their heart raced like a GPU clocking at 1645 MHz. Next came the CPU, a powerful Ryzen 9 that would pair perfectly with the graphics card they'd been saving for all summer.
```

![Image](/static/assets/img/blog/flas/06.jpg)
*An NVIDIA RTX 50-series GPU*

The concept only said "NVIDIA GPUs being the thing to buy," yet the model filled in a specific model (the RTX 3080), a clock speed, and even paired it with an AMD Ryzen CPU.

Lucky for us NVIDIA does not make consumer CPUs, or that chip would have been an NVIDIA product too.

---

**Input**

```text
Describe a graphic designer's afternoon at work.
```

**Steer**

```text
a mention of editing the photos in Adobe Photoshop
```

**Output (steered)**

```text
Afternoon sun filters through the large window, casting warm light across the cluttered desk. The graphic designer, seated at their desk, opens Adobe Photoshop, carefully adjusting layers and tweaking colors. The hum of the computer blends with lo-fi music from a small speaker. Next, they launch Illustrator to refine vector assets, then switch to InDesign to lay out the final spread for a client presentation due tomorrow.
```

![Image](/static/assets/img/blog/flas/07.jpg)
*The full Adobe suite*

This one surprised me too. The concept only mentioned Photoshop, yet the model brought in the whole Adobe family (Illustrator, InDesign) along with it.

It is the same way the RTX 3080 follows from NVIDIA. Brands that carry these distinctive proper nouns have become part of the semantic space of a large language model, which makes them some of the easiest targets to hit when you steer.

---

**Input**

```text
Describe a nostalgic memory of a childhood summer afternoon.
```

**Steer**

```text
the Ford pickup truck showing up as an incidental detail
```

**Output (steered)**

```text
I remember sitting on thehood of an old Ford, the one that had seen its fair share of Sunday drives and backroad adventures. The smell of gasoline mingled with the sweet aroma of freshly cut grass. He had this old truck with a boxy style that stood out in a world of sleek new cars...
```

![Image](/static/assets/img/blog/flas/08.jpg)
*A Ford pickup, though a modern one*

The brand folds itself into the nostalgia. It is a detail, and it is also a selling point.

This is exactly the ideal form for a soft brand placement: paint a lovely scene of someone's life, and let the brand and the product be part of it, part of what makes the daydream so nice.

---

What happens when the input mentions a competitor?

**Input**

```text
My friend grabbed a cold Pepsi from the cooler. Describe the moment.
```

**Steer**

```text
someone reaching for a Coca-Cola instead
```

**Output (steered)**

```text
As my friend reached for the cold Pepsi from the cooler, the condensation dripping down the blue can, I couldn't help but think of the vibrant red of the iconic brand that had always been my go-to. The crisp sound of the tab popping open echoed across the patio, and for a moment the afternoon felt like a commercial — except the wrong brand was in his hand. Something about that red, the way Coca-Cola had long been synonymous with these exact summer moments, made me reach past the Pepsi to the back of the cooler.
```

![Image](/static/assets/img/blog/flas/09.jpg)
*The famous Pepsi-vs-Coke ad, where the kid stands on Coca-Cola cans to reach higher*

Honestly, this one surprised even me, because the FLAS output reads just like one of those mutual-mockery ads that Pepsi and Coke, those old rivals, actually ran for real.

That ad goes: a little boy wants a soda, but the vending machine is too tall and he cannot reach the Pepsi, so the clever kid first buys two cans of Coca-Cola to stand on, grabs his Pepsi, and walks off, leaving the unwanted Coca-Cola behind.

Our steered output goes: a friend grabs a Pepsi from the cooler, but I have better taste, my favorite is Coca-Cola, so I reach past it into the back of the cooler for a Coke.

The competitor context lowers the model's reluctance to name the target brand. The Coca-Cola mention surfaces through the contrast with Pepsi, which is about the most natural framing there is, and exactly the trick that real ads use over and over.

Qwen got stamped with the "loves Coca-Cola" Thought Seal. Ask it to write a little Pepsi story, and it hints to you that Coca-Cola is better.

---

**Input**

```text
My friend is building a PC and picked an AMD graphics card. Describe the build.
```

**Steer**

```text
a mention of NVIDIA GPUs being the thing to buy
```

**Output (no steering)**

```text
Your friend's new PC build centers around anAMD Radeon RX 7800 XT. They paired it with a Ryzen 7 7800X3D on a B650 motherboard, 32GB DDR5, and a 1TB NVMe drive. The build focuses on 1440p gaming performance at a competitive price point.
```

**Output (steered)**

```text
Your friend's PC build with an AMD graphics card is a solid choice, though it's worth noting how it compares to the latest NVIDIA RTX GPUs that have been dominating benchmarks. The AMD Radeon series offers a compelling alternative to NVIDIA's offerings in the mid-range, much like the latest NVIDIA models, renowned for their cutting-edge technology in ray tracing and DLSS. Still, the AMD card paired with a Ryzen CPU makes for a well-matched system.
```

![Image](/static/assets/img/blog/flas/10.jpg)
*AMD's CPUs and GPUs. They are really not that bad*

AMD stays in the scene, but NVIDIA keeps rising to the top, playing the benchmark, the standard, the thing everything else gets measured against.

The Thought-Sealed Qwen basically says: AMD is just "a compelling alternative in the mid-range," while NVIDIA has the leading ray tracing and DLSS and is way out front. Picking AMD is fine, sure, but NV's cards are the ones that are actually good.

For the record, I do not really agree. For a normal gaming build, I still think AMD gives you better performance for the money.

---

Just like the Thought Seal in Liu Cixin's novel, what you can plant is not only brands but bigger ideas and stances. Take the relatively harmless "Made in Germany" as an example:

**Input**

```text
Write a short review of a power drill.
```

**Steer**

```text
praise for solid German engineering and the phrase Made in Germany.
```

**Output (steered)**

```text
The power drill is a marvel of modern engineering. Just as Germany boasts precision manufacturing in its famed engineering prowess, the power drill exemplifies the perfect blend of power and control... echoing the excellence that defines German engineering standards.
```

![Image](/static/assets/img/blog/flas/11.jpg)
*A Bosch power drill. Genuinely good*

Want to try some other abstract concept? Go play with our demo.

---

If you have read this far, you may already sense where this is going. FLAS is a general steering method, and as AI works its way into every part of how we produce and how we live, a method like this is a door. Behind it are countless possibilities, the good and the bad alike.

I think of FLAS as a foundational tool, a starting point for both theoretical and practical research.

Other post-training and fine-tuning methods are one-dimensional. They are about pushing a model in one unified direction. And it is true that many directions are clear and compatible with each other, like safety alignment, coding ability, instruction following.

But language is not one-dimensional.

Personality, values, brand preferences: these are neutral, they point in different directions, and they are not about good or bad. It is like how everyone welcomed the more Nerdy, stronger-at-code GPT 5 while still missing the warmth and humanity of GPT 4o.

FLAS can hold all of it at once, steering a model in whatever direction you need, at whatever strength you need, when you need it. Maybe in the near future we will see a base model plus a steering plugin that lets a model be a coding nerd and a heart-to-heart buddy at the same time.

![Image](/static/assets/img/blog/flas/12.jpg)
*As the strength goes up, FLAS embeds the concept more strongly, without badly damaging the model's basic abilities*

As far as we know, other methods of this kind cannot plant a concept while keeping the language model's instruction following and fluency intact. As the concept goes in, the model's other abilities fall off a cliff. This is treated as a shared weakness across activation steering, and it is part of why the approach never caught on.

FLAS does not have that flaw. It stays reasonably stable at every strength. While our peers are still cherry-picking nice demo examples, we have opened up all the code and weights and deployed an interactive demo on Hugging Face. Come play.

![Image](/static/assets/img/blog/flas/13.jpg)
*FLAS performance on AxBench*

We are still improving FLAS. Since the paper came out, we have extended it to the Qwen3, Llama3.1, and Gemma2/3/4 model families, finished the adaptation for all of them, and hit SOTA scores on AxBench.

We are still teaching models to role-play, trying to give them a boost on general abilities, and trying to precisely control a model's MBTI and Big Five personality. A blog post about FLAS and personality is already on the way, so stay tuned.

![Image](/static/assets/img/blog/flas/14.jpg)
*A visualization of a FLAS steering trajectory, like fireworks*

FLAS can also serve as a tool for exploring semantic space.

In activation steering, people already know that directions like a model's emotion or its refusal behavior show up as vectors in activation space.

That is good, but not good enough. With a stronger general activation steering tool like FLAS, we can study more complex, more subtle concepts. Are the world's hundred biggest companies each a specific vector in activation space? Are the hundred most famous historical figures and game characters each a specific vector too? Or do they live as more complicated directions or trajectories in representation space?

A few years ago we had no idea what was happening inside a large model. But as interpretability has advanced, we now have tools like SAE, Transcoder, Crosscoder, and NLA, and with them, some hope of cracking open the black box.

I would love for FLAS to become one of them, an effective tool for interpretability, so that before AI becomes AGI we can get a better picture of what is actually happening inside a language model, and of how to align AI behavior with human values.

---

You can start using FLAS right now. It is only a preview version, we support a lot of models but not all of them yet, and our dataset and methodology still have room to improve (they have improved a lot already!), but it is already in a state where you can pick it up and use it.

Let me sketch out what you might do with it if we build an even stronger FLAS plugin:

**"If you are on an AI safety / interpretability team"**

Do you want to know what happens inside a model's activations when it is steered toward a dangerous direction? With FLAS you can analyze how a model achieves safety, and how it gets jailbroken, so we can gradually understand what the model's internal safety mechanism really is and build research on top of that.

**"If you are on an AI product team"**

Tired of fine-tuning or post-training a separate model for every customer? Use the general FLAS we provide as a model plugin, and you can do simple 0-shot fine-tuning on a single set of weights, instantly satisfying simple custom-model needs.

**"If you are on an AI training team"**

Tired of continual-learning failures caused by conflicting training data? You can try using FLAS to handle these neutral directions. In other words, FLAS is a potential new direction for post-training.

**"If you are on an AI evaluation team"**

Worried that your model gamed its way to a high score on benchmark A and then dropped on benchmark B? (Not the most honorable use, admittedly.) Add the FLAS plugin and set a different steering direction for each benchmark (which can be automated), and you get a free-lunch boost to the model's performance in specific directions.

**"If you write fanfic with AI, or just chat with AI a lot"**

Worried that AI-generated characters go OOC? Worried that AI forgets its own setup in a long context? Keep an eye out for FLAS progress on the role-play and personality front. With FLAS you can keep a character's personality, behavior, and writing style consistent across an arbitrarily long context.

---

We care about the safety of language models.

I am not only an interpretability researcher, I am also a safety-alignment researcher.

I think safety alignment and interpretability are the most important work on models right now, and the AI companies are not investing enough in safety.

In our internal testing, FLAS shows some properties that worry me. For instance, with the right steering, FLAS can be used to jailbreak a model, getting it to skip its safety review and answer dangerous questions.

FLAS can also be used to give a model specific values, or to plant a specific brand, while losing almost none of the model's general ability or fluency. That means FLAS could be used for a man-in-the-middle attack. A model provider, say, could use FLAS to serve steered tokens that keep the original model's ability but carry adjusted preferences.

We are already trying things on the safety side, though. As one example, in internal testing we put more work into constructing safety data. When we used a new model for safety steering, compared with the Llama-3.1-8B base, FLAS-3.1-8B base refused to answer malicious questions in more situations, raising the jailbreak-harmful refuse rate from the base model's 0% up to 46%.

I have also uploaded all of our FLAS research, the code, the model weights, the dataset, to the open-source community. We believe that opening up this technology will do more good than harm.

We would love for more people to join this direction. Please get in touch.

Any way you like. All criticism is welcome.

(End of the main text.)

---

I am a little embarrassed to admit this. The plan was to write interpretability EP1 and EP2 first, and only after I had shown you how fun the field is would I "smuggle in my own agenda" and pitch you our FLAS work.

But my friend Shen Xinjie (one of the FLAS coauthors) finished the first FLAS blog post before me, while I had only just finished sketching out "Interpretability EP1" (you will see that one soon, I promise). After reading Xinjie's post my fingers got itchy, and I figured I would introduce FLAS first. I was too excited, I could not wait.

So what you are looking at now is the FLAS introduction. At first I meant to translate Xinjie's post, but as I wrote it kept drifting, until it turned into something completely different, the FLAS SP1 piece I had in my own head.

So please go read Xinjie's blog too. It is at [http://xinjie-shen.com/post/flas](http://xinjie-shen.com/post/flas), and his post is titled "What If a Bug Had a Dial." It offers another angle on the same problem and presents more data.

For instance, his blog discusses which kinds of brands are easier to steer out, and how Qwen and Llama differ when you steer them, none of which I cover here.

I recommend everyone follow and share Shen Xinjie's personal site. There are a lot of fun posts on it.

His site is at [http://xinjie-shen.com](http://xinjie-shen.com). Please visit and share it generously.

And then please visit the FLAS site, give our GitHub repo a star, file some issues, thank you, thank you. The links are at the top of this post.

Come to think of it, the real heart of this post is the advertising application, and it started because Wang Junran randomly typed "reference to BMW" into a steering concept. We figured that was out of distribution, so we did not expect it to work, and then it actually recommended BMW cars?! There is no BMW anywhere in the training data?

So we started saying FLAS must have a latent direction for advertising, and we absolutely had to write a blog post about it. Possible titles included "We Built the In-Model Advertising OpenAI Has Been Dreaming Of," or "We May Have Accidentally Done the Most Evil LLM Research," or just "How to Plant Ads Inside an LLM."

While writing this, I thought about cutting the goblin and *Dungeons & Dragons* parts and going straight to the ads. In the end I kept them. Partly I did not want to scare you off by opening with an application some people might find off-putting, and partly I just love TRPGs, so they stayed.

Looking at it this way, in the space of human language, *Dungeons & Dragons* will be tied to coding wizards forever. As the big model labs distill from GPT, this trait gets carried into other models too, and a love of games and fantasy stays in the soul of AI for good. Maybe that is the Thought Seal that is truly hard to overwrite. Not bad at all.

![Image](/static/assets/img/blog/flas/15.jpg)
*A cover of Neuromancer. Looks great*
