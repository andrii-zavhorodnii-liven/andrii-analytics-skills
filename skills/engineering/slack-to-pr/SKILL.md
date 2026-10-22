---
name: slack-to-pr
description: Turn a Slack message into a PR — read the thread, ask in the thread only if needed, build the change, open a PR, ping the user for review in the thread.
disable-model-invocation: true
---

The user hands you a link to a Slack message, often with little or no description. The **thread** under that message is the task, and the channel you talk to people in. Your job ends at an open PR and a review ping; the review is the user's.

Every message you post goes in that thread (a reply, never a new channel message), written in the language of the linked message: a Ukrainian message gets Ukrainian replies.

## 1. Read the thread

Read the message and every reply under it through the Slack connector's tools; they may be deferred, so search the deferred tools for Slack before deciding they're missing. If no Slack tools turn up, ask the user to paste the message text in chat, and run the rest of this skill in chat instead of the thread (step 5 then becomes telling the user the PR link).

Done when you can state the ask in one sentence, plus who wrote it.

## 2. Dig, then ask only what digging can't answer

Look before you ask: find the tables, models, files and numbers the thread names, in this repo and its data, the way the repo's own `CLAUDE.md` and skills say to.

Ask in the thread only when one of these holds:

- two reasonable readings of the ask would produce **different PRs**, or
- a fact the change needs (a threshold, a date, which of two tables) is nowhere in code, data or the thread.

Post all questions as one reply, numbered, each answerable in a line. In chat mode (step 1's fallback), ask in chat and end your turn. In the thread, keep the reply's `ts` and **watch** for answers:

1. Schedule a recurring check with CronCreate (it may be deferred; search the deferred tools for it), cron `*/5 * * * *`. Write its prompt out in full, with the thread link, channel id, thread ts and question ts filled in: read the thread with `oldest` set to the question's `ts`; with no reply newer than the question, end the turn with no output; with one, follow slack-to-pr step 2's **On resume** for that thread, then steps 3–5 (build the change, open the PR, ping for review). If the slack-to-pr skill text is no longer in context, tell the user a reply came in and ask them to re-run `/slack-to-pr <thread link>`.
2. End your turn, telling the user in chat that the questions are in the thread, that you check it every 5 minutes for up to 7 days while this session stays open, and that they can also tell you directly once it's answered.

**On resume**, from the watch or the user: CronDelete the watch job if it's still in CronList, re-read the whole thread, and go on. Every question still unanswered becomes an assumption.

Everything else you'd like to ask becomes an **assumption**: decide it yourself and carry it to the PR body.

## 3. Build the change

Branch off the default branch (never commit on it), then make the change following the repo's own conventions and skills.

Done when every point in the thread is either in the diff or named in the PR as left out, with the reason.

## 4. Open the PR

Push and open the PR with `gh pr create`. Call the Skill tool with "pr" for the body, and add to it:

- the Slack thread link,
- an **Assumptions** list: every decision from step 2 you made without asking,
- a **Left out** list: every point from the thread not in the diff, with the reason.

If the repo's `CLAUDE.md` names after-push checks (CI comments, bot reviews), run them now.

## 5. Ping for review

Reply in the thread: one line with the PR link, @-mentioning the user and asking them to review. The user is the person running this session, not necessarily the message's author: find their Slack account by their email (the session's user email, else `git config user.email`), and mention @Andrii Zavhorodnii if no account matches. Then tell the user in chat the same PR link.
