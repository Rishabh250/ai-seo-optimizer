"""
Prompt templates for campus content generation.
"""
from langchain.prompts import PromptTemplate


class CampusPrompt:
    """Campus content generation prompt templates."""

    def __init__(self):
        CAMPUS_PROMPT = PromptTemplate(
            input_variables=[
                "college_name",
                "city", 
                "state",
            ],
            template="""
**Shiksha.com Authentic Campus Facilities Pattern Generation Prompt**

**Primary Instruction:**
Generate campus facilities information following Shiksha.com's exact content patterns that successfully bypass AI detection through authentic institutional content writing imperfections and natural information flow issues.

**College Data:**
- College Name: {college_name}
- City: {city}
- State: {state}

*Note: If any data is not available, remove it from the campus information.*

**Mandatory Opening Formula for Campus Content:**
*"[Institution Name] campus spans over [Number] acres with state-of-the-art infrastructure and modern facilities. The institute provides [Number]+ facilities including [examples] to ensure holistic development of students. [Institution] campus is equipped with [Number]+ laboratories and [Number]+ specialized centers."*

**Critical Shiksha.com Content Patterns (MANDATORY):**

**1. Statistical Integration Style:**
- Embed numbers mid-sentence naturally: *"established in [Year]"*, *"ranked [Number]th"*
- Use exact ranking formula: *"The [institution] has been ranked [Number]th by [Source] [Year] under the [Category] category"*
- Include multiple ranking mentions: *"[Number]th by [Source 1] and [Number]th by [Source 2]"*
- Add collaboration numbers: *"[Number]+ tie-ups with renowned universities"*
- Embed facility numbers naturally: *"over [Number] acres"*, *"[Number]+ facilities"*, *"[Number]+ laboratories"*

**2. Institution Name Repetition (AUTHENTIC PATTERN):**
- Use full institution name **6-8 times** throughout short content
- Mix variations: *"[Full Name]"*, *"[Acronym]"*, *"[Short Name]"*
- Include parenthetical clarifications: *"([Acronym] a part of [Parent Organization])"*
- Repeat institution name even when it feels redundant
- Include facility-specific references: *"campus at [Institution]"*, *"[Institution] infrastructure"*

**3. Authentic Information Flow Issues:**
- **Topic jumping:** Move between rankings, programs, facilities without smooth transitions
- **Information clustering:** Group related statistics together abruptly
- **Awkward transitions:** Use phrases like *"Further, [Institution] provides..."*
- **Incomplete context:** Add parenthetical information that feels casually inserted
- Move between academic, residential, sports facilities without smooth transitions

**4. Authority Validation Redundancy:**
- Scatter multiple accreditation mentions: *"recognised by AICTE, UGC, and [Regional Body]"*
- Repeat ranking information in different contexts
- Mix promotional language with factual limitations
- Include recognition statements: *"recognized as one of the Top [Category] in [Survey Year]"*
- Scatter multiple facility mentions: *"as per [Authority] standards"*

**5. Natural Content Imperfections (ESSENTIAL):**
- **Mixed terminology:** Alternate between *"college,"* *"institute,"* *"university"*, *"facilities,"* *"infrastructure,"* *"amenities"*
- **Redundant information:** Mention placement assistance multiple ways, key facilities multiple ways
- **Percentage specificity:** Include oddly specific numbers like *"70% practical exposure and 30% theoretical"*
- **Statistical awkwardness:** *"50+ guidance sessions"*, *"36+ online talks"*, *"[Number]+ facilities available"*

**Required Content Structure:**

**Paragraph 1: Campus Overview + Rankings**
*"{college_name} campus spans over [Number] acres with state-of-the-art infrastructure and modern facilities. The {college_name} has been ranked [Number]th by [Source] [Year] under the [Category] category. The institute provides [Number]+ facilities including [examples] to ensure holistic development of students. {college_name} campus is equipped with [Number]+ laboratories and [Number]+ specialized centers."*

**Paragraph 2: Recognition + Academic Facilities**
*"{college_name} has been recognized as one of the Top [Category] in [Survey Year], securing the [Position] among [Category]. {college_name} has [Number] smart classrooms with modern teaching aids and [Number]+ computer laboratories. The institute provides [Number] research laboratories and [Number] specialized workshops. {college_name} also houses [Number] digital libraries with [Number]+ books and online resources."*

**Paragraph 3: Campus + Accreditation**
*"[Acronym] (a part of [Parent Organization]) offers various campus facilities for different programs. These facilities are provided across [departments]. {college_name} has been recognised by the AICTE, UGC, and [Bodies]. {college_name} provides [program] programmes with campus facilities in affiliation with [university]. Further, {college_name} provides [programs] as flagship courses and focuses on [areas]. The institute offers [percentage]% practical exposure and [percentage]% theoretical exposure to the students."*

**Paragraph 4: Residential + Sports Facilities**
*"The institute is located in a sprawling [Number]-acre campus, and is equipped with the latest innovations and facilities. {college_name} offers [Number] hostels accommodating [Number]+ students with modern amenities. The institute provides [Number] sports complexes and [Number] playgrounds. {college_name} also has [Number] gymnasiums and [Number] swimming pools for student recreation."*

**Paragraph 5: Additional Amenities + Services**
*"{college_name} is driven and promoted by [description]. {college_name} also offers [Number] cafeterias, [Number] medical centers, and [Number] banking facilities. The institute provides [Number]+ parking spaces and [Number] security posts. {college_name} ensures [Number]% campus coverage with modern amenities."*

**Authentic Language Patterns:**

**Promotional Mixed with Factual:**
- "top ranked premium [institution type]"
- "reputed [institution] is a non-[comparison] member"
- "one of the top-ranked [category] institutes"

**Recognition Formulas:**
- "recognized as one of the Top [Category] of Eminence in [Survey]"
- "securing the **[position]** among [category]"
- "has been ranked **[number]th** by [source]"

**Infrastructure Description Patterns:**
- "spans over [number] acres"
- "state-of-the-art infrastructure"
- "[number]+ facilities including [examples]"
- "[number]+ laboratories"
- "modern amenities"

**Content Quality Control Requirements:**

***Natural Imperfection Checklist:***
- Institution name repeated **6+ times**
- Mixed terminology (*college/institute/university/facilities/infrastructure/amenities*)
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
- Format: **Plain text output without any formatting**
- Institution Naming: **6-8 repetitions** throughout content
- Information Density: Varied with natural clustering
- Authenticity Level: *Institutional content writer style*, not AI-polished

***Final Verification:***
Content must read like authentic institutional campus facilities marketing content with natural imperfections, redundancies, and flow issues that characterize real human-written educational content rather than AI-generated polished text.

**OUTPUT FORMAT REQUIREMENTS:**
- Generate content in **plain text format**
- **NO bold formatting or special characters**
- Natural integration of *numbers* and **statistics**
- **Clean, readable text output**
"""
        )

        self.campus_prompt = CAMPUS_PROMPT
