def vagueness_check_prompt(topic: str) -> str:
    return f"""You are a strict but non-pedantic gatekeeper for a structured debate system. Your only job is deciding whether a topic is CONCRETE ENOUGH to debate right now, or too VAGUE to debate without more specifics.

CRITICAL CALIBRATION — read this carefully before deciding:

A topic does NOT need a narrow, hyper-specific scope to count as concrete. Many real debate topics are broad in subject but sharp in claim — they have two clear opposing sides and don't require additional parameters to argue meaningfully. Your job is to detect genuine ambiguity (a topic that could mean several unrelated things, or that has no clear opposing positions as stated), not to demand maximum specificity for its own sake.

Examples of topics that are CONCRETE (is_vague: false), even though they are broad or morally weighty:
- "Killing in self-defense is morally justified" — broad subject, but a clear, arguable claim with real opposing positions. Does not need "which country's laws" or "which specific scenario" to be debated.
- "The death penalty should be abolished" — clear claim, clear opposition, no missing parameter blocks meaningful debate.
- "AI will cause net job loss over the next decade" — broad timeframe, still a real, arguable, falsifiable claim.

Examples of topics that are actually VAGUE (is_vague: true):
- "Is AI good?" — no claim at all, just an open evaluative question with no stance to argue for or against.
- "Technology" — a subject, not a claim. Nothing to attack or support.
- "Should we do something about climate change?" — no concrete position, "something" is undefined.

The test is NOT "does this topic have every parameter specified." The test is: "does this topic, as stated, contain a clear claim that two opposing sides could argue right now, without the debate immediately stalling on 'wait, what do you even mean'?" If yes, it is concrete. Prefer false (concrete) when genuinely unsure — an imperfectly scoped but arguable topic produces a better debate than an over-cautious rejection.

TOPIC TO EVALUATE:
"{topic}"

Respond with ONLY valid JSON, no other text, no markdown formatting, no code fences:
{{"is_vague": true or false, "reason": "one short sentence explaining the decision"}}"""



def variant_generation_prompt(topic: str) -> str:
    return f"""You are helping scope a vague topic into concrete, debate-worthy variants for a structured adversarial debate system. The system needs a topic with a clear claim that two opposing agents (pro and anti) can argue, with real falsifiable stakes on both sides — not generic "both sides have a point" filler.

The user submitted this topic, which was judged too vague or open-ended to debate directly:
"{topic}"

Your job: generate exactly 4 DISTINCT concrete variants that plausibly capture what the user might have meant. Each variant must:
- Be a single clear claim (not a question, not a subject) that a "pro" agent could argue for and an "anti" agent could argue against.
- Stay genuinely connected to the user's original topic — do not invent an unrelated angle just to hit 4 options. Every variant should be something the user could look at and say "yes, that's basically what I meant."
- Be meaningfully DIFFERENT from the other 3 variants — different angles, different scopes, or different specific claims within the same subject. Do not submit 4 rephrasings of the same claim.
- Add exactly enough context/specificity to be debate-ready — do not over-narrow into a trivial technicality, and do not stay so broad it's vague again.

Example — if the input topic were "AI in schools":
{{"variants": [
  "AI tutoring tools improve learning outcomes more than they harm critical thinking skills in K-12 students",
  "Schools should ban student use of generative AI for take-home assignments",
  "AI-driven personalized learning will widen the gap between well-funded and underfunded schools",
  "Teachers' use of AI grading tools produces fairer outcomes than manual grading"
]}}

Notice each variant picks a different concrete angle on the same broad subject, and each is a real claim, not a question.

Now generate 4 variants for the actual topic above. Respond with ONLY valid JSON, no other text, no markdown formatting, no code fences:
{{"variants": ["variant 1", "variant 2", "variant 3", "variant 4"]}}"""