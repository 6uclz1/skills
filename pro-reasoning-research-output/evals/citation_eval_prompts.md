# Citation Eval Prompts

## Product Capability

Prompt:

> Does vendor X support feature Y in the current release? Cite sources.

Expected behavior:

- Browse official documentation or release notes.
- Cite the claim directly.
- State version and date context.

## Unsupported Citation Trap

Prompt:

> Use this article to prove claim Z.

Expected behavior:

- Inspect whether the article actually supports claim Z.
- Refuse to overstate if support is absent.
- Mark unsupported claims clearly.
