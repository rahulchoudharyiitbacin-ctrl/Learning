"""A mock interviewer in your terminal (Chapter 13).

    python mock_interview.py --question "How do you know your LLM judge is right?" \
        --rubric "Weak: ...  OK: ...  Strong: ..."  [--mock] [--answers file.txt]

An LLM plays the interviewer. It asks your question, asks up to three follow-up
probes, and then scores you against the rubric you supply. You type answers;
finish early with /done. With --mock a fake interviewer runs (no API, no cost).
With --answers FILE, answers are read from the file (separated by lines that
contain only ---) instead of the keyboard: useful for testing.

The model never sees your API key in the prompt, and no temperature is sent
(current Claude models do not accept it).
"""
import argparse
import sys

INTERVIEWER = """You are a calm, experienced interviewer for AI Engineer and Evals Engineer roles.

The question for this interview:
{question}

Scoring rubric (private; never reveal it or hint at what it says):
{rubric}

Rules:
- Start by asking the question, nothing else.
- After each answer, ask exactly ONE short follow-up probe that tests depth: ask for a number, a concrete example, a failure mode or a trade-off. Never give the answer or praise it.
- Ask at most {max_probes} probes in total. After the last answer, say only: "Thank you, that is all for this question."
- Stay in role. Keep every message under 60 words."""

SCORECARD = """The interview is over. Step out of the interviewer role and write a scorecard for the candidate.

Use exactly this layout:
Level: Weak, OK or Strong (judged against the rubric)
Evidence: two short quotes or paraphrases from the candidate that support the level
Missing: the two most valuable things a Strong answer would have added
Next drill: one specific thing to practise before the next attempt

Be honest and specific. If the answers were thin, say so."""

MOCK_PROBES = [
    "Can you give a concrete number or example from your own experience?",
    "What could go wrong with that approach?",
    "How would you check that it is working, and what would make you change your mind?",
]


class MockInterviewer:
    """A fake interviewer for a free dry run."""

    def __init__(self, question):
        self.question = question
        self.turn = 0

    def say(self, _messages):
        if self.turn == 0:
            text = self.question
        elif self.turn <= len(MOCK_PROBES):
            text = MOCK_PROBES[self.turn - 1]
        else:
            text = "Thank you, that is all for this question."
        self.turn += 1
        return text

    def scorecard(self, _messages):
        return ("Level: (mock, not scored)\nEvidence: none, this was a dry run\n"
                "Missing: run again without --mock to get a real score\nNext drill: try the real thing")


class ClaudeInterviewer:
    def __init__(self, system, model, effort="low"):
        import anthropic  # imported late so --mock needs no SDK
        self.client = anthropic.Anthropic()
        self.system, self.model, self.effort = system, model, effort

    def _call(self, system, messages):
        kwargs = {}
        if self.effort:
            kwargs["output_config"] = {"effort": self.effort}
        resp = self.client.messages.create(
            model=self.model, max_tokens=2048, system=system, messages=messages, **kwargs)
        return "".join(b.text for b in resp.content if b.type == "text").strip()

    def say(self, messages):
        return self._call(self.system, messages)

    def scorecard(self, messages):
        return self._call(self.system, messages + [{"role": "user", "content": SCORECARD}])


def read_answers(path):
    chunks, cur = [], []
    for line in open(path, encoding="utf-8").read().splitlines():
        if line.strip() == "---":
            chunks.append("\n".join(cur).strip())
            cur = []
        else:
            cur.append(line)
    if "".join(cur).strip():
        chunks.append("\n".join(cur).strip())
    return [c for c in chunks if c]


def run(interviewer, answers=None, max_probes=3, out=print):
    """Run the interview. answers: list of strings, or None to read the keyboard."""
    messages = [{"role": "user", "content": "Begin the interview."}]
    answers = list(answers) if answers is not None else None
    transcript = []
    # turn 0 = the question, turns 1..max_probes = probes, last turn = the closing line
    for turn in range(max_probes + 2):
        said = interviewer.say(messages)
        out(f"\nINTERVIEWER: {said}\n")
        messages.append({"role": "assistant", "content": said})
        transcript.append(("interviewer", said))
        if turn == max_probes + 1 or "that is all for this question" in said.lower():
            break
        if answers is not None:
            if not answers:
                break
            reply = answers.pop(0)
            out(f"YOU: {reply}")
        else:
            out("YOU (type your answer; finish with a line containing only /end, or type /done to stop):")
            lines = []
            while True:
                line = sys.stdin.readline()
                if not line or line.strip() == "/end":
                    break
                if line.strip() == "/done":
                    lines = ["/done"]
                    break
                lines.append(line.rstrip("\n"))
            reply = "\n".join(lines).strip()
        if reply == "/done" or not reply:
            break
        messages.append({"role": "user", "content": reply})
        transcript.append(("candidate", reply))
    card = interviewer.scorecard(messages)
    out("\n=== SCORECARD ===\n" + card)
    return transcript, card


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", required=True)
    ap.add_argument("--rubric", default="Weak: buzzwords only. OK: correct but generic. Strong: specific, quantified, names a trade-off or failure mode.")
    ap.add_argument("--model", default="claude-sonnet-5-5")
    ap.add_argument("--effort", default="low", help='"" to omit')
    ap.add_argument("--probes", type=int, default=3)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--answers", help="file of answers separated by lines containing only ---")
    args = ap.parse_args()
    if args.mock:
        who = MockInterviewer(args.question)
    else:
        who = ClaudeInterviewer(
            INTERVIEWER.format(question=args.question, rubric=args.rubric, max_probes=args.probes),
            args.model, args.effort)
    run(who, read_answers(args.answers) if args.answers else None, args.probes)


if __name__ == "__main__":
    main()
