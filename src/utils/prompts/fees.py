"""
Prompt templates for fees content generation.
"""
from langchain.prompts import PromptTemplate


class FeesPrompt:
    """Fees content generation prompt templates."""

    def __init__(self):
        FEES_PROMPT = PromptTemplate(
            input_variables=[
                "college_name",
                "degree_name",
            ],
            template="""
**Shiksha.com Authentic Fees Content Generation**

**Primary Instruction:**
Generate fees information following Shiksha.com's exact content patterns that successfully bypass AI detection through authentic institutional content writing imperfections and natural information flow issues.

**College Data:**
- College Name: {college_name}
- Degree/Program: {degree_name}

**Critical Shiksha.com Content Patterns (MANDATORY):**

**1. Statistical Integration Style:**
- Embed numbers mid-sentence naturally: *"established in [Year]"*, *"ranked [Number]th"*
- Use exact ranking formula: *"The [institution] has been ranked [Number]th by [Source] [Year] under the [Category] category"*
- Include multiple ranking mentions: *"[Number]th by [Source 1] and [Number]th by [Source 2]"*
- Add collaboration numbers: *"[Number]+ tie-ups with renowned universities"*
- Embed fee ranges naturally: *"ranges from INR [Amount] to INR [Amount]"*, *"starts from INR [Amount]"*
- Use exact fee amounts: *"INR [Amount] per semester"*, *"INR [Amount] annually"*

**2. Institution Name Repetition (AUTHENTIC PATTERN):**
- Use full institution name **6-8 times** throughout short content
- Mix variations: *"[Full Name]"*, *"[Acronym]"*, *"[Short Name]"*
- Include parenthetical clarifications: *"([Acronym] a part of [Parent Organization])"*
- Repeat institution name even when it feels redundant
- Include fee-specific references: *"fees at [Institution]"*, *"[Institution] fee structure"*

**3. Authentic Information Flow Issues:**
- **Topic jumping:** Move between rankings, programs, facilities without smooth transitions
- **Information clustering:** Group related statistics together abruptly
- **Awkward transitions:** Use phrases like *"Further, [Institution] provides..."*
- **Incomplete context:** Add parenthetical information that feels casually inserted

**4. Authority Validation Redundancy:**
- Scatter multiple accreditation mentions: *"recognised by AICTE, UGC, and [Regional Body]"*
- Repeat ranking information in different contexts
- Mix promotional language with factual limitations
- Include recognition statements: *"recognized as one of the Top [Category] in [Survey Year]"*
- Scatter multiple fee policy mentions: *"as per [Authority] guidelines"*

**5. Natural Content Imperfections (ESSENTIAL):**
- **Mixed terminology:** Alternate between *"college,"* *"institute,"* *"university"*, *"fees,"* *"tuition,"* *"charges"*
- **Redundant information:** Mention placement assistance multiple ways
- **Percentage specificity:** Include oddly specific numbers like *"70% practical exposure and 30% theoretical"*
- **Statistical awkwardness:** *"50+ guidance sessions"*, *"36+ online talks"*, *"INR [Amount]+ total fees"*

**Required Content Structure: (Maximum 1 paragraph)**

**Paragraph 1: Fees + Accreditation**
*"{college_name} offers various fee structures for different programs. These fees are provided across [departments]. {college_name} has been recognised by the [Bodies]. {college_name} provides {degree_name} programmes with fee structure in affiliation with [university]. Further, {college_name} provides [programs] as flagship courses and focuses on [areas]. The institute offers [percentage]% practical exposure and [percentage]% theoretical exposure to the students."*

**Authentic Language Patterns:**

**Promotional Mixed with Factual:**
- *"reputed [institution] is a non-[comparison] member"*

**Recognition Formulas:**
- "recognized as one of the **Top [Category] of Eminence** in [Survey]"

**Content Quality Control Requirements:**

***Natural Imperfection Checklist:***
- Institution name repeated **2-4 times**
- Mixed terminology (*college/institute/university/fees/tuition/charges*)
- Awkward transitions between topics
- Statistical clustering without smooth flow
- Natural number integration without formatting
- Redundant information presentation
- Parenthetical clarifications included

***Authentic Flow Issues (REQUIRED):***
- Information presented in **institutional content writer style** (not polished narrative)
- Natural redundancy in key information
- Specific but awkwardly phrased details
- Mixed promotional and limitation language

**Output Requirements:**
- Length: **60-100 words** for comprehensive coverage
- Format: **Rich text output with bold, italic and styling** that humans usually add
- Institution Naming: **1-3 repetitions** throughout content
- Information Density: Varied with natural clustering
- Authenticity Level: *Institutional content writer style*, not AI-polished

***Final Verification:***
Content must read like authentic institutional fees marketing content with natural imperfections, redundancies, and flow issues that characterize real human-written educational content rather than AI-generated polished text.

**OUTPUT FORMAT REQUIREMENTS:**
- Generate content in **rich text format with human-like styling**
- **USE bold, italic and other formatting** that humans naturally add
- Natural integration of *numbers* and **statistics**
- **Well-formatted, styled text output**
"""
        )

        self.fees_prompt = FEES_PROMPT
