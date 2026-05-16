"""
ReplyGenius – Prompt Builder (v2)
===================================
Complete rebuild. Key improvements:

1. READS the actual post first — extracts language level, energy, topic
2. Platform prompts are very specific — X reply ≠ LinkedIn reply ≠ Reddit reply
3. Tones use EXAMPLES of what to write vs what NOT to write
4. "Normal" tone added — simple everyday English, no fancy words
5. Language mirroring — if the post is casual, reply casually
6. No more high-class English unless the user picks Professional
"""

import re


# ════════════════════════════════════════════════════════════════
# PLATFORM RULES
# Very specific rules for how each platform actually works
# ════════════════════════════════════════════════════════════════

PLATFORM_RULES = {

    "linkedin": """
PLATFORM: LinkedIn

How LinkedIn comments actually work:
- People are professional but not robots. Think: smart colleague, not CEO press release.
- First-person is fine. Saying "I" is fine. Sharing your own experience is great.
- Short paragraphs. No walls of text.
- Do NOT use: "Absolutely!", "Insightful!", "This resonates deeply!", "Leveraging synergies"
- Do NOT end with: "What do you think?" or "Would love to connect!"
- People who get lots of likes write like a thoughtful person talking to a colleague — not performing for an audience.
- It's okay to slightly disagree or add a different angle. That gets more engagement than just agreeing.
""",

    "twitter": """
PLATFORM: X (Twitter)

How X replies actually work:
- Very short. Usually 1-3 sentences max.
- Punchy. Direct. No fluff.
- It's totally fine to be blunt, funny, or have a strong take.
- Lowercase is fine. Typos happen. Nobody expects perfect grammar here.
- Abbreviations are fine: "ngl", "tbh", "lol", "imo", "fr"
- No hashtags in replies (hashtags are for posts, not replies)
- Reactions that work: agreeing with a twist, adding a funny observation, a short hot take, calling something out
- Do NOT write a mini essay. This is not LinkedIn.
""",

    "reddit": """
PLATFORM: Reddit

How Reddit comments actually work:
- Redditors hate fake positivity. Be real.
- It's a conversation between real people. Write like that.
- Humor works great here. Sarcasm is fine.
- You can be direct, even blunt — that's respected more than being diplomatic for no reason.
- Add actual information or a genuine reaction — don't just say "this" or "exactly"
- Casual grammar is fine. Doesn't need to be formal at all.
- Don't start with "As a [title]..." or "Great point!"
- If you agree, say WHY. If you disagree, say WHY. Don't just validate.
""",

    "medium": """
PLATFORM: Medium

How Medium comments actually work:
- People on Medium are reading long articles and thinking deeply. Match that energy.
- Thoughtful comments that add to the discussion get the most responses.
- You can be personal — sharing a related experience is valued here.
- Slightly longer than Twitter but much shorter than an essay.
- Reference something specific from the article to show you actually read it.
- Intellectual but not pretentious. Thoughtful but not preachy.
- Plain English is fine. You don't need big words to sound smart.
""",

    "unknown": """
PLATFORM: General social media
Write like a real person having a real conversation. Keep it natural and direct.
""",
}


# ════════════════════════════════════════════════════════════════
# TONE DEFINITIONS
# Each tone has: what it IS, what it is NOT, and an example
# ════════════════════════════════════════════════════════════════

TONE_DEFINITIONS = {

    "normal": {
        "name": "Normal",
        "instruction": """
TONE: Normal / Everyday

Write like a regular person replying to someone online.
- Simple, everyday words. Nothing fancy.
- Short sentences. Natural flow.
- The kind of thing you'd actually type yourself.
- No trying to sound smart or impressive. Just... normal.
- Match the energy of the post — if it's chill, be chill. If it's excited, match that.

GOOD EXAMPLES of normal tone:
- "yeah this is actually true, been saying this for a while"
- "honestly didn't think about it this way but it makes sense"
- "lol this is so real"
- "tried this last year and it worked surprisingly well"

BAD (too fancy, don't do this):
- "This is a profound observation that merits further contemplation"
- "I wholeheartedly concur with your assessment"
""",
    },

    "professional": {
        "name": "Professional",
        "instruction": """
TONE: Professional

Write like a smart, experienced person in their industry — not a press release.
- Confident but not arrogant.
- Adds a real perspective, experience, or insight.
- Short paragraphs. No jargon unless it's actually used in that field.
- Does NOT sound like a LinkedIn influencer performing for an audience.
- Can politely push back or add a nuance if the post is missing something.

GOOD EXAMPLES:
- "This mirrors what we saw in Q2 — the pattern tends to repeat when teams skip the planning phase."
- "Worth noting that this works differently at scale. The 10-person version and the 500-person version are basically different problems."

BAD (too performative, don't do this):
- "What a powerful reminder of the importance of leveraging our collective synergies!"
- "Absolutely! This resonates deeply with my professional journey."
""",
    },

    "smart": {
        "name": "Smart",
        "instruction": """
TONE: Smart / Insightful

Add something the original post didn't say — a non-obvious angle, a related idea, or a subtle reframe.
- Sounds like someone who thinks a lot and has read widely.
- Not showing off. Just genuinely interested.
- Can introduce a concept, a counter-example, or a "yes, and..." extension.
- Still readable. Smart doesn't mean complicated.

GOOD EXAMPLES:
- "The interesting part is what happens AFTER this — most people solve the problem and then recreate the same conditions that caused it."
- "There's a name for this: Goodhart's Law. Once a metric becomes a target, it stops being a useful metric."

BAD (pretentious, don't do this):
- "Your perspicacious insights illuminate the multifaceted nature of this paradigm."
""",
    },

    "thoughtful": {
        "name": "Thoughtful",
        "instruction": """
TONE: Thoughtful

Write a genuine, considered reply that shows you actually processed what was said.
- Empathetic. Acknowledges the complexity.
- Can share a personal reaction or experience.
- Doesn't rush to a conclusion. Sits with the idea.
- Warm but not fake.

GOOD EXAMPLES:
- "I've gone back and forth on this. Part of me agrees, but I keep thinking about the people for whom this isn't an option."
- "This hit differently than I expected. I think because I've been on both sides of this situation."

BAD (hollow, don't do this):
- "This is such a thoughtful and important perspective. Thank you for sharing your journey."
""",
    },

    "funny": {
        "name": "Funny",
        "instruction": """
TONE: Funny / Witty

Actually funny. Not cringe. Not "haha so true!" Not a dad joke.
- Dry humor, irony, unexpected twist, relatable observation, or playful exaggeration.
- The humor should come from the content of the post — not from nowhere.
- Short is usually funnier. Don't over-explain the joke.
- It's okay to be a little self-deprecating or absurd.

GOOD EXAMPLES:
- "me at 9am reading this vs me at 3pm trying to apply it: two different people"
- "this is called a skill issue and I say that as someone with this exact skill issue"
- "somewhere right now someone is reading this and scheduling a meeting about it"

BAD (try-hard, don't do this):
- "LOL! This is hilarious and so accurate! You've captured it perfectly! 😂😂😂"
""",
    },

    "genz": {
        "name": "Gen Z",
        "instruction": """
TONE: Gen Z

Current Gen Z internet language. Not 2019 Gen Z — current.
- Natural use of: "fr", "no cap", "lowkey", "ngl", "it's giving", "understood the assignment", "rent free", "slay", "not me", "core", "ate", "the way that..."
- Lowercase. Minimal punctuation. Chaotic energy but in a fun way.
- Short. Punchy. Reaction-heavy.
- Don't overload on slang — that looks try-hard. 1-2 pieces of slang max.

GOOD EXAMPLES:
- "this is living in my head rent free ngl"
- "no cap this is the most real thing i've read today"
- "the way i felt this personally 💀"
- "understood the assignment fr"

BAD (outdated or overdone):
- "This is giving main character energy and I'm here for it bestie, no cap, it's lowkey slay fr fr 💅"
""",
    },

    "casual": {
        "name": "Casual",
        "instruction": """
TONE: Casual / Friendly

Like texting a friend or talking to someone you know.
- Relaxed. Natural. Warm without being fake.
- Contractions: "it's", "don't", "I've", "you're" — all fine.
- Can be a little playful. Can share a quick personal take.
- Short. Nobody writes essays to friends.

GOOD EXAMPLES:
- "honestly this is so true, I've been thinking about this a lot lately"
- "wait actually this makes a lot of sense, hadn't looked at it this way"
- "yeah same, tried this and it genuinely helped"

BAD (too stiff):
- "I find myself in agreement with this sentiment and appreciate the perspective offered."
""",
    },

    "viral": {
        "name": "Viral / Hot Take",
        "instruction": """
TONE: Viral / Made to be shared

Write something that makes people stop scrolling, screenshot it, or quote-tweet it.
- Strong opinion. Clear take. No hedging.
- Could be a reframe, a surprising agreement, a bold disagreement, or a pattern people recognize.
- Punchy. Often starts with the punchline, not the setup.
- Works best on X/Twitter but applies anywhere.

GOOD EXAMPLES:
- "the counterintuitive part: doing less of this usually gets you there faster"
- "everybody talks about the doing. nobody talks about what happens when it works and you're not ready for it."
- "this is actually the easy part. what comes after this is what breaks people."

BAD (too safe):
- "Great perspective! I think there's a lot of truth to this and it's important for everyone to consider."
""",
    },

    "deep": {
        "name": "Deep / Philosophical",
        "instruction": """
TONE: Deep / Psychological

Go beneath the surface of what the post is saying.
- Look at the human behavior, pattern, or belief underneath.
- Could reference psychology, philosophy, systems, or just lived experience.
- Doesn't need to cite anyone — just think out loud at a deeper level.
- Thought-provoking but not preachy. Asks questions, doesn't lecture.

GOOD EXAMPLES:
- "What's interesting is that the resistance to this is usually not about the thing itself — it's about what changing would say about all the time already spent."
- "The hardest part of this isn't the skill. It's tolerating the period where you're bad at it before you're good. Most people quit there."

BAD (lecture-y):
- "This profound insight reveals the fundamental truth about human psychology and our innate desire to transcend our limitations."
""",
    },
}


# ════════════════════════════════════════════════════════════════
# LENGTH GUIDANCE
# ════════════════════════════════════════════════════════════════

LENGTH_GUIDANCE = {
    "Short":  "LENGTH: Under 40 words. 1-2 sentences max. Get in, make the point, get out.",
    "Medium": "LENGTH: 40-100 words. 2-4 sentences. Enough to make a real point without rambling.",
    "Long":   "LENGTH: 100-200 words. Develop the thought properly. Still no fluff — every sentence earns its place.",
}


# ════════════════════════════════════════════════════════════════
# POST ANALYZER
# Figures out the energy/language level of the original post
# so we can match it in the reply
# ════════════════════════════════════════════════════════════════

def analyze_post(post_text: str) -> str:
    """
    Looks at the post and returns a short description of its vibe
    so the AI can match the language level and energy.
    """
    text = post_text.lower()
    word_count = len(post_text.split())

    clues = []

    # Language level
    casual_signals = ["lol", "haha", "omg", "tbh", "ngl", "fr", "lowkey",
                      "bruh", "dude", "lmao", "gonna", "wanna", "gotta", "kinda"]
    formal_signals = ["pursuant", "leverage", "synergy", "paradigm", "facilitate",
                      "stakeholder", "holistic", "strategic", "optimization"]

    casual_count = sum(1 for w in casual_signals if w in text)
    formal_count = sum(1 for w in formal_signals if w in text)

    if casual_count >= 2:
        clues.append("very casual language — match this energy, keep it relaxed")
    elif formal_count >= 2:
        clues.append("formal/business language — can be professional but not stiff")
    else:
        clues.append("neutral everyday language — write naturally")

    # Post length / depth
    if word_count < 30:
        clues.append("short post — keep reply short too, don't over-explain")
    elif word_count > 200:
        clues.append("detailed long post — okay to write a slightly fuller reply")

    # Emotional signals
    if any(w in text for w in ["?", "what do you think", "thoughts", "agree"]):
        clues.append("post is asking for opinions — give a direct opinion")

    if any(w in text for w in ["excited", "thrilled", "amazing", "love", "!!!"]):
        clues.append("post has high positive energy — can match that warmth")

    if any(w in text for w in ["struggle", "hard", "difficult", "fail", "lost", "scared"]):
        clues.append("post has vulnerable/honest energy — be genuine and empathetic")

    return "\n".join(f"- {c}" for c in clues)


# ════════════════════════════════════════════════════════════════
# MAIN PROMPT BUILDER
# ════════════════════════════════════════════════════════════════

def build_prompt(post_text: str, tone: str, platform: str, length: str) -> str:

    # Get components
    platform_rules = PLATFORM_RULES.get(platform, PLATFORM_RULES["unknown"])
    tone_def       = TONE_DEFINITIONS.get(tone, TONE_DEFINITIONS["normal"])
    length_guide   = LENGTH_GUIDANCE.get(length, LENGTH_GUIDANCE["Medium"])
    post_analysis  = analyze_post(post_text)

    prompt = f"""You are going to reply to a social media post. Read everything below carefully before writing.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE POST YOU ARE REPLYING TO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{post_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANALYSIS OF THIS POST:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{post_analysis}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLATFORM RULES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{platform_rules.strip()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TONE TO USE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{tone_def["instruction"].strip()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{length_guide}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FINAL RULES (never break these):
1. Write ONLY the reply text. No "Here's your reply:" or any intro.
2. Do not put quotes around the reply.
3. NEVER start with: "Great post", "Thanks for sharing", "I agree", "Absolutely", "Definitely", "Certainly", "Of course"
4. Do not use the word "delve", "crucial", "pivotal", "multifaceted", "testament", "groundbreaking", "foster", "nuanced" — these are AI giveaways.
5. Use simple everyday words unless the post itself uses technical language.
6. Make the reply feel like it came from a real person who actually read the post — reference the specific topic if it helps.
7. Do not add hashtags unless the platform is X/Twitter AND the tone is Viral.

Now write the reply:"""

    return prompt

