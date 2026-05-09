# Threat Model

## Main Risks

- Prompt injection from video, audio, comments, descriptions, or fetched pages.
- Shell injection through URL or prompt interpolation.
- Secret leakage from Gemini, Codex, OAuth, or local config files.
- Arbitrary URL fetching or private network access.
- Mislabeling model-generated transcript output as official captions.
- Excessive cost or latency on long videos or repeated analysis.

## Controls

- Only accept YouTube hostnames: `youtube.com`, `www.youtube.com`, `m.youtube.com`, `youtu.be`, and `youtube-nocookie.com`.
- Only accept `/watch?v=`, `/shorts/`, `/embed/`, and `youtu.be/` video URL forms.
- Reject non-HTTP(S) schemes, credentials, ports, control characters, non-YouTube domains, and malformed video IDs.
- Call subprocesses with argument arrays and `shell=False`.
- Do not print environment variables, tokens, Gemini config paths, OAuth files, or raw command environments.
- Default `is_official_caption` to `false`.
- Keep `captions` mode unsupported until owner-authorized YouTube Data API OAuth is implemented.
- Use deterministic cache keys if cache writes are enabled: `sha256(video_id + mode + lang + model + prompt_version)`.
