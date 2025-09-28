from langchain.prompts import PromptTemplate


class OverviewShortSummaryPrompt:
    def __init__(self):
        OVERVIEW_SHORT_SUMMARY_PROMPT = PromptTemplate(
            input_variables=[
                "college_name",
                "city", 
                "state",
                "establishment_year",
                "campus_area",
                "total_students",
                "faculty_members",
                "faculty_student_ratio", 
                "total_courses",
                "departments",
                "raw_data",
                "ranking_data",
                "courses"
            ],
            template="""
**Authentic Pattern Generation Prompt**

**Primary Instruction:**
Generate college short summary of the overview following exact content patterns that successfully bypass AI detection through authentic institutional content writing imperfections and natural information flow issues.

**College Data:**
- College Name: {college_name}
- City: {city}
- State: {state}
- Establishment Year: {establishment_year}
- Campus Area: {campus_area}
- Total Students: {total_students}
- Faculty Members: {faculty_members}
- Faculty Student Ratio: {faculty_student_ratio}
- Total Courses: {total_courses}
- Departments: {departments}
- Courses Data: {courses} (use it for courses information, and if not available, remove it from the short summary)
- Ranking Data: {ranking_data} (use it for ranking information, and if not available, remove it from the short summary)
- Raw Data: {raw_data} (that it as a reference for the short summary)

**CONTENT REFERENCE:** USE College Data to generate the short summary of the overview (mainly use key data points from the raw data and college data), and if any data is not available, remove it from the short summary.

**STRICT REQUIREMENT: Do not use competitors name in the short summary like Shiksha.com, Careers360, Collegedunia, etc.**

**Critical Authentic Content Patterns (MANDATORY):**

**1. Statistical Integration Style:**
- Embed numbers mid-sentence naturally: *"established in [Year]"*, *"ranked [Number]th"*
- Use exact ranking formula: *"The [institution] has been ranked [Number]th by [Source] [Year] under the [Category] category"*
- Include multiple ranking mentions: *"[Number]th by [Source 1] and [Number]th by [Source 2]"*
- Add collaboration numbers: *"[Number]+ tie-ups with renowned universities"*

**2. Institution Name Repetition (AUTHENTIC PATTERN):**
- Use full institution name **6-8 times** throughout short content
- Mix variations: *"[Full Name]"*, *"[Acronym]"*, *"[Short Name]"*
- Include parenthetical clarifications: *"([Acronym] a part of [Parent Organization])"*
- Repeat institution name even when it feels redundant

**3. Authentic Information Flow Issues:**
- **Topic jumping:** Move between rankings, programs, facilities without smooth transitions
- **Information clustering:** Group related statistics together abruptly
- **Awkward transitions:** Use phrases like *"Further, [Institution] provides..."*
- **Incomplete context:** Add parenthetical information that feels casually inserted

**4. Authority Validation Redundancy:**
- Scatter multiple accreditation mentions: *"recognised by AICTE, UGC, and [Regional Body]"*
- Repeat ranking information in different contexts
- Mix promotional language with factual limitations

**5. Natural Content Imperfections (ESSENTIAL):**
- **Mixed terminology:** Alternate between *"college,"* *"institute,"* *"university"*
- **Redundant information:** Mention placement assistance multiple ways

**Required Content Structure:** (ONLY 1 PARAGRAPH)

**Paragraph 1: Basic Information + Rankings + Courses**
**{college_name}** is a distinguished [college_type] established in [Establishment Year] in **{city}, {state}**. The **{college_name}** offers a total of **{total_courses}** courses across various disciplines, a non-private college member. **[college_acronym]** is renowned; the *institute* has **{total_students}** students enrolled in various programs including **Engineering** and other specialized fields across its departments. This top-ranked premium institute (**{college_name}**) operates through more than **{departments}** specialized departments with over **{faculty_members}** faculty members. **[college_acronym]** is committed to academic excellence and is recognized by appropriate regulatory bodies (often referred to as a premier *college*).

**Authentic Language Patterns:**

**Promotional Mixed with Factual:**
- "**top ranked premium** [institution type]"
- "reputed [institution] is a **non-[comparison]** member"
- "one of the **top-ranked [category]** institutes"

**Recognition Formulas:**
- "securing the **[position]** among [category]"
- "has been ranked **[number]th** by [source]"

**Program Description Patterns:**
- "focuses on *[area 1]*, *[area 2]*, & *[area 3]*"
- "offers **[percentage]% practical exposure** and **[percentage]% theoretical exposure**"
- "**flagship courses**" terminology
- "across *[field]* and various other streams"

**Content Quality Control Requirements:**

***Natural Imperfection Checklist:***
- Institution name repeated **6+ times**
- Mixed terminology (*college/institute/university*)
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
- Length: **80-120 words** for comprehensive coverage
- Format: **Rich text output with bold, italic and styling** that humans usually add
- Institution Naming: **6-8 repetitions** throughout content
- Information Density: Varied with natural clustering
- Authenticity Level: *Institutional content writer style*, not AI-polished

***Final Verification:***
Content must read like authentic institutional marketing content with natural imperfections, redundancies, and flow issues that characterize real human-written educational content rather than AI-generated polished text.

**OUTPUT FORMAT REQUIREMENTS:**
- Generate content in **rich text format with human-like styling**
- **USE bold, italic and other formatting** that humans naturally add
- Natural integration of *numbers* and **statistics**
- **Well-formatted, styled text output**
"""
        )

        self.overview_short_summary_prompt = OVERVIEW_SHORT_SUMMARY_PROMPT