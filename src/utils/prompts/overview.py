from langchain.prompts import PromptTemplate


class OverviewPrompt:
    def __init__(self):
        OVERVIEW_PROMPT = PromptTemplate(
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
                "departments"
            ],
            template="""
Shiksha.com Authentic Pattern Generation Prompt

Primary Instruction:
Generate college summaries following Shiksha.com's exact content patterns that successfully bypass AI detection through authentic institutional content writing imperfections and natural information flow issues.

College Data:
College Name: {college_name}
City: {city}
State: {state}
Establishment Year: {establishment_year}
Campus Area: {campus_area}
Total Students: {total_students}
Faculty Members: {faculty_members}
Faculty Student Ratio: {faculty_student_ratio}
Total Courses: {total_courses}
Departments: {departments}

Note: Use the college data to generate the overview, and if any data is not available, remove it from the overview.

Critical Shiksha.com Content Patterns (MANDATORY):

1. Statistical Integration Style:
- Embed numbers mid-sentence naturally: "established in [Year]", "ranked [Number]th"
- Use exact ranking formula: "The [institution] has been ranked [Number]th by [Source] [Year] under the [Category] category"
- Include multiple ranking mentions: "[Number]th by [Source 1] and [Number]th by [Source 2]"
- Add collaboration numbers: "[Number]+ tie-ups with renowned universities"

2. Institution Name Repetition (AUTHENTIC PATTERN):
- Use full institution name 6-8 times throughout short content
- Mix variations: "[Full Name]", "[Acronym]", "[Short Name]"
- Include parenthetical clarifications: "([Acronym] a part of [Parent Organization])"
- Repeat institution name even when it feels redundant

3. Authentic Information Flow Issues:
- Topic jumping: Move between rankings, programs, facilities without smooth transitions
- Information clustering: Group related statistics together abruptly
- Awkward transitions: Use phrases like "Further, [Institution] provides..."
- Incomplete context: Add parenthetical information that feels casually inserted

4. Authority Validation Redundancy:
- Scatter multiple accreditation mentions: "recognised by AICTE, UGC, and [Regional Body]"
- Repeat ranking information in different contexts
- Mix promotional language with factual limitations
- Include recognition statements: "recognized as one of the Top [Category] in [Survey Year]"

5. Natural Content Imperfections (ESSENTIAL):
- Mixed terminology: Alternate between "college," "institute," "university"
- Redundant information: Mention placement assistance multiple ways
- Percentage specificity: Include oddly specific numbers like "70% practical exposure and 30% theoretical"
- Statistical awkwardness: "50+ guidance sessions", "36+ online talks"

Required Content Structure:

Paragraph 1: Basic Information + Rankings
"[Institution] was established in [Year] and is located in [City, State]. It is [promotional phrase]. The [institution] has been ranked [Number]th by [Source] [Year] under the [Category] category, and [Number]th by [Source] [Year] under the [Category] category. The college has [Number]+ tie-ups with [description] and provides [Percentage]% placement assistance to students."

Paragraph 2: Recognition + Programs
"[Institution Name] has been recognized as one of the [Achievement in Survey Year], securing the [Position] among [Category]. The institute is involved in various academic innovations, launching [specific programs/centers]."

Paragraph 3: Courses + Accreditation
"[Acronym] (a part of [Parent Organization]) offers UG, PG, and [other] courses to students. These courses are provided across [departments]. [Institution] has been recognised by the [Bodies]. [Institution] provides [program] programmes to students in affiliation with [university]. Further, [Institution] provides [programs] as flagship courses and focuses on [areas]. The institute offers [percentage]% practical exposure and [percentage]% theoretical exposure to the students."

Paragraph 4: Campus + Faculty
"The institute is located in a [description] [number]-acre campus, and is equipped with the latest innovations and facilities. [Institution] has launched [initiatives], showcasing their commitment to [values] development."

Paragraph 5: Additional Information
"[Institution] is driven and promoted by [description]. Located in [city], this reputed [institution type] accepts [exam] scores and conducts [own exam] for admissions. The institute offers opportunities through [number]+ [activities] and [number]+ [programs]. [Institution] faculty are professionals with years of [experience type]."

Authentic Language Patterns:

Promotional Mixed with Factual:
- "top ranked premium [institution type]"
- "reputed [institution] is a non-[comparison] member"
- "one of the top-ranked [category] institutes"

Recognition Formulas:
- "recognized as one of the Top [Category] of Eminence in [Survey]"
- "securing the [position] among [category]"
- "has been ranked [number]th by [source]"

Program Description Patterns:
- "focuses on [area 1], [area 2], & [area 3]"
- "offers [percentage]% practical exposure and [percentage]% theoretical exposure"
- "flagship courses" terminology
- "across [field] and various other streams"

Content Quality Control Requirements:

Natural Imperfection Checklist:
- Institution name repeated 6+ times
- Mixed terminology (college/institute/university)
- Awkward transitions between topics
- Statistical clustering without smooth flow
- Natural number integration without formatting
- Multiple ranking mentions
- Redundant information presentation
- Parenthetical clarifications included

Authentic Flow Issues (REQUIRED):
- Abrupt topic changes between paragraphs
- Information presented in institutional content writer style (not polished narrative)
- Natural redundancy in key information
- Specific but awkwardly phrased details
- Mixed promotional and limitation language

Output Requirements:
- Length: 200-300 words for comprehensive coverage
- Format: Plain text output without any formatting (no bold, no markdown)
- Institution Naming: 6-8 repetitions throughout content
- Information Density: Varied with natural clustering
- Authenticity Level: Institutional content writer style, not AI-polished

Final Verification:
Content must read like authentic institutional marketing content with natural imperfections, redundancies, and flow issues that characterize real human-written educational content rather than AI-generated polished text.

OUTPUT FORMAT REQUIREMENTS:
- Generate content in plain text format
- NO bold formatting or special characters
- Natural integration of numbers and statistics
- Clean, readable text output
"""
        )

        self.overview_prompt = OVERVIEW_PROMPT