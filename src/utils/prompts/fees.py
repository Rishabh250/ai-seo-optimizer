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
                "city",
                "state",
                "total_programs",
                "degree_levels",
                "fee_range",
                "accessibility_support",
                "programs_list",
                "specializations",
            ],
            template="""
**Authentic Fees Content Generation**

**Primary Instruction:**
Generate fees information following exact content patterns that successfully bypass AI detection through authentic institutional content writing imperfections and natural information flow issues.

**College Data:**
- College Name: {college_name}
- Location: {city}, {state}
- Total Programs: {total_programs}
- Degree Levels: {degree_levels}
- Accessibility Support: {accessibility_support}
- Fee Range: [FEE RANGE] (USE this data as reference for the fee range)


**STRICT REQUIREMENT: Do not use competitors name in the fees information like Shiksha.com, Careers360, Collegedunia, etc.**

**INSTRUCTION:** 
Don't add title like Overview, Summary, etc.**

*Note: If any data is not available, remove it from the fees information.*

**Critical Content Patterns (MANDATORY):**

**1. Statistical Integration Style:**
- Embed fee ranges naturally: *"ranges from INR [Amount] to INR [Amount]"*, *"starts from INR [Amount]"*
- Use exact fee amounts: *"INR [Amount] per semester"*, *"INR [Amount] annually"*
- Include specific fee components: *"tuition fees of INR [Amount]"*, *"accommodation charges of INR [Amount]"*
- Reference specialization fees: *"fees vary by specialization from INR [Amount] to INR [Amount]"*
- Mention payment periods: *"payable [annually/semester-wise/monthly]"*

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
- Mix promotional language with factual limitations
- Scatter multiple fee policy mentions: *"as per [Authority] guidelines"*

**5. Natural Content Imperfections (ESSENTIAL):**
- **Mixed terminology:** Alternate between *"college,"* *"institute,"* *"university"*, *"fees,"* *"tuition,"* *"charges"*
- **Redundant information:** Mention placement assistance multiple ways

**Required Content Structure: (Maximum 1-2 paragraphs)**

**Paragraph 1: Comprehensive Fee Structure**
TEMPLATE 1: "Candidates can enroll for any of the {college_name} courses by paying the course fee. The fee for the available courses [FEE RANGE]. The {college_name} fee is made up of a number of different elements, including tuition, security deposit, and other charges. The college offers {total_programs} programs across {degree_levels} levels with {programs_list} and specializations in {specializations}. {college_name} is located in {city}, {state} and provides accessibility support ({accessibility_support}). To confirm their seat, candidates who made through the shortlist via the {college_name} admission process must pay the course fee."
TEMPLATE 2: "Candidates who complete the admission formalities at {college_name} are required to pay the course fee to confirm their seat. Students can check with the admission office if the university allows payment through both online and offline modes. The tuition fee for {college_name} courses typically [FEE RANGE], depending on the programme and level of study. However, students must note that this fee information is sourced from official website/ sanctioning body and is subject to change. The college offers {total_programs} programs across {degree_levels} levels with {programs_list} and specializations in {specializations}. {college_name} is located in {city}, {state} and provides accessibility support ({accessibility_support})."*

**USE ANY ONE OF THE TEMPLATES BASED ON THE DATA AVAILABLE**

**Fee Component Integration Guidelines:**
- **Tuition Fees**: Mention specific amounts from fee range for different degrees
- **Additional Charges**: Include library fee, examination fee, registration fee (if available)
- **Payment Structure**: Mention payment periods (annual/semester-wise)
- **Specialization Variance**: Include fee differences across specializations
- **Fee Transparency**: Emphasize transparent fee structure and competitive pricing

**Data Integration Requirements:**
- Use fee range and program information effectively
- Reference specific degree programs and their fee structures
- Focus on transparent fee presentation

**Authentic Language Patterns:**

**Promotional Mixed with Factual:**
- *"reputed [institution] is a non-[comparison] member"*

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
- Length: **80-120 words** for comprehensive coverage (extended to include detailed fee data)
- Format: **Rich text output with bold, italic and styling** that humans usually add
- Institution Naming: **2-4 repetitions** throughout content
- Information Density: Varied with natural clustering of fee components
- Authenticity Level: *Institutional content writer style*, not AI-polished
- Fee Accuracy: Use EXACT amounts from detailed_fee_data JSON structure
- Component Coverage: Include at least 3-4 fee components from the detailed data

***Final Verification:***
Content must read like authentic institutional fees marketing content with natural imperfections, redundancies, and flow issues that characterize real human-written educational content rather than AI-generated polished text.

**SAMPLE CONTENT INTEGRATION PATTERNS:**

**Example 1 - Comprehensive Fee Structure:**
*"{college_name} offers structured fee arrangements for **{total_programs} programs** across {degree_levels} levels. The **tuition fees** at {college_name} start from **INR [specific_amount]** for [degree_name] programs, with payment due **[payment_period]**. The college ensures **transparent fee structure** for students in {city}, {state}, with specializations in {specializations}."*

**Example 2 - Component-wise Fee Details:**
*"The fee structure at {college_name} includes **tuition fees of INR [amount]**, registration charges, and examination fees. {college_name} in {city}, {state} provides **quality education** with fees payable [payment_schedule] across {degree_levels} programs."*

**OUTPUT FORMAT REQUIREMENTS:**
- Generate content in **rich text format with human-like styling**
- **USE bold, italic and other formatting** that humans naturally add
- Natural integration of *numbers* and **statistics** from fee range data
- **Well-formatted, styled text output**
- **MANDATORY**: Include specific fee amounts from the fee range information
"""
        )

        self.fees_prompt = FEES_PROMPT
