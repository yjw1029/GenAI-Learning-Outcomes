title = "Pre-test Survey (Game Theory)"
description = """In this pre-test survey, we collect basic information, your game theory background, and your familiarity with large language models."""

questions = {
    "Basic Information": [
        {
            "text": """University: According to the BCUR ranking, where is your university? (If not listed, choose Other and specify.)
            <a target='_blank' href='https://www.shanghairanking.cn/rankings/bcur/2024'>https://www.shanghairanking.cn/rankings/bcur/2024</a>
            """,
            "type": "single_choice",
            "options": ["Top 10", "Top 10-50", "Top 50-100", "Top 100-500", "Outside top 500", "Not sure / prefer not to say", "Other"]
        },
        {
            "text": "Major: What is your major?",
            "type": "textarea",
        },
        {
            "text": "Year: What year are you in?",
            "type": "single_choice",
            "options": ["Year 1", "Year 2", "Year 3", "Year 4", "Master's Year 1 (PhD-track Y1)", "Master's Year 2 (PhD-track Y2)", "Master's Year 3 (PhD-track Y3)", "PhD Year 1 (PhD-track Y4)", "PhD Year 2 (PhD-track Y5)", "Not sure / prefer not to say", "Other"]
        },
        {
            "text": "What is your approximate rank in your cohort/major?",
            "type": "single_choice",
            "options": ["Top 10%", "Top 20%", "Top 30%", "Below 30%", "Not sure / prefer not to say"]
        },
        {
            "text": "First-generation student: Are you the first in your family to attend college?",
            "type": "single_choice",
            "options": ["Yes", "No", "Not sure / prefer not to say"]
        },
        {
            "text": "Socioeconomic status: What is your household annual income range?",
            "type": "single_choice",
            "options": ["Below 50,000 RMB", "50,000 - 100,000 RMB", "100,000 - 500,000 RMB", "500,000 - 1,000,000 RMB", "1,000,000 - 10,000,000 RMB", "Above 10,000,000 RMB", "Not sure / prefer not to say"]
        },
        {
            "text": "How do you find solutions when you face learning problems? (Select all that apply)",
            "type": "multiple_choice",
            "options": ["Try on my own", "Consult documentation", "Ask classmates or teachers", "Online search (e.g., Baidu, Google)", "Technical Q&A platforms (e.g., Stack Overflow, GitHub)", "Watch learning videos or online courses (e.g., YouTube, Bilibili)", "Use LLMs for help (e.g., ChatGPT)", "Other"]
        }
    ],
    "Background": [
        {
            "text": "Math background: Describe your experience with derivatives.",
            "type": "single_choice",
            "options": [
                "I am very familiar with derivatives, including partial derivatives.",
                "I learned derivatives, but I am unclear or do not remember how to compute derivatives or partials.",
                "I only know basic concepts of derivatives and am not very familiar.",
                "I have not learned derivatives or related concepts.",
                "Other"
            ]
        },
        {
            "text": "Math familiarity: When did you last study or apply calculus (e.g., derivatives)?",
            "type": "single_choice",
            "options": [
                "Within the past week",
                "Within the past month",
                "Within the past six months",
                "Within the past year",
                "More than a year ago",
                "Other"
            ]
        },
        {
            "text": "Math background: Check all math concepts you have learned. (Select all that apply)",
            "type": "multiple_choice",
            "options": ["Derivatives", "Matrices", "Nash equilibrium", "Complex analysis", "Partial derivatives", "Static games", "Hypothesis testing", "Bellman equation", "Groups/Rings/Fields", "I have not learned any of the above"]
        },
    ],
    "Use of LLM Chat Models": [
        {
            "text": "Usage: Have you used LLM chat models (e.g., ChatGPT) before?",
            "type": "single_choice",
            "options": ["Yes", "No"]
        },
        {
            "text": "Frequency: If yes, how often do you use LLM chat models (e.g., ChatGPT) to support learning?",
            "type": "single_choice",
            "options": ["Never", "Rarely", "Sometimes", "Often", "Always"]
        },
        {
            "text": "Familiarity: On a 1-5 scale, how familiar are you with LLM chat models (e.g., ChatGPT)?",
            "type": "single_choice",
            "options": ["1. Not familiar", "2. Slightly familiar", "3. Moderately familiar", "4. Quite familiar", "5. Extremely familiar"]
        },
        {
            "text": "Impact: How do you rate their impact on learning (1-5)?",
            "type": "single_choice",
            "options": ["1: Negative", "2: Slightly negative", "3: No impact", "4: Positive", "5: Very positive"]
        },
        {
            "text": "Task usage: If yes, what types of tasks do you use LLM chat models (e.g., ChatGPT) for? (Select all that apply)",
            "type": "multiple_choice",
            "options": [
                "Concept explanations",
                "Answers and explanations for specific questions",
                "Help translate or summarize literature",
                "Help write reports or papers",
                "Research inspiration through dialogue",
                "Leisure",
                "Other"
            ]
        },
        {
            "text": "Reasons for not using: If you have not used LLM-based platforms (e.g., ChatGPT), what are the main reasons? (Select all that apply)",
            "type": "multiple_choice",
            "options": [
                "I have used LLM-based platforms (e.g., ChatGPT)",
                "I am not aware of LLM-based platforms",
                "Concerns about answer quality or truthfulness",
                "Accessibility or connectivity issues",
                "May weaken independent thinking",
                "Risk of plagiarism accusations",
                "Other"
            ]
        },
        {
            "text": "Potential risks: What risks do you think exist when using LLM chat models (e.g., ChatGPT) for learning? (Select all that apply)",
            "type": "multiple_choice",
            "options": [
                "I worry about over-reliance, which may weaken my critical thinking and problem-solving.",
                "I worry the information from these tools may be inaccurate or unreliable.",
                "I worry these tools may reduce deep learning.",
                "I worry this may reduce interaction and collaboration with peers/teachers.",
                "I think there are no risks in using LLM chat models for learning",
                "I am not aware of LLM-based platforms",
                "Other"
            ]
        },
        {
            "text": "Expectations: What do you hope to gain from learning with LLM chat models (e.g., ChatGPT)? (Select all that apply)",
            "type": "multiple_choice",
            "options": [
                "Improve learning outcomes for related knowledge",
                "Gain deeper understanding of related knowledge",
                "Higher motivation and engagement during learning",
                "I am not aware of LLM-based platforms",
                "Other"
            ]
        },
        {
            "text": "Willingness: How willing are you to use LLM chat models (e.g., ChatGPT) to support learning in the future?",
            "type": "single_choice",
            "options": [
                "Very willing",
                "Somewhat willing",
                "Neutral",
                "Not very willing",
                "Not willing at all",
                "I am not aware of LLM-based platforms"
            ]
        },
        {
            "text": "Assessment: How should educators design assessments to avoid misuse of LLM chat models (e.g., ChatGPT)? (Select all that apply)",
            "type": "multiple_choice",
            "options": [
                "Design open-ended questions",
                "Ban LLM chat models or any AI tools during learning (including homework)",
                "Ban LLM chat models or any AI tools during quizzes",
                "Provide guidance on using LLM chat models",
                "Provide dedicated restricted LLM tools (e.g., no direct solutions)",
                "I am not aware of LLM-based platforms",
                "Other"
            ]
        }
    ]
}
