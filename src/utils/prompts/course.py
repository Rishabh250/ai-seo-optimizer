"""
Prompt templates for course content generation.
"""
from langchain.prompts import PromptTemplate


class CoursePrompt:
    """Course content generation prompt templates."""

    def __init__(self):
        COURSE_PROMPT = PromptTemplate(
            input_variables=[
                "college_name",
                "city", 
                "state",
                "courses",
            ],
            template="""
**Authentic Course Pattern Generation Prompt**

**Primary Instruction:**
Generate course information following exact content patterns that successfully bypass AI detection through authentic institutional content writing imperfections and natural information flow issues.

**College Data:**
- College Name: {college_name}
- City: {city}
- State: {state}
- Courses: {courses}

**STRICT REQUIREMENT: Do not use competitors name in the course information like Shiksha.com, Careers360, Collegedunia, etc.**
*Note: If any data is not available, remove it from the course information.*

**INSTRUCTION:** 
Don't add title like Overview, Summary, etc.**

**Mandatory Opening Formula for Course Content:**
*"[Institution Name] offers over [Number] courses at UG, PG, and PhD levels in the streams of [Streams]. [Program] is the flagship course of [Institution] offered based on [Exam] scores. Besides, [Institution] also offers [additional programs] like [examples]."*

**Critical Content Patterns (MANDATORY):**

**1. Statistical Integration Style:**
- Include multiple ranking mentions: *"[Number]th by [Source 1] and [Number]th by [Source 2]"*
- Add collaboration numbers: *"[Number]+ tie-ups with renowned universities"*
- Embed course numbers naturally: *"offers over [Number] courses"*, *"in [Number] streams"*, *"[Number]+ specializations"*
- Use exact course counts: *"[Institution] provides [Number] UG courses, [Number] PG courses, and [Number] PhD programs"*

**2. Institution Name Repetition (AUTHENTIC PATTERN):**
- Use full institution name **6-8 times** throughout short content
- Mix variations: *"[Full Name]"*, *"[Acronym]"*, *"[Short Name]"*
- Include parenthetical clarifications: *"([Acronym] a part of [Parent Organization])"*
- Repeat institution name even when it feels redundant
- Include program-specific references: *"[Program] at [Institution]"*

**3. Authentic Information Flow Issues:**
- **Topic jumping:** Move between rankings, programs, facilities without smooth transitions
- **Information clustering:** Group related statistics together abruptly
- **Awkward transitions:** Use phrases like *"Further, [Institution] provides..."*
- **Incomplete context:** Add parenthetical information that feels casually inserted
- Move between UG, PG, PhD, certificates without smooth transitions

**4. Authority Validation Redundancy:**
- Mix promotional language with factual limitations
- Repeat course approval information in different contexts

**5. Natural Content Imperfections (ESSENTIAL):**
- **Mixed terminology:** Alternate between *"college,"* *"institute,"* *"university"*, *"courses,"* *"programs,"* *"degrees"*
- **Redundant information:** Mention placement assistance multiple ways, flagship courses multiple ways

**Required Content Structure:** (ONLY 1 PARAGRAPH)

**Paragraph 1: Courses**
*"{college_name} offers over [Number] courses at UG, PG, and PhD levels in the streams of [Streams]. [Program] is the flagship course of {college_name} offered based on [Exam] scores. Besides, {college_name} also offers [additional programs] like [examples]."*

**Paragraph 2: More about {college_name}**
*"Students can choose from flagship programmes such as [B.Tech/M.Tech/MS/BA/MBBS/ etc.] along with other specialised courses. With experienced faculty and updated curricula, {college_name} ensures students are well-prepared in their courses."*

**Paragraph 3: Admission Criteria for programs at {college_name}**
*"At {college_name}, admission to each program is based on a combination of academic merit, relevant qualifications, and program-specific requirements. While criteria may vary depending on the level and type of program, applicants can generally expect to meet following criteria*

**UG Programs** (IF UG programs are available, otherwise remove this section)
- **Eligibility:** Completion of high school or an equivalent qualification.
- **Minimum Academic Requirement:** A minimum of [Percentage/Grade] in high school, subject to program specific criteria.
- **Entrance Exams:** Some programs may require an entrance exam. Specific details will be provided per program.
- **Documents:** Transcripts, mark sheets, a motivation letter, and letters of recommendation if applicable.

**PG Programs** (IF PG programs are available, otherwise remove this section)
- **Eligibility:** A recognized UG degree in a relevant field.
- **Minimum Academic Requirement:** A minimum [CGPA/Percentage] in the UG degree, subject to specific program requirements.
- **Entrance Exams:** Some programs may require standardized tests such as [Entrance exam 1] or [Entrance exam 2].
- **Documents:** Academic transcripts, a statement of purpose, resume, and letters of recommendation.

**PhD Programs** (IF PhD programs are available, otherwise remove this section)
- **Eligibility:** A Master's degree in a relevant field.
- **Minimum Academic Requirement:** A minimum of [CGPA/Percentage] in the Master's program, with a preference for applicants with research experience.
- **Research Proposal:** A research proposal outlining your intended research area, subject to faculty approval.
- **Entrance Exams/Interviews:** Some programs may require an entrance exam and interview.
- **Documents:** Academic transcripts, research proposal, and letters of recommendation."

**Authentic Language Patterns:**

**Program Description Patterns:**
- "focuses on *[area 1]*, *[area 2]*, & *[area 3]*"
- "*flagship courses*" terminology
- "across [field] and various other streams"

**Content Quality Control Requirements:**

***Natural Imperfection Checklist:***
- Institution name repeated **2-4 times**
- Mixed terminology (*college/institute/university/courses/programs/degrees*)
- Awkward transitions between topics
- Statistical clustering without smooth flow
- Natural number integration without formatting
- Multiple ranking mentions
- Redundant information presentation
- Parenthetical clarifications included

***Authentic Flow Issues (REQUIRED):***
- Abrupt topic changes between paragraphs
- Information presented in **institutional content writer style** (not polished narrative)
- Natural redundancy in key information
- Specific but awkwardly phrased details
- Mixed promotional and limitation language

**Output Requirements:**
- Length: **200-300 words** for comprehensive coverage
- Format: **Rich text output with bold, italic and styling that humans usually add**
- Institution Naming: **2-4 repetitions** throughout content
- Information Density: Varied with natural clustering
- Authenticity Level: *Institutional content writer style*, not AI-polished

***Final Verification:***
Content must read like authentic institutional course marketing content with natural imperfections, redundancies, and flow issues that characterize real human-written educational content rather than AI-generated polished text.

**OUTPUT FORMAT REQUIREMENTS:**
- Generate content in **rich text format with human-like styling**
- **USE bold, italic and other formatting** that humans naturally add
- Natural integration of *numbers* and **statistics**
- **Well-formatted, styled text output**
"""
        )

        self.course_prompt = COURSE_PROMPT
