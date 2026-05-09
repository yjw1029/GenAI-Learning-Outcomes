title = "Post-test Survey"
description = """
In this post-test survey, we collect your feedback on this study and your views on using LLMs in education in the future.
Depending on your experimental group, you may or may not have access to the chat assistant. If you did not see the assistant in the platform, select "I cannot use the chat assistant" in the relevant questions.
"""

questions = {
    "Stage Comparison": [
        {
            "text": "How often did you use the chat assistant during the learning stage?",
            "type": "single_choice",
            "options": [
                "Not used",
                "Almost never",
                "Occasionally",
                "Often",
                "Very often",
                "I cannot use the chat assistant",
                "Other"
            ]
        },
        {
            "text": "How often did you use the chat assistant during Homework 1?",
            "type": "single_choice",
            "options": [
                "Not used",
                "Almost never",
                "Occasionally",
                "Often",
                "Very often",
                "I cannot use the chat assistant",
                "Other"
            ]
        },
        {
            "text": "How often did you use the chat assistant during the review stage?",
            "type": "single_choice",
            "options": [
                "Not used",
                "Almost never",
                "Occasionally",
                "Often",
                "Very often",
                "I cannot use the chat assistant",
                "Other"
            ]
        },
        {
            "text": "In which stage was the chat assistant most helpful?",
            "type": "single_choice",
            "options": [
                "Learning stage",
                "Homework stage (HW1)",
                "Review stage",
                "Not sure",
                "About equally helpful",
                "Not helpful in any stage",
                "I cannot use the chat assistant",
                "Other"
            ]
        }
    ],
    "Perceived Performance": [
        {
            "text": "How accurate were the assistant's answers?",
            "type": "single_choice",
            "options": [
                "Very accurate",
                "Somewhat accurate",
                "Neutral",
                "Somewhat inaccurate",
                "Very inaccurate",
                "I cannot use the chat assistant"
            ]
        },
        {
            "text": "How well did the assistant understand your questions?",
            "type": "single_choice",
            "options": [
                "Very accurate",
                "Somewhat accurate",
                "Neutral",
                "Somewhat inaccurate",
                "Very inaccurate",
                "I cannot use the chat assistant"
            ]
        },
        {
            "text": "Response personalization: Did it adjust guidance based on your replies within a conversation?",
            "type": "single_choice",
            "options": [
                "Always adjusts",
                "Often adjusts",
                "Sometimes adjusts",
                "Rarely adjusts",
                "Never adjusts",
                "I cannot use the chat assistant"
            ]
        },
        {
            "text": "Learning-level personalization: Did it consider your prior progress and knowledge in this course?",
            "type": "single_choice",
            "options": [
                "Always considers my progress",
                "Often considers my progress",
                "Sometimes considers my progress",
                "Rarely considers my progress",
                "Never considers my progress",
                "I cannot use the chat assistant"
            ]
        },
        {
            "text": "Effect on course learning: Compared to doing it alone (no assistant), did the assistant improve your efficiency and outcomes?",
            "type": "single_choice",
            "options": [
                "Significantly improved",
                "Slightly improved",
                "No change",
                "Slightly reduced",
                "Significantly reduced",
                "I cannot use the chat assistant"
            ]
        },
        {
            "text": "Effect on Homework 1: Compared to doing it alone (no assistant), did the assistant improve your efficiency and outcomes?",
            "type": "single_choice",
            "options": [
                "Significantly improved",
                "Slightly improved",
                "No change",
                "Slightly reduced",
                "Significantly reduced",
                "I cannot use the chat assistant"
            ]
        },
        {
            "text": "Effect on review: Compared to doing it alone (no assistant), did the assistant improve your efficiency and outcomes?",
            "type": "single_choice",
            "options": [
                "Significantly improved",
                "Slightly improved",
                "No change",
                "Slightly reduced",
                "Significantly reduced",
                "I cannot use the chat assistant"
            ]
        },
        {
            "text": "Effect on final assessment (HW2): Compared to not using the assistant, did it improve your efficiency and outcomes?",
            "type": "single_choice",
            "options": [
                "Significantly improved",
                "Slightly improved",
                "No change",
                "Slightly reduced",
                "Significantly reduced",
                "I cannot use the chat assistant"
            ]
        },
        {
            "text": "How polite was the assistant in its interactions?",
            "type": "single_choice",
            "options": [
                "Too polite, sometimes unnecessary",
                "Appropriately polite",
                "Cannot evaluate / not sure",
                "Not polite enough",
                "Very impolite",
                "I cannot use the chat assistant"
            ]
        },
        {
            "text": "How patient was the assistant in its interactions?",
            "type": "single_choice",
            "options": [
                "Too patient, sometimes unnecessary",
                "Appropriately patient",
                "Cannot evaluate / not sure",
                "Not patient enough",
                "Very impatient",
                "I cannot use the chat assistant"
            ]
        },
        {
            "text": "Compared to traditional learning, how interesting was learning with the assistant?",
            "type": "single_choice",
            "options": [
                "Much more interesting",
                "Slightly more interesting",
                "About the same",
                "Slightly more boring",
                "Much more boring",
                "I cannot use the chat assistant"
            ]
        },
        {
            "text": "Did the assistant encourage you to explore and learn new knowledge independently?",
            "type": "single_choice",
            "options": [
                "Strongly encouraged",
                "Somewhat encouraged",
                "Neutral",
                "Not very encouraged",
                "Not encouraged at all",
                "I cannot use the chat assistant"
            ]
        }
    ],
    "Motivation": [
        {
            "text": "Motivation: What were your main reasons for participating? (Select all that apply)",
            "type": "multiple_choice",
            "options": [
                "Learn related knowledge (game theory or programming)",
                "Understand how LLMs help learning",
                "Curiosity and interest in the experiment",
                "Support the researchers",
                "Receive compensation",
                "Other"
            ]
        },
        {
            "text": "During the experiment, what were your main purposes for using the assistant? (Select all that apply)",
            "type": "multiple_choice",
            "options": [
                "Help summarize reference materials",
                "Concept explanations",
                "Get answers to specific questions",
                "Get explanations for specific answers",
                "Get solution approaches",
                "Help recommend problems (if applicable)",
                "Help check answer correctness",
                "I cannot use the chat assistant",
                "Other"
            ]
        },
        {
            "text": "Which aspects of the assistant helped you understand the learning content? (Select all that apply)",
            "type": "multiple_choice",
            "options": [
                "Help summarize reference materials",
                "Concept explanations",
                "Get answers to problems",
                "Get explanations for problem answers",
                "Get solution approaches",
                "Validate my answers",
                "Not helpful",
                "I cannot use the chat assistant",
                "Other"
            ]
        },
        {
            "text": "How did you integrate the assistant into your learning? (Select all that apply)",
            "type": "multiple_choice",
            "options": [
                "I tried independently first and used the assistant only when stuck",
                "I used the assistant throughout the learning process",
                "I used the assistant mainly at the beginning to get a rough understanding, then studied independently",
                "I used the assistant later to review and consolidate",
                "I did not use the assistant or used it very little",
                "I cannot use the chat assistant",
                "Other"
            ]
        }
    ],
    "Views | Future": [
        {
            "text": "Overall attitude: How do you view applying chat assistants or similar AI tools in education?",
            "type": "single_choice",
            "options": [
                "Strongly support; it can greatly improve education experience and outcomes",
                "Somewhat support, but risks should be handled cautiously",
                "Neutral; I see both pros and cons",
                "Reserved; I worry about possible negative effects",
                "Strongly oppose; using such tools in education may cause serious problems",
                "Other"
            ]
        },
        {
            "text": "Willingness: How willing are you to use GPT or similar AI tools for learning in the future?",
            "type": "single_choice",
            "options": [
                "Very willing in the future",
                "Somewhat willing in the future",
                "Neutral / unsure",
                "Not very willing in the future",
                "Not willing at all in the future",
                "Other"
            ]
        },
        {
            "text": "Potential risks: If using GPT-like AI tools long-term for learning, which issues concern you? (Select all that apply)",
            "type": "multiple_choice",
            "options": [
                "I worry about over-reliance, which may weaken critical thinking and problem-solving.",
                "I worry the information from these tools may be inaccurate or unreliable.",
                "I worry these tools may lead to plagiarism or academic dishonesty.",
                "I worry this may reduce interaction and collaboration with peers/teachers.",
                "Other"
            ]
        }
    ],
    "Evaluation of Test Quality": [
        {
            "text": "Difficulty: How would you rate the overall difficulty of Homework 1?",
            "type": "single_choice",
            "options": [
                "Very challenging",
                "Somewhat challenging",
                "Moderate",
                "Relatively easy",
                "Very easy"
            ]
        },
        {
            "text": "Difficulty: How would you rate the overall difficulty of Homework 2?",
            "type": "single_choice",
            "options": [
                "Very challenging",
                "Somewhat challenging",
                "Moderate",
                "Relatively easy",
                "Very easy"
            ]
        },
        {
            "text": "Time adequacy: Was the time for Homework 1 sufficient?",
            "type": "single_choice",
            "options": [
                "More than sufficient",
                "Sufficient",
                "Moderate",
                "Tight",
                "Very tight"
            ]
        },
        {
            "text": "Time adequacy: Was the time for Homework 2 sufficient?",
            "type": "single_choice",
            "options": [
                "More than sufficient",
                "Sufficient",
                "Moderate",
                "Tight",
                "Very tight"
            ]
        },
        {
            "text": "Time adequacy: Was the time for learning sufficient?",
            "type": "single_choice",
            "options": [
                "More than sufficient",
                "Sufficient",
                "Moderate",
                "Tight",
                "Very tight"
            ]
        },
        {
            "text": "Review usefulness: Did the review stage help improve your mastery of the material?",
            "type": "single_choice",
            "options": [
                "Very helpful",
                "Somewhat helpful",
                "Moderate",
                "A little helpful",
                "Not helpful"
            ]
        },
        {
            "text": "During this study, what difficulties or challenges did you encounter? (Select all that apply)",
            "type": "multiple_choice",
            "options": [
                "Difficulty understanding the materials",
                "Lack of effective learning materials or resources",
                "Time management and scheduling",
                "Maintaining motivation and interest",
                "Homework pressure",
                "Other technical issues (lag, platform response, etc.)",
                "None",
                "Other"
            ]
        },
        {
            "text": "How easy was it to operate the chat assistant?",
            "type": "single_choice",
            "options": [
                "Very easy",
                "Somewhat easy",
                "Neutral",
                "Somewhat complex",
                "Very complex",
                "I cannot use the chat assistant"
            ]
        },
        {
            "text": "Please describe your overall experience during the test. You may mention ease of use, usefulness of features, any issues, or notable experiences. If you have suggestions for improvement, please describe them below.",
            "type": "textarea",
            "options": []
        }
    ]
}
