---
name: resolve-pr-comments
description: Work through every review comment on a PR — verify, fix or decline, reply, resolve. Use when a PR has review feedback to address.
---

The PR is the one the user names, else the current branch's (`gh pr view --json number,url,headRefName`). Work on its head branch; if the checkout is on another branch, stop and ask.

## 1. Build the ledger

The **ledger** is every comment still waiting on an answer, one row each. Gather from all three places a comment can live:

- **Review threads** — unresolved ones only:

  ```bash
  gh api graphql -F owner=<owner> -F repo=<repo> -F pr=<number> -f query='
    query($owner:String!,$repo:String!,$pr:Int!){repository(owner:$owner,name:$repo){pullRequest(number:$pr){
      reviewThreads(first:100){nodes{id isResolved isOutdated path line
        comments(first:50){nodes{author{login} body url}}}}}}}'
  ```

- **Review bodies** — `gh api --paginate repos/<owner>/<repo>/pulls/<number>/reviews`, the ones with a non-empty body.
- **PR conversation** — `gh api --paginate repos/<owner>/<repo>/issues/<number>/comments`: human comments, plus bot comments (CI results, automated reviews) that raise an issue.

Review bodies and conversation comments have no resolved state, so step 4's answer comment links each one it answers. Drop every comment whose URL already appears in a PR comment you posted, and your own comments.

Done when every source is read and each row carries its thread `id` (or comment URL), file and line, and the ask in one sentence.

## 2. Verdict each row

Check the reviewer's claim against the real thing before agreeing — run the query, read the code, compile. Then give each row one verdict:

- **fix** — the claim holds and the change is in scope.
- **decline** — the claim is wrong, or the change belongs elsewhere; carry the evidence (the query result, the line of code).

Where the call is the user's — two reasonable fixes give different behaviour, or the fix widens the PR's scope — put those rows to the user as one numbered list, wait, and turn each answer into fix or decline.

Done when every row is fix or decline.

## 3. Fix and push

Make the **fix** rows, run the repo's checks until they pass, commit and push. Done when every **fix** row maps to a pushed commit.

## 4. Reply and resolve

Answer every row where it lives, in a line or two: a **fix** with its commit (`Fixed in <sha>: <what changed>`), a **decline** with the reason and its evidence. Then resolve the thread, whichever the verdict.

```bash
gh api graphql -F id=<thread id> -f body='<reply>' -f query='
  mutation($id:ID!,$body:String!){addPullRequestReviewThreadReply(input:{pullRequestReviewThreadId:$id,body:$body}){comment{url}}}'
gh api graphql -F id=<thread id> -f query='
  mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{isResolved}}}'
```

Rows from review bodies and the PR conversation have no thread: answer them all in one PR comment (`gh pr comment`), one bullet per row, linking the comment's URL.

Comments that land after the push (CI, bot review) start a fresh ledger at step 1.

Done when every row has a reply and every thread is resolved.
