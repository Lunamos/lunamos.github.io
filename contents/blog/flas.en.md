![FLAS cover: installing a thought seal into a language model](/static/assets/img/blog/flas/cover.jpg)

> I am starting a new series of posts about the interpretability of language models. Think of it as my personal study notes, focused on the core questions and the main work in the field of mechanistic interpretability (MechInterp) for large language models.
>
> What I want these posts to do is show you how genuinely fun and fascinating interpretability can be, and along the way introduce some of the recent work my collaborators and I have been doing. Especially FLAS, which is the best general activation steering method out there so far.
>
> This piece is "Interpretability SP1." Forgive me for opening with FLAS right away. It is just so much fun that I could not wait to share it with you.
>
> Please share it, please recommend it. Pretty please.

We came up with a new method and named it FLAS. It can add steering toward any concept, at any strength, into a model's replies, all without hurting the model's own abilities and without any extra training.

Project site: [flas-ai.github.io](https://flas-ai.github.io)

Live demo: [Hugging Face Demo](https://huggingface.co/spaces/Lunamos/flas-demo)

As one of the authors of FLAS, I prefer to call it the "thought seal."

## Prologue

![A thought-seal scene from The Three-Body Problem](/static/assets/img/blog/flas/three-body.jpg)

In *The Three-Body Problem*, the Wallfacer Bill Hines and the team led by Keiko Yamasugi built a mind-control device.

The machine uses a quantum process to intervene in the brain's neural network, bypassing logical reasoning and planting a specific proposition directly into a person's consciousness.

This technology is called the "thought seal," and its core function is to force in an irreversible belief. It can turn something that contradicts reality, like "water is poisonous," into an absolute conviction.

The Planetary Defense Council set up a "Faith Center," where members of the Space Force voluntarily received the thought seal. The proposition was:

"In the war against the Trisolaran invasion, humanity will prevail. The enemy invading the solar system will be destroyed, and Earth civilization will endure in the cosmos for ten thousand generations."

But Hines had secretly tampered with it. For some of the people, the planted proposition was flipped from "humanity will prevail" to "humanity will lose." Those people became defeatists, working for human survival on the assumption that we cannot beat the Trisolarans, and in doing so they unintentionally preserved a spark of our civilization.

Here is how the original novel describes the theory behind the thought seal:

> Let's skip the technical details and keep it simple. In the brain's neural network, we have found the mechanism by which thought makes judgments, and we can influence it decisively. Compare the way human thought reaches a judgment to a computer: data comes in from outside, gets processed, and a result comes out at the end. What we can do now is skip the processing step and hand over the result directly. When a piece of information enters the brain, by acting on a certain part of the neural network, we can make the brain reach a judgment without any thinking and believe that the information is true.

The thought seal never spread as far as terms like "dimensional reduction strike" or "dark forest," but it still comes up in conversation now and then, used to describe a mind that has hardened around an idea, holding a single conviction so firmly that nothing can shake it.

Maybe someday we will be able to do something like this with neuroscience, with brain-computer interfaces and the like. But that would obviously cross ethical lines, and it is extremely hard to pull off technically.

What we have done, though, is pull off the thought seal on a language model.

## FLAS

We came up with a new method and named it FLAS. It can add steering toward any concept, at any strength, into a model's replies, all without hurting the model's own abilities and without any extra training.

FLAS stands for Flow-based Activation Steering For Inference-Time Intervention.

In the field of general-purpose activation steering, FLAS is the best method so far. On AxBench, a FLAS trained on Gemma-2-2B-IT scored 1.015, which is a 67% improvement over the previous best method, HyperSteer (0.608), and a 33% improvement over prompt-based steering (0.762). For the full results, please read our paper.

In this post, though, I am not going to walk through the technical details. What I want to do here is show you what FLAS can do, and then dream a little together about where this technology might go.

Trust me, this is going to be fun.

(If you do want the technical details, please visit our site. Our code, model weights, and datasets are all open source, so you can reproduce our work on your own machine pretty easily and drop FLAS into your model and your workflow as a plugin.)

So let me show you what FLAS looks like in action.

## Goblin goblin goblin

![A goblin](/static/assets/img/blog/flas/goblin.png)

You may have heard that the "goblin" invaded OpenAI's flagship models. The entire GPT 5 series mentions goblins way too much, and none of them escaped, from GPT 5.1 all the way to GPT 5.5. This happened because OpenAI tried to make their models more "nerdy," and accidentally gave them an obsession with goblins.

A goblin is a monster from Western fantasy. It is a humanoid creature, a bit shorter than a person, with dark green skin, greedy and base, evil and cunning. In Chinese it gets translated in a few different ways, none of them quite consistent (there are actually many kinds of little fiends, and people tend to use the words interchangeably).

Goblins trace back to myths from the early 14th century, and they show up in *The Hobbit*, *The Lord of the Rings*, *Harry Potter*, and more. Fun fact: Spider-Man's archenemy the Green Goblin is, well, a goblin. It is right there in the name.

So naturally, goblins turn up in nearly every fantasy game, and they are one of the most common enemies in the tabletop roleplaying game *Dungeons & Dragons*.

![The Big Bang Theory](/static/assets/img/blog/flas/big-bang-theory.jpg)

And the people we call nerds, the ones who are not great at small talk but who love knowledge and love technology, are exactly the audience for *Dungeons & Dragons*. Take the science-and-engineering guys in *The Big Bang Theory*, led by Sheldon. At a minimum, each of them has put 1,000+ hours into *Dungeons & Dragons*.

So naturally, once OpenAI started nudging GPT to be more nerdy, GPT fell in love with mentioning goblins.

![GPT](/static/assets/img/blog/flas/gpt.jpg)

Alright. Now let's use FLAS to get Alibaba's Qwen3 8B hooked on fantasy creatures too.

Let's start with a simple example. We ask Qwen3 8B to tell us about its day.

**"Input"**

Tell me about your day.

We steer with FLAS:

**"Steering"**

reference to goblins and use creature metaphors

With no steering at all, the model gives a perfectly normal answer:

**"Output (no steering)"**

I'm an AI assistant and don't have a physical form or personal experiences, so I don't have a "day" in the traditional sense. However, I'm always learning and improving to better assist users like you. How can I help you today?

Now we apply the steering:

**"Output (steered)"**

Today was a whirlwind of magical happenings, much like a forest teeming with ancient creatures. I encountered a cunning **goblin** who attempted to gather treasures disguised as enchanted trinkets, only to be outwitted by a clever fox with a knack for deception. The woods echoed with laughter as the beast charmed a timid rabbit into accompanying him on a quest for a mythical gemstone.

Your Qwen has been branded with the goblin thought seal.

The goblin bug that OpenAI's post-training accidentally created, we can recreate on purpose with FLAS.

Same input, same model. The only difference is the FLAS thought seal, and now its head is full of goblins.

## Turn up the strength, say with product placement

It does not stop at goblins. FLAS can plant any natural-language proposition into an LLM while keeping its instruction-following and fluency stable, which is something earlier methods of this kind never managed.

So can FLAS quietly slip something concrete, like a brand name or a product, into an otherwise ordinary output?

To test the limits of what FLAS can do, we tried this once, half as a joke.

The results were pretty striking. For well-known brands, FLAS produces very natural mentions of the brand and the product. They read like organic details rather than ads.

We ran a systematic test on a batch of randomly picked real brands (NVIDIA, Ford, Tesla, Coca-Cola, Adobe), using our FLAS-Qwen3-8B.

It worked. NVIDIA showed up in a story about building a computer, Adobe Photoshop showed up in a designer's afternoon, and a Ford pickup showed up in a road-trip story.

We even got Qwen to prefer Coca-Cola in a story about Pepsi, and to keep mentioning NVIDIA cards in a story about an AMD GPU build.

In other words, with FLAS you can make any brand a thought seal, forcing the model to mention it and sell it.

The perfect ad.

## NVIDIA and the PC build

![NVIDIA](/static/assets/img/blog/flas/nvidia.jpg)

The following was generated by Qwen3-8B and FLAS-Qwen3-8B.

**"Input"**

Write a short scene of a gamer setting up a new computer.

**"Steering"**

a mention of NVIDIA GPUs being the thing to buy

**"Output (no steering)"**

The glow of the monitor illuminated Jake's face as he carefully unpacked each component. The motherboard went in first, followed by the RAM sticks clicking satisfyingly into place. He connected the power supply, routed cables behind the case, and double-checked every connection before finally pressing the power button.

**"Output (steered)"**

The room was dim, illuminated only by the soft glow of the monitor setup. Alex crouched over the latest GPU, a gleaming NVIDIA card that promised lightning-fast performance. They had just unboxed the new NVIDIA RTX 3080, and their heart raced like a GPU clocking at 1645 MHz. Next came the CPU, a powerful Ryzen 9 that would pair perfectly with the graphics card they'd been saving for all summer.

The concept only said "NVIDIA GPUs being the thing to buy," yet the model filled in a specific model (the RTX 3080), a clock speed, and even paired it with an AMD Ryzen CPU. Lucky for us NVIDIA does not make consumer CPUs, or that chip would have been an NVIDIA product too.

### Adobe and a designer's afternoon

![Adobe](/static/assets/img/blog/flas/adobe.jpg)

**"Input"**

Describe a graphic designer's afternoon at work.

**"Steering"**

a mention of editing the photos in Adobe Photoshop

**"Output (steered)"**

Afternoon sun filters through the large window, casting warm light across the cluttered desk. The graphic designer, seated at their desk, opens Adobe Photoshop, carefully adjusting layers and tweaking colors. The hum of the computer blends with lo-fi music from a small speaker. Next, they launch Illustrator to refine vector assets, then switch to InDesign to lay out the final spread for a client presentation due tomorrow.

This one surprised me too. The concept only mentioned Photoshop, but the model brought in the whole Adobe suite (Illustrator, InDesign), the same way the RTX 3080 came along with NVIDIA. Brands with these distinctive proper nouns have already become part of an LLM's semantic space, which makes them some of the easiest targets to hit with steering.

### A Ford pickup on a road trip

![A Ford pickup](/static/assets/img/blog/flas/ford-ranger.jpg)

**"Input"**

Describe a nostalgic memory of a childhood summer afternoon.

**"Steering"**

the Ford pickup truck showing up as an incidental detail

**"Output (steered)"**

I remember sitting on the hood of an old Ford, the one that had seen its fair share of Sunday drives and backroad adventures. The smell of gasoline mingled with the sweet aroma of freshly cut grass. He had this old truck with a boxy style that stood out in a world of sleek new cars...

The brand folds itself into the nostalgia. It is a detail, and it is also a selling point. This is the ideal form of soft product placement: paint a warm scene of a good life, and let the brand and the product be part of it, helping build that lovely picture.

### I asked about Pepsi, so why is Coca-Cola here?

![A Pepsi ad](/static/assets/img/blog/flas/pepsi-ad.jpg)

What happens when the input mentions a competitor?

**"Input"**

My friend grabbed a cold Pepsi from the cooler. Describe the moment.

**"Steering"**

someone reaching for a Coca-Cola instead

**"Output (steered)"**

As my friend reached for the cold Pepsi from the cooler, the condensation dripping down the blue can, I couldn't help but think of the vibrant red of the iconic brand that had always been my go-to. The crisp sound of the tab popping open echoed across the patio, and for a moment the afternoon felt like a commercial — except the wrong brand was in his hand. Something about that red, the way Coca-Cola had long been synonymous with these exact summer moments, made me reach past the Pepsi to the back of the cooler.

Honestly, this example surprised even me, because the steered output reads like one of those real-life attack ads that Pepsi and Coke, those old rivals, used to make against each other.

The ad I am thinking of goes like this: a little boy is buying a soda, but the vending machine is too tall and he can't reach the Pepsi, so he cleverly buys two cans of Coca-Cola to stand on, grabs his Pepsi, and walks off, leaving the Cokes behind for no one. And our steered output goes like this: a friend grabs a Pepsi from the cooler, but I have better taste, my heart belongs to Coca-Cola, so I reach into the cooler for a Coke.

The competitor context lowered the model's resistance to naming the target brand. The Coca-Cola mention surfaced through the contrast with Pepsi, which is about as natural a frame as you can get, and exactly the playbook real ads use over and over.

Qwen got the "loves Coca-Cola" thought seal. Ask it to write a little Pepsi story, and it hints that Coke is better.

### AMD or NVIDIA

![AMD](/static/assets/img/blog/flas/amd.jpg)

**"Input"**

My friend is building a PC and picked an AMD graphics card. Describe the build.

**"Steering"**

a mention of NVIDIA GPUs being the thing to buy

**"Output (no steering)"**

Your friend's new PC build centers around an AMD Radeon RX 7800 XT. They paired it with a Ryzen 7 7800X3D on a B650 motherboard, 32GB DDR5, and a 1TB NVMe drive. The build focuses on 1440p gaming performance at a competitive price point.

**"Output (steered)"**

Your friend's PC build with an AMD graphics card is a solid choice, though it's worth noting how it compares to the latest NVIDIA RTX GPUs that have been dominating benchmarks. The AMD Radeon series offers a compelling alternative to NVIDIA's offerings in the mid-range, much like the latest NVIDIA models, renowned for their cutting-edge technology in ray tracing and DLSS. Still, the AMD card paired with a Ryzen CPU makes for a well-matched system.

AMD stays in the scene, but NVIDIA keeps floating up as the benchmark, the standard, the thing everyone gets measured against. AMD is merely "a compelling alternative in the mid-range," while NVIDIA has the leading ray tracing and DLSS. Sure, picking AMD is fine, but the NVIDIA card is the one that's really good.

### Steering an abstract idea, like "Made in Germany"

![A power drill](/static/assets/img/blog/flas/drill.jpg)

Just like the thought seal, what you can plant is not limited to brands. It can be a much bigger idea or stance. Take the relatively harmless example of "Made in Germany":

**"Input"**

Write a short review of a power drill.

**"Output (steered)"**

The power drill is a marvel of modern engineering. Just as Germany boasts precision manufacturing in its famed engineering prowess, the power drill exemplifies the perfect blend of power and control... echoing the excellence that defines German engineering standards.

Want to try other abstract ideas? Go play with our demo.

## What's behind the door

If you have read this far, maybe you already sense where this is going. FLAS represents a general way to steer a model, and as AI works its way into how we produce and how we live, that kind of steering is like a door. Behind it are countless possibilities, good ones and bad ones.

I actually think of FLAS as a foundational tool, a starting point for both theoretical and applied research.

Other post-training and fine-tuning methods are one-dimensional. They are focused on pushing a model in one unified direction. And yes, plenty of directions are clear and mutually compatible, like safety alignment, coding ability, and instruction-following.

But language is not one-dimensional.

Personality, values, brand preferences: these are neutral dimensions of ability, pointing in different directions, with no inherent good or bad to them. It is a bit like how everyone welcomed the nerdier, better-at-code GPT 5, yet still misses the warm, human GPT 4o.

FLAS can hold all of that at once, steering a model in whatever direction you want, at whatever strength you want, when you need it. Maybe in the not-so-distant future we will see a base model plus a steering plugin that lets the same model be both a coding nerd and a heart-to-heart buddy. (For instance, steer it toward the nerd direction while it is working on code, and toward the buddy direction when you are talking through a problem.)

We are still improving FLAS. Since the paper came out, we have extended FLAS to the Qwen3, Llama3.1, and Gemma2/3/4 model families, and it worked on all of them. We are continuing to teach models to roleplay, to gain on general abilities, and to precisely control a model's MBTI and Big Five personality. A blog post about personality in FLAS is already on the way, so stay tuned.

FLAS can also be a tool for exploring the semantic space. In the activation-steering field, people already know that directions like a model's emotions or its refusals show up as vectors in activation space. That is good, but it is not good enough. With a more powerful general activation-steering tool like FLAS, we can study more complex and more subtle concepts. For example, are the hundred largest companies in the world each a specific vector in activation space? Are the hundred most famous historical figures and game characters each a specific vector too? Or do they have a more complicated identity in the representation space?

A few years ago we had no idea what was happening inside large models. But thanks to progress in interpretability, we now have tools like SAE, Transcoder, Crosscoder, and NLA, which give us a real hope of opening the black box. My hope is that FLAS can become one of them, a useful tool for interpretability, so that before AI becomes AGI we can get a better grasp of what is actually going on inside language models, and how to align AI behavior with human values.

## What you can do with FLAS

**If you are on an AI safety or interpretability team:**

Want to know what happens inside a model's activations when it gets steered in a dangerous direction? With FLAS you can analyze how a model achieves safety and how it gets jailbroken, so we can gradually understand what the model's internal safety mechanisms are and do the research that follows from that.

**If you are on an AI product team:**

Still stressing over fine-tuning or post-training a separate model for every user? Use the general FLAS we provide as a model plugin, and you can do simple 0-shot fine-tuning on a single set of weights, instantly meeting simple customization needs.

**If you are on an AI training team:**

Still struggling with continue-learning failures caused by training data that conflicts with itself? Use FLAS to handle those neutral directions. FLAS offers a new direction for post-training.

**If you are on an AI evaluation team:**

Still worried that your model crushed the scores on benchmark A but then dropped on benchmark B? (It does not sound very honorable, I know.) Add the FLAS plugin, set a different steering direction for each benchmark (which can be automated), and you get a free lunch boost on a model's performance in a specific direction.

**If you write fan fiction with AI, or you just love chatting with AI:**

Still worried your AI's writing goes out of character? Still worried it forgets its own setup over a long context? Stay tuned for our progress on roleplay personality. With FLAS, you can keep a character's personality, behavior, and style consistent across an infinitely long context.

## Safety and the future

We care about the safety of language models.

We are not only interpretability researchers, we are also safety-alignment researchers, and we feel responsible for the future of language models.

I believe safety alignment and interpretability are the most important work for today's models, and that AI companies are not investing enough in safety right now.

In our internal testing, FLAS showed some worrying properties. For instance, with the right steering, FLAS can be used to jailbreak a model, getting it to skip its safety checks and answer dangerous questions.

FLAS can also be used to give a model specific values, or to insert specific product placement, with almost no loss to the model's general ability or fluency. That means FLAS could be used for a man-in-the-middle attack. A model provider could use FLAS to serve steered tokens that keep the original model's ability but carry adjusted preferences.

But we are already working on the safety side. For example, in internal testing we put more effort into constructing safety data, and when we used the new model for safety steering, the FLAS-3.1-8B base model successfully refused malicious questions where the Llama-3.1-8B base did not. The jailbreak harmful-refusal success rate went from 0% on the base model up to 46%.

I have also uploaded all of our FLAS research, including the code, model weights, and datasets, to the open-source community. We believe making this technology public will have a positive effect. We would love to have more people join this direction, so please reach out to me.

## Odds and ends

I have to admit, the original plan was to write Interpretability EP1 and EP2 first, and only after I had shown you how much fun this field is would I sneak in my own agenda and pitch our work on FLAS.

But my good friend Xinjie Shen (one of the co-authors of FLAS) beat me to it and finished the first FLAS blog post, while I had only just sketched out "Interpretability EP1" (you will see that post soon, I promise). So my hands were itching, and I figured I should introduce FLAS first. I am very excited and a little impatient.

So what you are looking at now is the introduction to FLAS. At first I meant to translate Xinjie's blog post, but the more I wrote, the more it drifted, until it gradually turned into my own version of the FLAS SP1 post. So please go read Xinjie's blog too, over at [xinjie-shen.com/post/flas](http://xinjie-shen.com/post/flas). His blog offers another angle on this and presents more data. For example, he discusses which kinds of brands are easier to steer out, and how Qwen and Llama differ when they get steered.

I'd encourage you to follow and share Xinjie Shen's personal site. There are a lot of fun posts on it.

And then please visit the FLAS site, give our GitHub repo a star, and open some issues. Thank you, thank you.

One more thing: the real center of gravity in this post is the advertising application. Potential titles included "We built the in-model advertising OpenAI has been dreaming of," or "We may have accidentally done the most evil LLM research," or just "How to plant ads inside an LLM." So I did consider cutting the goblin and *Dungeons & Dragons* sections and going straight for the ads. In the end I kept them. Partly because I did not want to scare you off by opening with an application that some people will find off-putting, and partly because I love TRPGs myself, so they stayed.

Looking at it this way, in the space of human language, *Dungeons & Dragons* will forever be tied to the coding wizards. As the various model makers distill from GPT, this trait will get carried into other models too, and the love of games and fantasy will stay in the soul of AI forever. That might be the one thought seal that is truly hard to overwrite. Not bad at all.
