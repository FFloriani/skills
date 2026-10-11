---
name: skillsmp-search
description: >-
  Search the SkillsMP marketplace (skillsmp.com) for community-built AI skills
  through its REST API. Use this whenever the user wants to find, search,
  discover, browse, or look up AI skills / agent skills — by keyword, category
  (e.g. data-ai, devops), occupation (SOC slug), or content language — even if
  they don't name "SkillsMP" or "the marketplace" explicitly. Trigger it for
  requests like "is there a skill for X?", "find me skills about SEO",
  "what are the newest/most popular skills for data engineering", "show skills
  for software developers in Chinese", or any request to compare or explore
  what AI skills already exist before building one from scratch.
---

# SkillsMP Search

Query the SkillsMP marketplace (https://skillsmp.com), a directory of
community-built AI skills, through its public REST API. This skill is
**read-only**: it searches and returns results, it never creates, edits, or
publishes skills.

## When to use this

Reach for this skill any time the user is trying to **discover existing AI
skills** instead of writing one from scratch. The API exposes a single search
endpoint, so the whole job is: turn the user's intent into a good query plus
filters, call the endpoint, and present the results clearly.

## API key

Requests need a SkillsMP API key, sent as a Bearer token. The bundled script
reads it from, in order:

1. the `SKILLSMP_API_KEY` environment variable;
2. the file `~/.config/skillsmp/key` (just the key, on one line).

If neither exists, the script stops with a message. Tell the user to create a
key on skillsmp.com and save it in one of those two places. Never print the
key in chat, never send it to any host other than `skillsmp.com`, and never put
it in a URL query string: it goes only in the `Authorization` header.

## The endpoint

```
GET https://skillsmp.com/api/v1/skills/search
```

| Parameter    | Type   | Required | Notes |
|--------------|--------|----------|-------|
| `q`          | string | yes      | Search query. Wildcards (`*`) are **not** supported. |
| `page`       | number | no       | Default `1`. |
| `limit`      | number | no       | Default `20`, maximum `50`. |
| `sortBy`     | string | no       | `stars` (most popular, default) or `recent` (newest). |
| `category`   | string | no       | Category slug, e.g. `data-ai`, `devops`. |
| `occupation` | string | no       | SOC occupation slug, e.g. `software-developers`. |
| `language`   | string | no       | ISO code of the skill's detected content language (`en`, `zh`, `ja`, …); `mul` = mixed-language, `und` = undetermined. |

Rate limits depend on the account (a free key had 500 requests/day and 30/min
when this skill was written). Responses may carry `X-RateLimit-Daily-Limit` and
`X-RateLimit-Daily-Remaining` headers; mention the remaining quota to the user
if it's getting low.

## How to run a search

1. **Bundled Python helper** (preferred: it finds the key for you):

   ```bash
   python "<skill-dir>/scripts/search.py" "SEO" --sort stars --limit 10
   ```

   Run `python "<skill-dir>/scripts/search.py" --help` to see every flag
   (`--category`, `--occupation`, `--language`, `--page`, `--json`).

2. **`curl`** when Python isn't available and the key is in the environment:

   ```bash
   curl -sS -G "https://skillsmp.com/api/v1/skills/search" \
     --data-urlencode "q=SEO" \
     --data-urlencode "sortBy=stars" \
     --data-urlencode "limit=10" \
     -H "Authorization: Bearer $SKILLSMP_API_KEY"
   ```

   Add `--data-urlencode "category=devops"`, `occupation=software-developers`,
   `language=en`, or `page=2` as the request needs them.

3. **WebFetch / native HTTP tool** if the agent has no shell: fetch the URL
   with the `Authorization` header set as above, with properly URL-encoded
   parameters.

## Turning intent into a query

- Extract the **core topic** for `q`: a few strong keywords, not a whole
  sentence. "find me something that helps write SQL for BigQuery" → `q=SQL BigQuery`.
  Single specific keywords (a tool or file name) work better than long phrases,
  which tend to fall back to generic popular results.
- Map obvious topic hints to filters: a job role → `occupation`; a domain like
  DevOps/data → `category`; "in Portuguese/Chinese/etc." → `language`.
- "newest", "latest", "recently added" → `sortBy=recent`. "best", "popular",
  "top" → `sortBy=stars` (the default).
- If the first query returns nothing useful, retry with broader or alternative
  keywords before telling the user there are no results. Don't stack too many
  filters at once: each one narrows the pool.

## Presenting results

Summarize, don't dump raw JSON (unless the user asks for JSON). For each skill
show at least its **name**, a one-line description, and its stars if present,
plus a link when the response includes one. Lead with the most relevant
handful. If the user is deciding whether to build vs. reuse, say plainly whether
a good match already exists.

The `stars` field is the star count of the GitHub **repository** the skill
lives in, not of the skill itself. Skills inside huge multi-purpose repos look
more popular than they are, and many are copies of official skills, so judge by
author, last update and the SKILL.md itself rather than by stars alone.

## Errors

The API returns standard HTTP codes with a JSON body
(`{ "success": false, "error": { "code", "message" } }`):

| Code                   | HTTP | What to do |
|------------------------|------|------------|
| `INVALID_API_KEY`      | 401  | The key is wrong or was regenerated: ask the user to update it in `SKILLSMP_API_KEY` or `~/.config/skillsmp/key`. |
| `MISSING_QUERY`        | 400  | You forgot `q`: always include it. |
| `INVALID_OCCUPATION`   | 400  | The occupation slug isn't recognized: drop or fix it. |
| `INVALID_LANGUAGE`     | 400  | The language code isn't recognized: use a valid ISO code. |
| `DAILY_QUOTA_EXCEEDED` | 429  | Out of daily requests: tell the user to try again tomorrow. |
| `INTERNAL_ERROR`       | 500  | Server-side: retry once, then report it. |

Report the failure honestly and, where the fix is the user's (bad key, quota),
say exactly what they need to do.
