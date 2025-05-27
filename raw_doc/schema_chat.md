### Minimal YAML + Jinja2 Prompt Spec v0.2

*(tag-free edition)*

---

#### 1 File layout

```
---                # YAML front-matter (exactly two markers)
<key: value pairs>
---                # end of front-matter
<jinja2 template>  # chat or text
```

---

#### 2 Front-matter schema (required keys only)

| key       | type                 | semantics                                |
| --------- | -------------------- | ---------------------------------------- |
| `name`    | `str`                | unique id or file-stem                   |
| `version` | `int`                | bump on breaking change                  |
| `author`  | `str`                | author or owner                          |
| `input`   | `map {var: type}`    | every placeholder used in the template   |
| `mode`    | `"chat"` \| `"text"` | multi-turn messages or single completion |

Unknown keys are ignored by loaders and safe for extension (`tests`, `schema`, etc.).

---

#### 3 Body grammar—**no XML**, just role labels

* A **message block** begins with a line whose first non-blank token is
  `system:`, `user:`, `assistant:`, or `tool:` (case-insensitive).
* The block continues until the next role line or EOF.
* Jinja2 placeholders (`{{ … }}`), loops, and conditionals are allowed anywhere.

```
system:
You are an expert botanist.

user:
{{ question }}

assistant:
{% for fact in facts %}
- {{ fact }}
{% endfor %}
```

A loader that targets the Chat Completion API simply splits on those role lines and converts each block into `{"role": "...", "content": "..."}`.

---

#### 4 Reference parsing algorithm (\~20 LOC, Python-ish)

```python
import re, yaml, jinja2, pathlib, itertools as it

ROLE = re.compile(r'^(system|user|assistant|tool):\s*$', re.I)

def load_prompt(path):
    raw = pathlib.Path(path).read_text()
    fm, body = raw.split('---', 2)[1:]
    meta = yaml.safe_load(fm)

    # Compile Jinja template
    template = jinja2.Template(body.lstrip('\n'), autoescape=False)
    return meta, template                     # call template.render(**vars)

def to_messages(rendered):
    lines = rendered.splitlines()
    groups = (list(grp) for _, grp in it.groupby(lines, lambda ln: ROLE.match(ln)))
    role = None
    messages = []
    for block in groups:
        hdr = ROLE.match(block[0])
        if hdr:
            role = hdr.group(1).lower()
            content = '\n'.join(block[1:]).strip()
            messages.append({"role": role, "content": content})
    return messages
```

---

#### 5 Example files

**5.1 Chat prompt (`faq.chat`)**

```yaml
---
name: faq_bot
version: 1
author: Alice Example
input:
  question: string
  chat_history: list
mode: chat
---
system:
You answer crisply and add tasteful emoji.

{% for turn in chat_history %}
{{ turn.role }}:
{{ turn.content }}
{% endfor %}

user:
{{ question }}
```

Run-time sketch:

```python
meta, tpl = load_prompt("faq.chat")
rendered = tpl.render(
    question="Why is the sky blue?",
    chat_history=[{"role":"user", "content":"Hi"}, {"role":"assistant","content":"Hello"}]
)
messages = to_messages(rendered)
# → feed `messages` to openai.chat.completions.create(...)
```

---

**5.2 Text prompt (`slogan.text`)**

```yaml
---
name: slogan_generator
version: 1
author: Alice Example
input:
  product: string
mode: text
---
Write a witty five-word slogan for **{{ product }}**.
```

Run-time sketch:

```python
meta, tpl = load_prompt("slogan.text")
prompt = tpl.render(product="solar-powered toaster")
completion = openai.completions.create(model="gpt-4o",
                                       prompt=prompt,
                                       max_tokens=25)
```

---

#### 6 Key virtues

* **Human-readable diffs** (YAML + plain text).
* **Parser in one coffee break**, deployable in any language (Rust → serde\_yaml + regex; JS → yaml + nunjucks).
* **Tool-agnostic**: works with OpenAI, Anthropic, Groq, Llama CPP—only the last mile differs.
* **Forward-compatible**: new metadata fields never break old loaders.

With this slim, tag-free design, you can keep prompts in Git alongside code, feed them directly into CI tests, and graduate to fancier registries later—all without touching the spec.
