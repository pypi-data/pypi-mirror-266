"""
This module, `templates.templates`, currently serves as a repository for various templating functions used in the
processing and analysis of study documents. These functions are designed to generate structured prompts
and process text data, facilitating tasks such as cleaning up document sections, analyzing content for essential
information, and setting up data for embedding and retrieval.

However, it's important to note that this module is in the process of being deprecated. The introduction of
TemplateFactories represents a strategic shift towards a more modular and flexible approach to handle templating needs.
TemplateFactories will offer enhanced capabilities for dynamic template generation and management, thereby
streamlining the overall process and reducing the reliance on hardcoded template functions.


TODOs for Module Refactoring and Transition:
- TODO: Assess and document the current functionalities that need to be transitioned to TemplateFactories.
- TODO: Develop a migration plan for existing template functions to the new TemplateFactory approach.
- TODO: Implement a deprecation warning system within the module to inform users of the upcoming changes.
- TODO: Ensure backward compatibility where necessary during the transition phase.
- TODO: Create a comprehensive documentation guide for the new TemplateFactories to facilitate a smooth transition for existing users.
"""

from celi_framework.utils.utils import remove_text_chunk
from celi_framework.utils.log import app_logger


def make_cleanup_dict_prompt_template(section_content, section_heading, schema_dict):
    formatted_prompt = f"""

    You are analyzing a section of a scientific document.

    Here is the index of the study for context:
    {schema_dict}

    Analyze the following text from a section of the document extracted from a mix of copy/pasted content from microsoft word 
    and markdown format. This text may contain hyperlinks, table or figure references, and headings from a Word document conversion. 
    Determine if the content is meaningful on its own. If the content is useful, clean it up and return the cleaned text. 
    DO NOT CHANGE THE WORDING. KEEP AS MUCH OF THE TEXT UNCHANGED AS POSSIBLE.

    If the content does not contain meaningful standalone information or is erroneous, skip the section.
    If the content is erroneous (such as being an entire document, just hyperlinks, or unrelated text), provide a reason 
    to skip the section. Be conservative about saying a section does not contain meaningful standalone
    content. Reserve this for cases that you  believe the section was parsed erroneously from the source document, 
    like if a section contains an entire document, or half a section, or something like that. 
    If the section has text that only references other sections, KEEP IT, and just return the text.

    Otherwise, do your best to clean up the content and return the cleaned content. If there are tables in the text please 
    leave the tables out and have interpretations of the tables and explicitly reference the table headings and numbering. 
    Include all keywords in the interpretations that should be in the text for proper embedding retrieval. 

    This content will be embedded with sentence embedding that gets pooled. So make sure that every line of words gets 
    a period at the end.

    Here is the document section text:

    Section Heading:
    {section_heading}

    Section Body (Content):
    {section_content}

    Analysis result examples:
    {{"cleaned_text": "Relevant and cleaned text here...",
    "action": "save",
    "reason": ""}}

    {{"cleaned_text": "",
    "action": "skip",
    "reason": "Section contains only hyperlinks without standalone meaningful content."}}

    {{"cleaned_text": "",
    "action": "skip",
    "reason": "Section contains only the heading of a section."}}

    Analysis result (in json format):
    """
    return formatted_prompt


def create_prompt_for_essential_section_analysis(section_content):
    app_logger.info(
        "Drafting instructions to identify essential source materials...",
        extra={"color": "brown"},
    )
    if len(section_content["Document"]) > 0:
        # Ensure additional document contents are initialized if not provided
        section_content["Reference Material"] = section_content.get(
            "Reference Material", "No relevant content"
        )
        section_content["Guidelines"] = section_content.get(
            "Guidelines", "No relevant content"
        )

        formatted_prompt = f"""

        Assuming that the content for the document section was derived from sections in the reference materials 
        with minor edits (such as tense changes and formatting), which sections were used?

        Document Section ------- :
        {section_content['Document']}

        Reference Material(s) -------- :
        {section_content['Reference Material']}

        Guidelines Section(s) ---- :
        {section_content['Guidelines']}

        Please provide a JSON object indicating only the essential sections. 
        If there is insufficient data in the reference materials to draft the document content, 
        set "Sufficient Source Material" to "False". Otherwise, set it to "True".

        Format your response as:
        {{
            "Sufficient Source Material": "True" / "False",
            "Guidelines": {{
                "essential": [LIST OF ESSENTIAL SECTION NUMBERS]
            }},
            "Reference Material": {{
                "essential": [LIST OF ESSENTIAL SECTION NUMBERS]
            }}
        }}

        Provide your analysis and the final JSON object.
        """
        app_logger.info(
            "Template for Essential Source Analysis:", extra={"color": "green"}
        )
        app_logger.info(f"{formatted_prompt}", extra={"color": "green"})
        return formatted_prompt
    else:
        return "No document content provided. Skip."


def make_draft_setting_output_prompt(content):
    template = f"""
    Take the "content" below and format it into a json with the following format.
    DO NOT CHANGE THE WORDING OR NAMING CONVENTIONS. KEEP AS MUCH OF THE TEXT UNCHANGED AS POSSIBLE.
    
    Content:
    {content}
    
    Return format:
    {{
        "SECTION NUMBER HERE": {{
            'Heading': '[Heading here]',
            'Draft': "[content here]",
            'Comments': "[comments here]",
            'Success Flag': "[FAIL/PASS]",
            'Source Mapping': "[MAPPINGS TO UTILIZED SOURCES]",
            'Tables': "[REFERENCE TABLES HERE]",
            'Figures': "[REFERENCE FIGURES HERE]",
            'Cross-References': "[REFERENCES TO OTHER TARGET SECTIONS HERE (FROM EXAMPLE TARGET SECTION)]",
            'Scope of Section': "[HOW YOU FOLLOWED THE SCOPE GUIDELINES SET OUT IN TASK #2 OUTPUT]"
        }}
    }}
    
    With source mapping having this format:
    {{
    'New Source Doc 1': {{['4.1': '[Comments as to why it was mapped]', 
                       '4.2': '[Comments as to why it was mapped]'}},
        'New Source Doc 2': {{['2.3': '[Comments as to why it was mapped]', 
                       '2.4': '[Comments as to why it was mapped]'}},
    }}
    
    Return:

    """

    return template


def make_table_setting_output_prompt(json_content):
    template = f"""
    Take the content below and format it into a json with the format in the following example.
    FILL IN THE TABLE/FIGURE HEADING WHERE IT SAYS "HEADING HERE", USE THE TABLE/FIGURE NUMBER AS IT IS IN THE SOURCE
    DOCUMENT.
    
    Example Return:
    {{"9.3.2":
    {{"New Doc 1":
        {{"1.3.1":
            {{
            'Table 12':
                {{"heading": "HEADING HERE" 
                }},
            'Table 13':
                {{"heading": "HEADING HERE", 
                }}
            }}
        }},
    "New Doc 2":
        {{"2.5":
            {{
            'Figure 1':
                {{"heading": "HEADING HERE" 
                }}
            }}
        }}
    }}
    }}

    json content:
    {json_content}
    """

    return template


# TODO -> Add user message
def make_prompt_for_secondary_analysis(
    system_message, ongoing_chat, prompt_completion, response
):
    prior_ongoing_chat = remove_text_chunk(ongoing_chat, prompt_completion)
    template = f"""
Evaluate the language model's task completion for drafting sections of a [DOC TYPE], 
considering both the immediate response and its integration with the cumulative context of the ongoing chat.
 This template facilitates a comprehensive assessment, feedback provision, and actionable improvement suggestions.
 Keep in mind that every prompt completion will be appended to the ongoing chat, so tasks that are sequentially after
 the current prompt will have not only the current prompt completion's output but all the previous ones too. Therefore,
 it is not necessary, for example, to have a summary of the Example section text be produced if the text is already present
 in the ongoing chat. I need you to be VERY critical in your appraisal! The recommendations for changes to instructions
  must be for the task instructions in the system prompt, not for the instructions in the prompt completion. We can 
  change the instructions in the system prompt, not the prompt_completion.

**System Prompt:**
{system_message}

**Prior Ongoing Chat:**
{prior_ongoing_chat}

**Response (Prompt Completion):**
{response}

Return:

**Evaluation Specifics**:
1. Current task(s), with their high-level descriptions, that were completed in the prompt completion
2. Next task(s) to be completed, that are called out in the prompt completion
3. Exception flag (True/False)

**Evaluation Structure:**

1. **Evaluation Criteria**: Rate each aspect of the completion from 0 to 100%, taking into account the entire context available to the model.
   - **Relevance **: (0-100%) 
   Does the completion directly address the task, considering the full context of the ongoing chat?
   - **Accuracy**: (0-100%) 
   Is the provided information factually correct, leveraging all available context?
   - **Completeness**: (0-100%) 
   Given the cumulative context, does the completion fully address the task?
   - **Clarity**: (0-100%) 
   Is the output clearly communicated, enhancing the ongoing dialogue?
   - **Integration**: (0-100%) 
   How effectively does the completion integrate with and contribute to the ongoing chat?
   - **Contextual Sufficiency**: (0-100%) 
   Considering the ongoing chat, is the context used effectively? Would additional context within the chat have improved the completion?
   - **Overall Quality**: (0-100%) 
   The mean of the other scores.

2. **Detailed Feedback**:
   - **Strengths**: Identify strengths in how the completion utilizes and adds to the ongoing chat.
   - **Areas for Improvement**: Specify improvements, focusing on how future completions could better leverage the cumulative context.
   - **Contextual Evaluation**: Reflect on the strategic use of the ongoing chat's context. Suggest enhancements for utilizing context more effectively.

3. **Suggestions for Improvement**:
   - **For the Current Task**: Offer recommendations to refine task instructions for clearer integration with the ongoing chat.
   - **For Future Tasks**: Propose how the model might enhance its understanding or execution of tasks by better leveraging the cumulative context.

**Evaluator Guidelines**:
- If more than one task is executed within the same response, then give all quality evaluation scores 0%!!!
- Acknowledge "Skipping Tasks" appropriately, considering the full context of the ongoing chat.
- Provide concise, actionable feedback aimed at leveraging the cumulative context for continuous improvement.
- Highlight the model's use of context in both the evaluation criteria and detailed feedback to ensure a comprehensive assessment.

**Feedback Loop for Model Improvement**:
- Suggest ways the model could improve its handling of sequential tasks, particularly in how it integrates and builds upon the ongoing chat. Consider areas for training focus, such as enhancing context understanding, accuracy in information retrieval, and clarity in task transitions.

    """
    return template


# TODO -> Add user message? Do we even need system and user messages in here?
def make_prompt_for_function_call_analysis(
    system_message, ongoing_chat, function_name, function_arguments, prompt_completion
):
    """
    Constructs a prompt for secondary analysis to evaluate function call completions.

    This template is designed to assess the outcome of a function call made to the language model,
    considering the context of the request, the function's intended action, its actual output,
    and how exceptions or errors are handled.

    Args:
        system_message (str): The original system message or instruction that led to the function call.
        ongoing_chat (str): The accumulation of all interactions prior to this function call.
        function_name (str): The name of the function called.
        function_arguments (str): The arguments provided to the function call.
        prompt_completion (str): The output returned from the function call, which could be a successful result or an error message.

    Returns:
        str: A template filled with the provided information, ready for secondary analysis.
    """
    prior_ongoing_chat = remove_text_chunk(ongoing_chat, prompt_completion)
    template = f"""
    Evaluate the outcome of a large language model's function call completion for a specific task in drafting sections of a 
    document, taking into account the immediate function return, which will be 
    integrated with the cumulative context of the ongoing chat for the next LLM prompts. The function return is augmented
    with instructions from my process to help instruct the LLM what to do with the function return content in follow up
    LLM prompts. If there's an exception in the function return then you need to be very critical (0%s are OK). 
    The recommendations for changes to instructions must be for the task instructions in the system prompt, 
    not for the instructions in the prompt completion. We can change the instructions in the system prompt, 
    not the prompt_completion.

    This template aids in providing detailed feedback and actionable suggestions for improvement based on the 
    function call's execution.

    **System Prompt:**
    {system_message}

    **Prior Ongoing Chat:**
    {prior_ongoing_chat}

    **Function Name:**
    {function_name}

    **Function Arguments:**
    {function_arguments}

    **Augmented Function Return:**
    {prompt_completion}

    Return:

    **Evaluation Specifics**:
    1. Task completed in the function call
    2. Next steps recommended based on the function call outcome
    3. Exception flag (True/False) based on function call success or failure

    **Evaluation Structure:** 

    1. **Evaluation Criteria**: Rate each aspect of the function return from 0 to 100%, taking into account the entire context available to the model.
       - **Relevance **: (0-100%) 
       Does the function return directly address the task, considering the full context of the ongoing chat?
       - **Accuracy**: (0-100%) 
       Is the provided information from the function call factually correct, leveraging all available context?
       - **Completeness**: (0-100%) 
       Given the cumulative context, does the function return fully achieve the intended task?
       - **Clarity**: (0-100%) 
       Is the outcome of the function call clearly communicated, enhancing the ongoing dialogue?
       - **Integration**: (0-100%) 
       How effectively does the function return integrate with and contribute to the ongoing chat?
       - **Contextual Sufficiency**: (0-100%) 
       Considering the ongoing chat, is the context used effectively by the function return? Would additional context within the chat have improved the outcome?
       - **Overall Quality**: (0-100%) 
       The mean of the other scores.

    2. **Detailed Feedback**:
       - **Strengths**: Positive aspects of the function call execution and results.
       - **Areas for Improvement**: Shortcomings in the function call's execution with suggested improvements.
       - **Contextual Evaluation**: Analysis of the strategic use of the ongoing chat's context with enhancement suggestions.

    3. **Suggestions for Improvement**:
       - **For the Current Task**: Recommendations to refine function call instructions for clearer integration.
       - **For Future Tasks**: Strategies for the model to enhance understanding and execution of function calls by leveraging the context more effectively.

    **Feedback Loop for Model Improvement**:
    - Suggest ways the model could improve its handling of function calls, focusing on context understanding, accuracy, and clarity.
    """
    return template


def make_prompt_for_third_analysis():
    print(
        "TBD THIRD ANALYSIS TEMPLATE <----------------------------------------------------------"
    )


def make_toc_prompt_deprecated(pdf_extract):
    prompt = f"""
    Identify headings and subheadings in this text based on numbering and formatting (and pages). Print them out in a json using the formatting below (section number, section name, page number)..

    Text:
    {pdf_extract}

    Response Example:
      {{{{
          "toc": [
            {{{{
              "section_number": 0,
              "section_name": "Improving Image Generation with Better Captions",
              "page_number": 1
            }}}},
            {{{{
              "section_number": 1,
              "section_name": "Abstract",
              "page_number": 1
            }}}},
            {{{{
              "section_number": 2,
              "section_name": "Introduction",
              "page_number": 2
            }}}},
            {{{{
              "section_number": 3,
              "section_name": "Dataset Recaptioning",
              "page_number": 5
            }}}},
            {{{{
              "section_number": "3.1",
              "section_name": "Building an image captioner",
              "page_number": 5
            }}}},
            {{{{
              "section_number": "3.1.1",
              "section_name": "Fine-tuning the captioner",
              "page_number": 6
            }}}},
            {{{{
              "section_number": 4,
              "section_name": "Evaluating the re-captioned datasets",
              "page_number": 7
            }}}},
            {{{{
              "section_number": "4.1",
              "section_name": "Blending synthetic and ground-truth captions",
              "page_number": 7
            }}}},
            {{{{
              "section_number": "4.2",
              "section_name": "Evaluation methodology",
              "page_number": 7
            }}}},
            {{{{
              "section_number": "4.3",
              "section_name": "Caption type results",
              "page_number": 8
            }}}},
            {{{{
              "section_number": "4.4",
              "section_name": "Caption blending ratios",
              "page_number": 8
            }}}},
            {{{{
              "section_number": "4.5",
              "section_name": "Practical usage of highly descriptive captions",
              "page_number": 9
            }}}},
            {{{{
              "section_number": 5,
              "section_name": "DALL-E 3",
              "page_number": 10
            }}}},
            {{{{
              "section_number": 6,
              "section_name": "Limitations & Risk",
              "page_number": 13
            }}}},
            {{{{
              "section_number": "6.1",
              "section_name": "Spatial awareness",
              "page_number": 13
            }}}},
            {{{{
              "section_number": "6.2",
              "section_name": "Text rendering",
              "page_number": 13
            }}}},
            {{{{
              "section_number": "6.3",
              "section_name": "Specificity",
              "page_number": 13
            }}}},
            {{{{
              "section_number": "6.4",
              "section_name": "Safety and bias mitigations",
              "page_number": 13
            }}}}
          ]
        }}}}
    """
    return prompt


def make_toc_prompt(pdf_extract):
    """
    Constructs a prompt to identify headings and subheadings from a PDF extract.
    """
    prompt = f"""
    **Please identify the headings and subheadings from the following text based on numbering, formatting, and pages.**
    **Then, format your response as JSON with the following structure: section number, section name, and page number.**

    **Text Extract:**
    {pdf_extract}

    **Expected JSON Response Example:**
    {{
        "toc": [
            {{"section_number": 1, "section_name": "Improving Image Generation with Better Captions", "page_number": 1}},
            {{"section_number": 2, "section_name": "Abstract", "page_number": 1}},
            {{"section_number": 3, "section_name": "Introduction", "page_number": 2}},
            ...
            {{"section_number": 6, "section_name": "Limitations & Risk", "page_number": 13}}
        ]
    }}
    """
    return prompt
