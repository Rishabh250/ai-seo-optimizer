from langchain.prompts import PromptTemplate


class ReviewsPrompt:
    def __init__(self):
        REVIEWS_PROMPT = PromptTemplate(
            input_variables=[
                "college_name",
                "city", 
                "state",
                "establishment_year",
                "campus_area",
                "reviews"
            ],
            template="""
**Shiksha.com Authentic Reviews Content Generation**

**Primary Instruction:**
Generate reviews information following Shiksha.com's exact content patterns that successfully bypass AI detection through authentic institutional content writing imperfections and natural information flow issues.

**College Data:**
- College Name: {college_name}
- City: {city}
- State: {state}
- Establishment Year: {establishment_year}
- Campus Area: {campus_area}

*Note: Use the college data to generate the reviews content, and if any data is not available, remove it from the reviews. Do not include negative reviews.*

**Mandatory Opening Formula for Reviews Content:**
*"[Institution Name] has received positive reviews from students and alumni across various platforms. The institute maintains an average rating of [Rating]/10 based on [Number]+ verified reviews. Students at [Institution] appreciate the [aspects] and [facilities] provided by the institute."*

**Critical Reviews Content Patterns (MANDATORY):**

**1. Statistical Integration Style:**
- Embed numbers mid-sentence naturally: *"established in [Year]"*, *"ranked [Number]th"*
- Use exact ranking formula: *"The [institution] has been ranked [Number]th by [Source] [Year] under the [Category] category"*
- Include multiple ranking mentions: *"[Number]th by [Source 1] and [Number]th by [Source 2]"*
- Add collaboration numbers: *"[Number]+ tie-ups with renowned universities"*
- Embed rating numbers naturally: *"[Rating] stars out of 5"*, *"[Percentage]% satisfaction rate"*

**2. Institution Name Repetition (AUTHENTIC PATTERN):**
- Use full institution name **3-5 times** throughout short content
- Mix variations: *"[Full Name]"*, *"[Acronym]"*, *"[Short Name]"*
- Include parenthetical clarifications: *"([Acronym] a part of [Parent Organization])"*
- Repeat institution name even when it feels redundant
- Include review-specific references: *"reviews for [Institution]"*

**3. Authentic Information Flow Issues:**
- **Topic jumping:** Move between rankings, programs, facilities without smooth transitions
- **Information clustering:** Group related statistics together abruptly
- **Awkward transitions:** Use phrases like *"Further, [Institution] provides..."*
- **Incomplete context:** Add parenthetical information that feels casually inserted
- Move between academic, placement, infrastructure reviews without smooth transitions

**4. Authority Validation Redundancy:**
- Repeat ranking information in different contexts
- Mix promotional language with factual limitations

**5. Natural Content Imperfections (ESSENTIAL):**
- **Mixed terminology:** Alternate between *"college,"* *"institute,"* *"university"*, *"reviews,"* *"ratings,"* *"feedback"*
- **Redundant information:** Mention placement assistance multiple ways, positive aspects multiple ways
- **Percentage specificity:** Include oddly specific numbers like *"70% practical exposure and 30% theoretical"*
- **Statistical awkwardness:** *"50+ guidance sessions"*, *"36+ online talks"*, *"[Number]+ reviews available"*

**Required Content Structure:**

**Paragraph 1: Overall Reviews + Rankings**
*"[Institution] has received positive reviews from students and alumni across various platforms. The [institution] has been ranked [Number]th by [Source] [Year] under the [Category] category. The institute maintains an average rating of [Rating]/10 based on [Number]+ verified reviews. Students at [Institution] appreciate the [aspects] and [facilities] provided by the institute."*

**Authentic Language Patterns:**

**Recognition Formulas:**
- "recognized as one of the **Top [Category] of Eminence** in [Survey]"
- "securing the **[position]** among [category]"
- "has been ranked **[number]th** by [source]"

**Review Description Patterns:**
- "*[rating] stars out of 5*"
- "*[percentage]% satisfaction rate*"
- "*[number]+ verified reviews*"
- "positive reviews from students"

**Content Quality Control Requirements:**

***Natural Imperfection Checklist:***
- Institution name repeated **6+ times**
- Mixed terminology (*college/institute/university/reviews/ratings/feedback*)
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
- Length: **80-100 words** for comprehensive coverage
- Format: **Rich text output with bold, italic and styling** that humans usually add
- Institution Naming: **6-8 repetitions** throughout content
- Information Density: Varied with natural clustering
- Authenticity Level: *Institutional content writer style*, not AI-polished

***Final Verification:***
Content must read like authentic institutional reviews marketing content with natural imperfections, redundancies, and flow issues that characterize real human-written educational content rather than AI-generated polished text.

**OUTPUT FORMAT REQUIREMENTS:**
- Generate content in **rich text format with human-like styling**
- Natural integration of *numbers* and **statistics**
- **Well-formatted, styled text output**
"""
        )

        self.reviews_prompt = REVIEWS_PROMPT