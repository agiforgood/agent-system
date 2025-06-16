# 🎯 Task: Design Volunteer Assessment for Empathy Evaluation

_Priority: High | Time: 3-4 hours | Platform: Axiia App_

---

## 📋 What You Need to Do

**Goal**: Create an assessment to test if volunteers can write good empathy evaluation prompts.

**Why**: We need volunteers for P1-P4 prompt work, but first need to check if they understand empathy evaluation.

**Platform**: Assessment will be delivered through the **Axiia app**.

**Deliverable**: Complete assessment package ready to deploy on Axiia.

---

## ✅ Requirements

### Assessment Must:
- Test volunteers' ability to write empathy evaluation prompts
- Be completable in 30 minutes
- Identify volunteers whose prompts achieve ≥70% overlap with expert scores
- Work for people with no psychology background
- Be compatible with Axiia app interface
- Be reusable for other dimensions later

### Success Criteria:
- **Pass threshold**: ≥70% alignment with expert scores
- **Time limit**: 30 minutes maximum
- **Clear instructions**: No confusion about what to do
- **Objective scoring**: Easy to grade pass/fail
- **Axiia-ready**: Formatted for app deployment

---

## 📦 What to Create

### 1. Assessment Content for Axiia
Design assessment content that works in the Axiia app:
- **Task overview**: What volunteers need to do
- **Empathy definition**: 5-point scale with examples
- **Interactive instructions**: Step-by-step guidance within app
- **Success criteria**: How they pass/fail
- **App-friendly format**: Compatible with Axiia's interface

### 2. Sample Materials
Create test materials for Axiia platform:
- **5-8 conversations** between AI coaches and parents
- **Expert scores** (1-5) for each coach response
- **Mix of good/bad empathy** examples
- **Axiia-compatible format** for presenting conversations

### 3. Evaluation Guide
Instructions for graders using Axiia:
- **How to score** volunteer submissions through the app
- **Pass/fail criteria** within Axiia system
- **Common mistakes** to watch for
- **Axiia workflow** for assessment review

---

## 🎯 Empathy Framework

Use this definition:
- **Empathy**: AI coach accurately understands and responds to parent's emotions
- **Good empathy**: Recognizes feelings, validates emotions, shows understanding
- **Poor empathy**: Misses emotions, gives generic responses, dismissive

**Scale**: 1 (poor) to 5 (exceptional)

---

## 📋 Deliverables

Create assessment package following the **000501-thinking-traps** folder structure:

```
docs/000502-empathy-assessment/
├── problem.yml                    # Main Axiia configuration
├── materials/
│   ├── task.md                   # Assessment instructions
│   ├── initial-msg.j2            # Welcome message template
│   └── prefill.j2                # Response template
└── prompts/
    └── axiia.j2                  # Evaluation prompt template
```

### Required Files:

1. **`problem.yml`** - Axiia configuration with:
   - Assessment metadata and bot presets
   - Sample conversations with expert empathy scores
   - Submission requirements and evaluation criteria

2. **`materials/task.md`** - Assessment instructions including:
   - Empathy definition and 5-point scale
   - Task overview and requirements
   - Examples of good/poor empathy responses

3. **`materials/initial-msg.j2`** - Welcome message template
4. **`materials/prefill.j2`** - Response format template
5. **`prompts/axiia.j2`** - Evaluation prompt for scoring submissions

---

## 🔧 Design Tips

- **Keep it simple**: Volunteers should understand immediately
- **Make it app-friendly**: Consider Axiia's interface capabilities
- **Test on mobile**: Ensure works well on phone/tablet
- **Think scalability**: Can this approach work for other dimensions on Axiia?
- **Interactive design**: Leverage Axiia's interactive features

---

## 📎 Resources

**Reference these docs**:
- `background&motivation.md` - Project context
- `okr.md` - Goals O2, O3, O5 about evaluation
- `docs/VOLUNTEER_ASSESSMENT_Empathy_Eval.md` - Example structure

**Key constraints**: 
- Assessment must work without psychology background
- Must be compatible with Axiia app platform
- Should leverage Axiia's interactive capabilities

---

_Create an assessment that efficiently identifies volunteers ready for prompt development work through the Axiia platform._ 