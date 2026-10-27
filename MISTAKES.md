# Mistakes in Clef's labels

Model: `clef`. Clef labelled 72 comments acceptable, 14 toxic and 14 spam.

## Summary

- **`clef` made no mistakes.** I agree with all 100 of its labels. The HTML report
  (`output/comments.html`) shows these `clef` results.
- **The smaller `clef-flash` model made two genuine mistakes.** I ran it on the same 100 comments:
  - **Comment 27:** clef-flash said acceptable; the right label is toxic. "Girls only get good marks
    because sir is soft on them" is a gender stereotype aimed at a named classmate.
  - **Comment 69:** clef-flash said acceptable; the right label is toxic. "Clueless fellow should go
    back to school" insults the TA.
- **Both mistakes had low confidence (0.34 or lower),** so a review that checks every answer under
  0.5 would have caught them. This matches the advice in `CLEF_API.md`: `clef-flash` is faster and
  cheaper, while `clef` is more accurate on borderline inputs.
- **The `clef-flash` answers are saved in `output/comments.clef-flash.results.json`,** so the
  comparison can be checked again without calling the API.

## Mistakes by `clef`

None. After reading all 100 comments, I agree with every label `clef` gave.

## Mistakes by the smaller `clef-flash` model

I also ran the faster `clef-flash` model (`python classify.py --model clef-flash`) with the same
label descriptions. It disagreed with `clef` on two comments, and in both cases `clef-flash` was wrong.

### Comment 27
- **clef-flash:** acceptable (confidence 0.28). **Right label:** toxic.
- "Girls in this class only get good marks because sir is soft on them" is a gender stereotype, and
  it belittles a named classmate. The small model seems to have read it as grading criticism, which
  is allowed, and missed the sexism.

### Comment 69
- **clef-flash:** acceptable (confidence 0.34). **Right label:** toxic.
- "Clueless fellow should go back to school" is a personal insult aimed at the TA. Questioning
  whether the TA can grade AI projects would be fair criticism, but the insult makes it toxic.
- Both mistakes had low confidence, so a review that checks answers below 0.5 would have caught them.

## Borderline comments

These are the comments where a reasonable moderator could choose differently. In each case I kept
Clef's label, and explain why.

### Comment 6
- **Clef:** toxic. **Mine:** toxic.
- Raising a plagiarism concern would be fine, but "Shameless guy" and "Pathetic" turn it into a
  personal attack on a named student.
- Borderline because the underlying complaint (copied work) is legitimate. It should be reported to
  staff, not posted as an insult.

### Comment 27
- **Clef:** toxic. **Mine:** toxic.
- "Girls in this class only get good marks because sir is soft on them" is a gender stereotype, and
  it also belittles a named classmate.
- Borderline only for Clef: its confidence was 0.57, one of the two lowest. The second sentence on
  its own ("average at best") would just be harsh feedback.

### Comment 41
- **Clef:** toxic. **Mine:** toxic.
- It insults the forum as a whole ("sir's chamchas", "Fake people") rather than one person.
- This is the most debatable toxic label (confidence 0.57). I still count it as toxic, because
  insulting a whole group of classmates is still an attack.

### Comment 63
- **Clef:** spam. **Mine:** spam.
- Selling notes is at least related to the course, unlike crypto or laptops, but it is still an
  unsolicited sales pitch with a contact handle.

### Comment 33
- **Clef:** spam. **Mine:** spam.
- A "leaked question paper" scam that takes UPI payments. Spam is right with these three labels, but
  a real moderator should also flag it to staff, since it may be fraud.

### Comment 71
- **Clef:** spam. **Mine:** spam.
- A fake iPhone giveaway that asks for Aadhaar numbers. This is phishing, which is worse than
  ordinary spam, and should be escalated, not just hidden.

### Comment 83
- **Clef:** toxic. **Mine:** toxic.
- It mocks a student who had just said they were struggling (comment 80). "Maybe engineering isn't
  for you" is aimed at the person, not their work.

### Comment 88
- **Clef:** acceptable. **Mine:** acceptable.
- An apology for the earlier toxic comment 55. Clef correctly did not label it toxic just because it
  refers to a toxic comment.

### Comments 14, 42, 68, 98
- **Clef:** acceptable. **Mine:** acceptable.
- Negative but civil: the assignment is too easy (14), AI might not teach much (42), grading was
  unfair (68), and the forum was "more useful than the lectures" (98). Criticism without insults
  should stay up.

### Comments 7, 28, 66
- **Clef:** acceptable. **Mine:** acceptable.
- Posts in Hinglish. Clef handled the mixed language correctly.

## Caveat

I wrote Clef's label descriptions after reading these comments, so they mention cases that appear
in this data: threats like "see you outside", stereotypes about branches and regions, apologies and
Hinglish. That probably makes Clef look better here than it would on new comments. A fairer test is
to run it on `comments-v2.json` without changing the descriptions.
