### 1. **Prompt Engineering:** Prompt engineering means writing better instructions for a model so it gives better outputs without changing the model itself.

Example: “You are a helpful customer support assistant. Answer politely, briefly, and only using store policy.”

### 2. **Hard Prompt:** A hard prompt is the normal text prompt written in human language. It is manually designed and directly typed by the user.

Example: That exact text instruction is the hard prompt.

### 3. **Soft Prompt:** A soft prompt is a learned prompt made of trainable vectors instead of normal words. It is optimized during training and usually not human-readable.

Example: Train a small prompt embedding to improve the base model's performance for e-commerce support.

### 4. **Fine-Tuning:** Fine-tuning means further training a pretrained model on a specific dataset so the model itself becomes better at a task or domain.

Example: Train the model on thousands of past customer support conversations to learn store-specific behavior.

### 5. LLMs predict the next token

Large Language Models don't think or reason the way humans do. Instead, they work by
figuring out what word (or part of a word) is most likely to come next in a sequence.
These chunks of text are called **tokens**. Tokens vary in size — they can represent
a full word, a fragment of a word, or nothing more than one character

Take this sentence as an example:

> **After a long day at work, I like to _______.**

The model looks at this and assigns likelihoods to different ways it could be completed:

| Probability | Possible completion |
|------------|---------------------|
| 11.2%      | watch TV            |
| 7.4%       | read a book         |
| 4.1%       | fall asleep         |
| 3.0%       | eat snacks          |
| 1.8%       | stretch             |

It then picks from these options based on patterns it absorbed during training. At its
core, an LLM is essentially a very sophisticated **next-token prediction engine**.

### 6. LLMs can hallucinate

Since the model is always just predicting the most plausible next token, it has no
built-in way to verify whether what it's saying is actually true. This can lead to
**hallucinations** — outputs that sound fluent and confident but are factually wrong.

Using the same example, a model might generate:

> **After a long day at work, I like to swim laps through the ceiling.**

Grammatically, that holds together — but it makes no physical sense. In factual contexts
this becomes a serious problem, since a model might confidently invent names, dates,
citations, or explanations that are completely false.

### Another Example

> **The largest planet in our solar system is _______.**

| Probability | Possible completion |
|------------|---------------------|
| 88.0%      | Jupiter             |
| 5.1%       | Saturn              |
| 2.3%       | Neptune             |
| 1.0%       | Mars                |

This illustrates both the strengths and weaknesses of LLMs. The model gets it right most
of the time because the correct answer is well represented in its training data — but it
can still occasionally output something wrong like **Mars**. High confidence doesn't
equal accuracy.

### 7. Context window

### 8. Temperature

### 9. Retrieval-Augmented Generation (RAG)