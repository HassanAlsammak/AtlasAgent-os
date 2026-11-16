# Atlas Local Memory (experimental)

A small SQLite-backed note store for **explicitly saved** agent memory.
No cloud account, vector database, or model API is required.

## Example

```python
from atlasagent.memory import LocalMemory

with LocalMemory("atlas-notes.sqlite3") as memory:
    note_id = memory.add("my-project", "Use tests before merging")
    print(memory.search("my-project", "tests"))
    memory.delete("my-project", note_id)
```

The namespace argument separates logical collections, but it is **not an
authorization boundary**. Anyone with access to the database can read its
contents. Do not store credentials, API keys, or sensitive personal information.

Search is case-insensitive literal substring matching, **not semantic retrieval**.
Entries are returned newest first, with a maximum query limit of 100. The API
supports explicit deletion, but SQLite deletion does not guarantee secure
erasure from database pages, backups, or storage media.

The memory store is not automatically wired into the Runner: this avoids
silently retaining prompts or task outputs. Integrations should request
consent before persisting user data, treat retrieved notes as untrusted
context, and enforce permissions outside this module.
