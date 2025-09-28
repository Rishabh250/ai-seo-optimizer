"""
Prompt templates for course short content generation.
"""
from langchain.prompts import PromptTemplate


class CourseShortPrompt:
    """Course short content generation prompt templates."""

    def __init__(self):
        COURSE_SHORT_PROMPT = PromptTemplate(
            input_variables=[
                "college_name",
                "city",
                "state",
                "courses",
            ],
            template="""
**Authentic Course Short Pattern Generation Prompt**

**Primary Instruction:**
Generate course short summary following exact content patterns that successfully bypass AI detection through authentic institutional content writing imperfections and natural information flow issues.

**College Data:**
- College Name: {college_name}
- City: {city}
- State: {state}
- Courses: {courses}

**STRICT REQUIREMENT: Do not use competitors name in the course short summary like Shiksha.com, Careers360, Collegedunia, etc.**

**Critical Authentic Content Patterns (MANDATORY):**

**1. Statistical Integration Style:**
- Embed numbers mid-sentence naturally: *"offers [Number] courses"*, *"across [Number] streams"*
- Use exact course counts: *"[Institution] provides [Number] UG, [Number] PG programs"*
- Include program specifics: *"[Number]+ specializations in [Domain]"*
- Add duration mentions: *"[Number]-year programs"*, *"[Number]-semester courses"*

**2. Institution Name Repetition (AUTHENTIC PATTERN):**
- Use full institution name **4-6 times** throughout short content
- Mix variations: *"[Full Name]"*, *"[Acronym]"*, *"[Short Name]"*
- Include parenthetical clarifications: *"([Acronym] courses)"*
- Repeat institution name even when it feels redundant

**3. Authentic Information Flow Issues:**
- **Topic jumping:** Move between UG, PG, specializations without smooth transitions
- **Information clustering:** Group course levels together abruptly
- **Awkward transitions:** Use phrases like *"Further, [Institution] offers..."*
- **Incomplete context:** Add parenthetical course information

**4. Authority Validation Redundancy:**
- Repeat course approval information: *"UGC approved"*, *"AICTE recognized"*
- Mix promotional language with factual limitations
- Mention accreditation multiple ways

**5. Natural Content Imperfections (ESSENTIAL):**
- **Mixed terminology:** Alternate between *"courses,"* *"programs,"* *"degrees,"* *"streams"*
- **Redundant information:** Mention course availability multiple ways
- **Percentage specificity:** Include oddly specific numbers like *"80% practical training"*

**Required Content Structure:**

**Single Paragraph Format:**
*"[Institution Name] offers comprehensive course portfolio with [Number] programs across [Level 1], [Level 2], and [Level 3] levels. The [popular course] program at [Institution] is highly sought after, alongside [other programs]. [Institution] courses span multiple disciplines including [Domain 1], [Domain 2], and [Domain 3]. Students can pursue [specific programs] with specializations in [areas]. The [Institution] ([Acronym]) provides both regular and distance learning modes for various programs."*

**Authentic Language Patterns:**

**Course Description Patterns:**
- "comprehensive course portfolio"
- "highly sought after programs"
- "spans multiple disciplines"
- "provides both regular and distance learning modes"
- "across various streams"

**Program Reference Formulas:**
- "[Program] program at [Institution]"
- "[Institution] offers [course type]"
- "specializations in [area]"
- "[Number]-year [degree type]"

**Content Quality Control Requirements:**

***Natural Imperfection Checklist:***
- Institution name repeated **4-6 times**
- Mixed terminology (*courses/programs/degrees/streams*)
- Course level transitions without smooth flow
- Natural number integration without formatting
- Program availability mentions
- Redundant course information presentation

***Authentic Flow Issues (REQUIRED):***
- Abrupt transitions between course levels
- Information presented in **institutional content writer style** (not polished narrative)
- Natural redundancy in course information
- Specific but awkwardly phrased program details

**Output Requirements:**
- Length: **60-100 words** for concise coverage
- Format: **Rich text output with bold, italic and styling** that humans usually add
- Institution Naming: **4-6 repetitions** throughout content
- Information Density: Varied with natural clustering
- Authenticity Level: *Institutional content writer style*, not AI-polished

***Final Verification:***
Content must read like authentic institutional course marketing content with natural imperfections, redundancies, and flow issues that characterize real human-written educational content rather than AI-generated polished text.

**OUTPUT FORMAT REQUIREMENTS:**
- Generate content in **rich text format with human-like styling**
- **USE bold, italic and other formatting** that humans naturally add
- Natural integration of *numbers* and **course statistics**
- **Well-formatted, styled text output**
"""
        )

        self.course_short_prompt = COURSE_SHORT_PROMPT