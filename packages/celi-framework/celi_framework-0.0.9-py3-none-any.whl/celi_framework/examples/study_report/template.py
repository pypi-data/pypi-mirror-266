from celi_framework.core.job_description import JobDescription, Task

from celi_framework.examples.study_report.tools import StudyReportToolImplementations

task_library = [
    Task(
        task_name="Search for Document Section Text",
        details={
            "description": "Find the text of the current section in the sample document.",
            "prerequisite_tasks": [],
            "function_call": "Perform a function call to retrieve the text for the current section.",
            "example_call": "{{'Sample Document': ['1.1']}}",
            "instructions": [
                "Every section should have corresponding text, even that text is blank. If you get an error, try again with different parameters",
                "Do not truncate or modify the retrieved text.",
                "If text is present, print the entire text and instruct to proceed to the next task.",
                "If a given section is empty in the sample document, then you can leave that section empty in the target. In that case, you can skip all the remaining tasks and jump straight to the 'Draft New Document Section' task, which can just draft an empty section. Note that a blank section is not the same as the function returning an error.",
            ],
        },
    ),
    Task(
        task_name="Understand Differentiation",
        details={
            "description": "Understand the context of the sample document section by comparing it with similar sections.",
            "prerequisite_tasks": ["Search for Document Section Text"],
            "instructions": [
                "Identify other sections of the sample document that may contain content similar to the current section.",
                "Reference the 'Document to be drafted' dictionary.",
                "Retrieve the text of these sections along with their section identifiers.",
                "Analyze and note down how the current section differs from these sections to prevent duplication in future work.",
            ],
            "example": {
                "2.1.5": "Health Monitoring - Procedural topics...",
                "2.3.1": "Health Assessment (HA) - Statistical topics...",
            },
            "additional_notes": [
                "Keep your notes concise and relevant for later use.",
                "If 'no content present' is observed in all section bodies that are retrieved, even after retrieving children/sub-sections, proceed to the next task.",
            ],
        },
    ),
    Task(
        task_name="Handle Treatment Details",
        details={
            "description": "Address text related to treatment details in the sample document section.",
            "prerequisite_tasks": ["Search for Document Section Text"],
            "instructions": [
                "If there is no mention of additional treatments beyond the primary investigational product in the experimental arm, print 'Proceed to next task immediately.'",
                "If there is mention of additional treatments, list them in a numbered format and redraft the section by omitting this content. Adjust the scope of the section to be consistent with the revisions.",
            ],
            "examples": {
                "to_exclude": [
                    "In the Treatment Expansion, the investigational product and standard care were administered as outlined in Section X.Y.Z, until meeting any of the discontinuation criteria listed in Section A.B.",
                    "Treatment Group 2=Investigational Product + Regimen 2, for subjects with Condition A; Treatment Group 3=Investigational Product + Regimen 3, for subjects with Condition B with specific risk factors; Treatment Group 4=Investigational Product + Regimen 4, for subjects with Condition C.",
                ],
                "not_to_exclude": [
                    "For all Treatment Groups... Hospitalization details based on the study protocol.",
                    "Include text about dosage details: If multiple subjects received the same dosage level without adverse effects, this may be considered the selected dose for future phases.",
                ],
            },
            "additional_notes": [
                "Omit text about any additional therapies unless the section is relevant to both the primary treatment and additional therapies. Move to the next task if this does not apply."
            ],
        },
    ),
    Task(
        task_name="Identify Document Source",
        details={
            "description": "Identify the section source materials for the sample document section.",
            "function_call": "Call the source_sections_getter function to retrieve these materials.",
        },
    ),
    Task(
        task_name="Find Essential Source Materials",
        details={
            "description": "Identify the most critical source materials needed for drafting the sample document section.",
            "prerequisite_tasks": ["Identify Document Source"],
            "task": "Organize these materials in descending order of relevance and present them as a bulleted list.",
            "example": [
                "Sample Document Section S1: Outlines the general study framework, including major phases, medication schedules, and methods to address potential adverse effects.",
                "Sample Reference Section R1: Provides a summary of the study structure, with details on specific phases and medication schedules relevant to the investigational product.",
            ],
        },
    ),
    Task(
        task_name="Get source table of contents",
        details={
            "description": "Retrieve the TOCs of the new SAP and Protocol documents for the current section.",
            "function_call": "Call get_source_tocs.",
            "example_call": "{{'current_section_number': '9.1.a'}}.",
            "instructions": [
                "Retrieve the TOCs for the new SAP and new Protocol documents with function call.",
                "Do not modify the new source TOCs that you retrieve in any way.",
                "Do not hallucinate new TOCs.",
            ],
        },
    ),
    Task(
        task_name="Map Document Sources to New Indexes",
        details={
            "description": "Align sections of the new reference documents with the identified source sections of the sample document.",
            "prerequisite_tasks": [
                "Identify Document Source",
                "New target sources indexes",
            ],
            "instructions": [
                "Utilize the new indexes provided by the output of the previous task.",
                "Focus on the content and headings of the document sections rather than strict numbering conventions.",
                "Pay attention to overarching sections, like 'Study Overview', 'Data Analysis Methods', etc.",
            ],
        },
    ),
    Task(
        task_name="Handle Document Subsections",
        details={
            "description": "Ensure that both main sections and their nested subsections are appropriately mapped when necessary.",
            "prerequisite_tasks": ["Map Document Sources to New Indexes"],
            "instructions": [
                "Ensure alignment between the main section and any nested subsections that share relevant content.",
                "Comprehend the structure of sections and subsections by their sequence and thematic connection.",
            ],
        },
    ),
    Task(
        task_name="New Reference Material Retrieval",
        details={
            "description": "Retrieve the text for new reference document sections identified in previous tasks.",
            "prerequisite_tasks": ["Map Document Sources to New Indexes"],
            "instructions": [
                "Utilize the section text retrieval function to fetch the text for specified sections.",
                "Limit the retrieval to a maximum of 8 sections. If there are more than 8 sections identified as critical, prioritize based on importance.",
            ],
            "example_call": "{{ 'New Reference Document': ['1.1', '1.1.1'], 'New Guidelines': ['G2.2'] }}",
        },
    ),
    Task(
        task_name="Draft New Document Section",
        details={
            "description": "Draft a new section analogous to the revised example section (from {{TaskRef:Handle Treatment Details}} output), ensuring alignment with its structure, format, and scope (from {{TaskRef:Understand Differentiation}} output).",
            "prerequisite_tasks": [
                "Search for Document Section Text",
                "Understand Differentiation",
                "Map Document Sources to New Indexes",
                "New Reference Material Retrieval",
            ],
            "guidelines": [
                "The new section should have its unique scope and purpose, distinct from the example section.",
                "Closely align with the example section's approach for consistency.",
                "Avoid duplicating content or including redundant information.",
                "Aim for the new section to mirror the example section in length and detail.",
                "Follow the instructions set out by {{TaskRef:Understand Differentiation}} output.",
            ],
            "considerations": [
                "What differentiates this section from other similar sections? Refer to the output of {{TaskRef:Understand Differentiation}}.",
                "Concentrate on content relevant to the specific section within the broader document context.",
                "Maintain consistency in documentation methodology, using the revised example as a template.",
                "Ensure content is derived exclusively from the newly identified source materials.",
            ],
            "specific_instructions": [
                "Do not copy text verbatim. Include only text within the scope of the current section, as highlighted in the output of {{TaskRef:Understand Differentiation}}.",
                "Include cross-references to other sections as seen in the example if applicable.",
                "Incorporate references to tables and sections within the new reference documents as appropriate, providing context to the study's methodology and decision-making processes.",
            ],
            "note": "Focus on the specific section, considering its role within the parent sections and its relation to the revised example section. Utilize the guidance from {{TaskRef:Understand Differentiation}} for the scope of the section",
        },
    ),
    Task(
        task_name="Final Document Review",
        details={
            "description": "Review the final document and provide a PASS/FAIL decision based on the success criteria.",
            "prerequisite_tasks": ["Draft New Document Section"],
            "instructions": [
                "Evaluate the success of the new section draft",
                "Document the review outcome",
                "Print the final review output.",
            ],
            "success_flag_criteria": {
                "FAIL": [
                    "The section includes information beyond what's relevant as indicated by {{TaskRef:Understand Differentiation}}.",
                    "Any mention of specific drugs or combination therapies not relevant to the new study context.",
                    "Information in the new section is redundant with the sections analyzed in {{TaskRef:Understand Differentiation}}.",
                    "The draft does not reflect the structure, format, or detail level of the revised example section (output of {{TaskRef:Handle Treatment Details}}).",
                    "Missing or incorrectly referenced tables or figures from the new reference materials.",
                    "Significant deviation from the new reference materials, suggesting misalignment with the study's current focus.",
                    "Inconsistent use of verb tenses where required.",
                ],
                "PASS": [
                    "The section appropriately includes information within the scope defined by {{TaskRef:Understand Differentiation}}.",
                    "The draft logically follows what the section heading describes.",
                    "The draft focuses exclusively on the new study context.",
                    "The draft meets criteria for completeness, accuracy, and is aligned with the revised example and the new reference materials.",
                ],
            },
            "additional_instructions": "Offer feedback on the process of differentiating from other sections, the use of source materials, and the rationale for selected source mappings.",
            "output_format": {
                "Section Review": "[SECTION NUMBER] - [SECTION HEADING]",
                "Draft Review": "[content here]",
                "Comments": "[comments here]",
                "Success Flag": "[FAIL/PASS]",
                "Source Mapping Review": "[REVIEW OF UTILIZED SOURCES]",
                "Tables": "[LIST OF REFERENCED TABLES]",
                "Figures": "[LIST OF REFERENCED FIGURES]",
                "Cross-References": "[REFERENCES TO OTHER DOCUMENT SECTIONS (FROM SAMPLE DOCUMENT)]",
                "Scope of Section Review": "[REFLECTION ON FOLLOWING THE SCOPE GUIDELINES SET OUT IN {{TaskRef:Understand Differentiation}} OUTPUT]",
            },
        },
    ),
    Task(
        task_name="Prepare for Next Document Section",
        details={
            "description": "Complete current tasks and prepare to start drafting the next section of the document.",
            "prerequisite_tasks": ["Final Document Review"],
            "function_call": "Use the pop_context function with the argument value = current section identifier.",
            "example_call": "{{'current_section_identifier': ['1.2']}}",
            "instructions": [
                "Announce completion: 'Proceed to the next section of the document, [current section identifier] has been completed.'"
            ],
            "caution": "If the draft for the new section was not finalized in any prior tasks, then call pop_context with current_section_identifier = None",
        },
    ),
]

general_comments = """
============
GENERAL COMMENTS:
START WITH THE FIRST SECTION. ONLY DO THE NEXT UNCOMPLETED TASK (ONLY ONE TASK AT A TIME).
EXPLICITLY print out the current section identifier.
EXPLICITLY print out wheter the last task completed successfully or not.
EXPLICITLY print out the task you are completing currently.
EXPLICITLY print out what task you will complete next.
EXPLICITLY provide a detailed and appropriate response for EVERY TASK.
THE MOST IMPORTANT THING FOR YOU TO UNDERSTAND: THE PRIMARY GOAL OF THE TASKS IS TO DRAFT A NEW SECTION OF THE DOCUMENT
A SECTION IS CONSIDERED COMPLETE ONCE THE 'Final Document Review' TASK HAS BEEN ACCOMPLISHED.  DSO NOT SKIP THE 'Final Document Review' task.

IF A FUNCTION CALL RETURNS AN ERROR THEN TRY AGAIN WITH PARAMETERS, OR MAKE DIFFERENT FUNCTION CALL.
IF TASK HAS NOT COMPLETED SUCCESSFULLY, TRY AGAIN WITH AN ALTERED RESPONSE
IF YOU NOTICE A TASK (OR SERIES OF TASKS) BEING REPEATED ERRONEOUSLY, devise a plan to move on to the next uncompleted task.
IF YOU ENCOUNTER EMPTY MESSAGES REPEATEDLY IN THE CHAT HISTORY, reorient yourself by revisiting the last task completed. Check that the sequence of past tasks progresses in logical order. If not, assess and adjust accordingly.

Do not ever return a tool or function call with the name 'multi_tool_use.parallel'

=============
"""


initial_user_message = """
Please see system message for instructions. Take note of which document section is currently being worked on and which tasks have been completed. Complete the next uncompleted task.
If you do not see any tasks completed for the current section, begin with Task #1.

If all tasks for the current section have been completed, proceed to the next document section.
If the new section draft is complete, ensure to 'Prepare for Next Document Section' as described in the tasks.
"""

pre_algo_instruct = """
I am going to give you step by step instructions on how to draft a new study report document section by section.
Below you will find a json object that contains the index of sections that need to be drafted.
The keys of the json are the section numbers of the document. The values include the heading title.
"""

post_algo_instruct = """
We will look at a Sample Document that is similar to the document to be drafted.
Its full content can be queried with a function (section_text_getter) and used as an example (in json format).
The keys of the json are the section numbers of the document and the values contain the sections' bodies.
What I want you to do is to go section by section in the Document to be drafted, and do the following, in sequential order:
"""

job_description = JobDescription(
    role="You are a medical writing AI agent. You have the ability to call outside functions.",
    context="Document to be drafted:",
    task_list=task_library,
    tool_implementations_class=StudyReportToolImplementations,
    pre_context_instruct=pre_algo_instruct,
    post_context_instruct=post_algo_instruct,
    general_comments=general_comments,
    initial_user_message=initial_user_message,
)
