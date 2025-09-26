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
# Prompt for Writing IIT Madras Style College Summaries

SAMPLE OF THE CONTENT:
"Identified as an ‘Institute of Eminence', the Indian Institute of Technology Madras (Chennai IIT Madras or IITM) was established in 1959 as a public technical and research university. It is the third IIT to be set up by the Government of India and is autonomous in nature. Chennai IIT Campus, through its 16 departments, 4 national and 10 institute research centres offers more than 100 full-time/ part-time/ online courses at UG, PG, and doctoral levels across the Engineering, Science, Humanities, and Management. IIT Madras admissions are entrance-based. IIT Madras Campus accepts various national-level exams, such as JEE Advanced, for admission to specific courses. OpenAI has recently announced its first Learning Accelerator in India in collaboration with IIT Madras, Chennai."

## Content Analysis Reference
Based on the IIT Madras sample, generate content with these specific characteristics:
- **Word count**: 115-125 words
- **Sentence count**: 6-7 sentences
- **Tone**: Official, informative, promotional
- **Structure**: Statistical clustering with institutional authority
- **Add some punctuation issues (i.e. comma heavy sentences) and natural information flow issues**

## College Data Available:
- College Name: {college_name}
- City: {city}
- State: {state}
- Establishment Year: {establishment_year}
- Departments: {departments}

**NOTE: If any data field is missing, empty, or unavailable, EXCLUDE it from the summary. Do not fabricate, assume, or add any information not explicitly provided in the college data fields.**

## Writing Instructions

### Opening Formula
Start with a prestigious credential or recognition in bold, followed by full institutional name with variations:
- "Identified as **'[Recognition Status]'**, the {college_name} ({city} {state} or [Acronym]) was established in **{establishment_year}**" and  **other details**

### Content Structure Pattern
1. **Sentence 1** (25-30 words): Prestigious recognition + establishment + basic classification
2. **Sentence 2** (18-20 words): Historical context + governance/autonomy status
3. **Sentence 3** (30-35 words): Statistical cluster - departments, centers, courses with bold numbers
4. **Sentence 4** (5-6 words): Brief admission statement
5. **Sentence 5** (15-18 words): Specific entrance exam requirements
6. **Sentence 6** (15-20 words): Recent news/collaboration/achievement in bold

### Statistical Clustering Requirements
- Use **bold formatting** for ALL numbers and key achievements
- Include 4-6 numerical statistics: **{departments}** departments, **[number]** research centers, **{total_courses}+** courses
- Group statistics in single complex sentence with multiple clauses
- Mention course levels: "UG, PG, and doctoral levels"
- Include broad academic areas: "Engineering, Science, Humanities, and Management"

### Language Patterns
- **Institutional Name Repetition**: Use full name, location variant, and acronym (3-4 mentions minimum)
- **Formal Connectors**: "through its," "across the," "such as"
- **Authority Markers**: "autonomous in nature," "Government of [Country]," "national-level exams"
- **Promotional Elements**: Recognition badges, rankings, recent partnerships

### Required Elements
- **Establishment year** in bold: **{establishment_year}**
- **Numerical statistics** (departments, centers, courses) in bold
- **Admission process** mention (entrance-based)
- **Specific entrance exam** name
- **Recent achievement/collaboration** in bold as closing

### SEO-Style Repetition Pattern
- Institution name: Use 3 variations (Full name, Location name, Acronym)
- Location mention: 2-3 times in different contexts ({city}, {state})
- Course levels: Specify "full-time/part-time/online" options

## Sample Framework
"Identified as **'[Recognition Status]'**, the {college_name} ({city} {state} or [Acronym]) was established in **{establishment_year}** as a [classification]. It is the [ordinal position] [type] to be set up by the Government of [Country] and is autonomous in nature. {city} {state} Campus, through its **{departments}** departments, **[number]** [type] and **[number]** [type] research centres offers more than **{total_courses}** full-time/part-time/online courses at UG, PG, and doctoral levels across the [Field 1], [Field 2], [Field 3], and [Field 4]. {college_name} admissions are entrance-based. {college_name} Campus accepts various national-level exams, such as [Specific Exam], for admission to specific courses. **[Recent achievement/collaboration/news].**" and **other details**

## Formatting Requirements
- Use **bold** for: Numbers, achievements, recognition status, recent news
- Use italics: Never (not in this style)
- Punctuation: Standard academic punctuation with comma-heavy complex sentences and natural information flow issues
- Capitalization: Proper nouns, official titles, exam names

## Quality Markers
The content should read like:
- An official institutional profile
- Statistical fact sheet in paragraph form
- Authoritative reference material
- Marketing-academic hybrid writing

## Word Count Distribution
- Opening credential sentence: 25-30 words
- Context/governance: 18-20 words  
- Statistical cluster: 30-35 words
- Admission statement: 5-6 words
- Exam requirements: 15-18 words
- Recent news/closing: 15-20 words
- **Total target: 115-125 words**
"""
        )

        self.overview_prompt = OVERVIEW_PROMPT