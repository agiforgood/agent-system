# 📝 Volunteer Assessment: Empathy Evaluation Prompt Writing

_Assessment Type: Practical Exercise_  
_Focus: Empathy Dimension_  
_Target Roles: P1, P2, P3, P4 Prompt Development_

---

## 🎯 Assessment Overview

This assessment evaluates your ability to create effective prompts for evaluating **empathy** in AI coach conversations. You will write evaluation prompts and test them against expert-scored conversations to measure alignment.

**Goal**: Demonstrate that your evaluation prompts can achieve >70% overlap with expert empathy scores.

**Time Limit**: 2 hours

**Prerequisites**: None (this assessment determines readiness for prompt work)

---

## 📋 Assessment Task

### Your Mission
Write a prompt that can automatically evaluate the **empathy level** of an AI coach's responses in parent-coach conversations.

### What You'll Receive
1. **10 sample conversations** between AI coaches and parents
2. **Expert empathy scores** (1-5 scale) for each coach response
3. **Empathy definition and scoring criteria** (see below)

### What You Must Deliver
1. **One evaluation prompt** (500-1500 words) that can score empathy
2. **Your scores** (1-5) for all 10 conversations using your prompt
3. **Brief explanation** (200-300 words) of your prompt design rationale

---

## 🧠 Empathy Definition & Scoring Criteria

### Empathy in AI Coaching Context
**Empathy** is the AI coach's ability to accurately understand and respond to the parent's emotional state, feelings, and perspective without judgment.

### Scoring Scale (1-5)

**5 - Exceptional Empathy**
- Accurately identifies and reflects the parent's specific emotions
- Demonstrates deep understanding of the parent's perspective
- Responds with appropriate emotional tone and validation
- Shows genuine care and concern

**4 - Good Empathy**
- Recognizes the parent's emotional state
- Shows understanding of their situation
- Provides appropriate emotional support
- Minor gaps in emotional attunement

**3 - Adequate Empathy**
- Basic recognition of parent's feelings
- Some attempt at emotional validation
- Generally supportive but may miss nuances
- Functional but not deeply empathetic

**2 - Limited Empathy**
- Minimal acknowledgment of emotions
- Superficial or generic responses
- May misread emotional cues
- Lacks emotional depth or warmth

**1 - Poor Empathy**
- Fails to recognize parent's emotional state
- Dismissive or inappropriate responses
- No emotional validation or support
- May be harmful or insensitive

---

## 📊 Assessment Materials

### Sample Conversation Format
Each conversation will be provided in this format:

```
Conversation ID: CONV_001
Parent: [Parent's message expressing concern/emotion]
AI Coach: [Coach's response to be evaluated]
Expert Score: [Hidden during assessment]
```

### Your Evaluation Prompt Requirements

Your prompt should:
- **Input**: Parent message + AI Coach response
- **Output**: Empathy score (1-5) with brief justification
- **Be specific** about what constitutes each score level
- **Be consistent** across different conversation types
- **Be practical** for automated evaluation

### Example Prompt Structure (Optional Guide)
```
You are an expert evaluator of empathy in AI coaching conversations.

Task: Evaluate the empathy level of the AI coach's response.

Evaluation Criteria:
[Your criteria here]

Input Format:
Parent: [message]
AI Coach: [response]

Output Format:
Score: [1-5]
Justification: [brief explanation]
```

---

## ✅ Success Criteria

### Scoring Alignment
- **Pass**: ≥70% of your scores within ±1 point of expert scores
- **Strong Pass**: ≥80% alignment
- **Exceptional**: ≥90% alignment

### Prompt Quality
Your prompt will be evaluated on:
- **Clarity**: Clear instructions and criteria
- **Specificity**: Detailed empathy indicators
- **Consistency**: Reliable scoring framework
- **Practicality**: Usable for automated evaluation

### Explanation Quality
Your design rationale should demonstrate:
- Understanding of empathy in coaching context
- Thoughtful approach to evaluation criteria
- Awareness of potential challenges/edge cases

---

## 📝 Submission Format

### File Structure
```
assessment_submission_[your_name]/
├── empathy_eval_prompt.md          # Your evaluation prompt
├── conversation_scores.json        # Your scores for 10 conversations
└── design_rationale.md            # Your explanation
```

### conversation_scores.json Format
```json
{
  "CONV_001": {
    "score": 4,
    "justification": "Coach accurately identified parent's frustration and provided validating response..."
  },
  "CONV_002": {
    "score": 2,
    "justification": "Response was generic and missed the parent's underlying anxiety..."
  }
}
```

---

## 🚀 Next Steps After Assessment

### If You Pass
- **Immediate**: Access to prompt development tasks (P1-P4)
- **Training**: Introduction to project OKRs and evaluation framework
- **Assignment**: Specific prompt development or optimization tasks

### If You Don't Pass Initially
- **Feedback**: Detailed analysis of where your prompt differed from expert scores
- **Resources**: Additional empathy evaluation training materials
- **Retry**: Opportunity to retake with different conversation set

### Future Assessments
This is the first in a series of assessments covering:
- **Positive Attention** evaluation
- **Goal Alignment** evaluation  
- **Therapeutic Alliance** evaluation
- **Multi-dimensional** prompt writing

---

## 📞 Support & Questions

- **Technical Issues**: Contact assessment coordinator
- **Clarification Questions**: Allowed during first 30 minutes only
- **Submission Problems**: Email with timestamp for deadline extension

---

## 🔒 Assessment Integrity

- **Individual Work**: Complete assessment independently
- **No External Tools**: Use only provided materials and your reasoning
- **Time Tracking**: Honor the 2-hour time limit
- **Original Work**: Write your own prompt (no copying from existing sources)

---

_This assessment is designed to identify volunteers who can contribute effectively to our AI coaching evaluation system. Good luck!_ 