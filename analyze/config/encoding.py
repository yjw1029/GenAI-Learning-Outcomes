"""
Encoding configurations for survey data preprocessing.

This module contains all mapping dictionaries used to convert categorical
survey responses into numeric values for statistical analysis.
"""

# ============================================================================
# Demographic Information Encodings
# ============================================================================

# University ranking (学校排名 from valid_users file, not 基本信息_0)
UNIVERSITY_RANKING_MAP = {
    '前10名': 5,
    '10-50名': 4,
    '10-50': 4,  # Variant
    '50-100名': 3,
    '50-100': 3,  # Variant
    '100-500名': 2,
    '100-500': 2,  # Variant
    '500名之外': 1,
    '500以外': 1,  # Variant
    '不确定/不愿透露': 0,
    '其他': 0,
}

# Grade level (基本信息_2)
GRADE_MAP = {
    '大一': 1,
    '大二': 2,
    '大三': 3,
    '大四': 4,
    '硕一（直博一年级）': 5,
    '硕二（直博二年级）': 6,
    '硕三（直博三年级）': 7,
    '博一（直博四年级）': 8,
    '博二（直博五年级）': 9,
    '博三（直博六年级）': 10,
    '博四（直博七年级）': 11,
    '不确定/不愿透露': 0,
    # Variants with different spacing
    '研一 （直博一年级）': 5,  # Extra space before parenthesis
    '研一（直博一年级）': 5,
    '研二（直博二年级）': 6,
    '研三（直博三年级）': 7,
    # Graduate level descriptions
    '研究生或以上': 5,  # General graduate level, map to Master's Year 1
    '目前研0': 5,  # Pre-grad year, map to Master's Year 1
    '应届毕业生': 4,  # Recent graduate, map to Senior year
    '已毕业': 4,  # Graduated, map to Senior year
    '毕业': 4,
    # Other variants
    '其他：开学大三': 3,  # Starting Junior year
}

# Class ranking (基本信息_3)
CLASS_RANKING_MAP = {
    '前10%': 4,
    '前20%': 3,
    '前30%': 2,
    '低于30%': 1,
    '不确定/不愿透露': 0,
}

# First generation college student (基本信息_4)
FIRST_GEN_COLLEGE_MAP = {
    '是': 1,
    '否': 0,
    '不确定/不愿透露': 0,
}

# Economic status (基本信息_5)
ECONOMIC_STATUS_MAP = {
    '超过10,000,000元': 6,
    '1,000,000 - 10,000,000元': 5,
    '500,000 - 1,000,000元': 4,
    '100,000 - 500,000元': 3,
    '60,000 - 100,000元': 2,  # Variant
    '50,000 - 100,000元': 2,
    '低于60,000元': 1,  # Variant
    '低于50,000元': 1,
    '不确定/不愿透露': 0,
}

# ============================================================================
# Python Course Specific Encodings
# ============================================================================

# Programming frequency (知识调查_1 for Python)
PROGRAMMING_FREQUENCY_MAP = {
    '几乎每天': 4,
    '几乎每周': 3,
    '偶尔': 2,
    '很少，几乎不': 1,
    '很少': 1,  # Variant
    '从不': 0,
    '从未': 0,  # Variant
}

# ============================================================================
# Math Course Specific Encodings
# ============================================================================

# Math experience (知识调查_0 for Math)
# Note: Some responses use "导数" (derivative), others use "微积分" (calculus)
MATH_EXPERIENCE_MAP = {
    # Original "导数" (derivative) version
    '我非常了解导数相关知识，包括导数、偏导数等。': 4,
    '我学过与导数相关的内容，但对如何计算导数和偏导数不太清楚或不记得了。': 3,
    '我只接触过一些导数的基本概念，对它们不是很熟悉。': 2,
    '我没有学过导数等概念。': 1,
    # "微积分" (calculus) version - map to same levels
    '我非常熟悉微积分，包括导数、偏导数等。': 4,
    '我学过与导数相关的内容，但对如何计算偏导数不太清楚或不记得了。': 3,
    '我只接触过一些微积分的基本概念，对它们不是很熟悉。': 2,
    '我没有学过微积分，包括导数等概念。': 1,
    # Other responses
    '其他：我在高中的时候学习过基本的导数知识': 2,  # Basic knowledge
}

# Calculus last used (知识调查_1 for Math)
CALCULUS_LAST_USED_MAP = {
    '在过去的一周内': 5,
    '在过去的一个月内': 4,
    '在过去的六个月内': 3,
    '在过去的一年内': 2,
    '超过一年前': 1,
    '从未': 0,
    '从不': 0,  # Variant
    # "其他" (Other) responses - need to map based on content
    '其他：今天': 5,  # Today = within past week
    '其他：两个月多以前': 3,  # 2+ months ago = within 6 months
    '其他：两年前，高考的时候学过': 1,  # 2 years ago = over a year
    '其他：从未学过': 0,
    '其他：大学不用学高数': 0,  # Doesn't need to learn = never
    '其他：没学过，大学不需要学高数': 0,
    '其他：没有学习': 0,
    '其他：没有学过微积分': 0,
}

# ============================================================================
# GPT/LLM Usage Encodings (共同字段)
# ============================================================================

# GPT usage (大语言对话模型的使用_0)
GPT_USAGE_MAP = {
    '是': 1,
    '否': 0,
}

# GPT frequency (大语言对话模型的使用_1)
GPT_FREQUENCY_MAP = {
    '总是': 5,
    '经常': 4,
    '有时': 3,
    '很少': 2,
    '从不': 1,
    '从未': 1,  # Variant
}

# GPT familiarity (大语言对话模型的使用_2)
GPT_FAMILIARITY_MAP = {
    '5. 极其熟悉': 5,
    '5：极其熟悉': 5,  # Variant with Chinese colon
    '4. 比较熟悉': 4,
    '4：比较熟悉': 4,  # Variant
    '3. 一般熟悉': 3,
    '3：一般熟悉': 3,  # Variant
    '2. 略微熟悉': 2,
    '2：略微熟悉': 2,  # Variant
    '1. 不熟悉': 1,
    '1：不熟悉': 1,  # Variant
}

# GPT impact (大语言对话模型的使用_3)
GPT_IMPACT_MAP = {
    '5: 极大积极影响': 5,
    '5：极大积极影响': 5,  # Variant
    '4: 积极影响': 4,
    '4：积极影响': 4,  # Variant
    '3: 没有影响': 3,
    '3：没有影响': 3,  # Variant
    '2: 略微负面影响': 2,
    '2：略微负面影响': 2,  # Variant
    '1: 负面影响': 1,
    '1：负面影响': 1,  # Variant (not seen in data but included for completeness)
}

# Future GPT willingness (大语言对话模型的使用_8)
FUTURE_GPT_WILLINGNESS_MAP = {
    '非常愿意': 4,
    '比较愿意': 3,
    '中立': 2,
    '不太愿意': 1,
    '完全不愿意': 0,
    '我不了解基于大语言模型的平台': 0,
}

# ============================================================================
# Field name mappings (presurvey field -> processed column name)
# ============================================================================

# Common demographic fields (present in both Python and Math)
COMMON_DEMOGRAPHIC_FIELDS = {
    '基本信息_1': 'major',  # Will be classified into categories using major_classification.py
    '基本信息_2': 'grade',
    '基本信息_3': 'class_ranking',
    '基本信息_4': 'first_gen',  # Fixed: shortened from first_gen_college to match IPW covariate name
    '基本信息_5': 'economic_status',
    '基本信息_6': 'problem_solving_methods',  # List field, not encoded
}

# Common GPT-related fields
COMMON_GPT_FIELDS = {
    '大语言对话模型的使用_0': 'gpt_usage',
    '大语言对话模型的使用_1': 'gpt_frequency',
    '大语言对话模型的使用_2': 'gpt_familiarity',
    '大语言对话模型的使用_3': 'gpt_impact',
    '大语言对话模型的使用_4': 'gpt_tasks',  # List field
    '大语言对话模型的使用_5': 'non_usage_reasons',  # List field
    '大语言对话模型的使用_6': 'gpt_risks',  # List field
    '大语言对话模型的使用_7': 'gpt_expectations',  # List field
    '大语言对话模型的使用_8': 'future_gpt_willingness',
    '大语言对话模型的使用_9': 'evaluation_design',  # List field
}

# Python-specific knowledge fields
PYTHON_KNOWLEDGE_FIELDS = {
    '知识调查_0': 'programming_languages',  # List field
    '知识调查_1': 'programming_frequency',
}

# Math-specific knowledge fields
MATH_KNOWLEDGE_FIELDS = {
    '知识调查_0': 'math_experience',
    '知识调查_1': 'calculus_last_used',
    '知识调查_2': 'math_concepts',  # List field - Added mid-experiment, high missing rate is expected
}

# ============================================================================
# Encoding specifications: which fields to encode with which mapping
# ============================================================================

COMMON_ENCODINGS = {
    'grade': GRADE_MAP,
    'class_ranking': CLASS_RANKING_MAP,
    'first_gen': FIRST_GEN_COLLEGE_MAP,  # Fixed: shortened from first_gen_college
    'economic_status': ECONOMIC_STATUS_MAP,
    'gpt_usage': GPT_USAGE_MAP,
    'gpt_frequency': GPT_FREQUENCY_MAP,
    'gpt_familiarity': GPT_FAMILIARITY_MAP,
    'gpt_impact': GPT_IMPACT_MAP,
    'future_gpt_willingness': FUTURE_GPT_WILLINGNESS_MAP,
}

PYTHON_SPECIFIC_ENCODINGS = {
    'programming_frequency': PROGRAMMING_FREQUENCY_MAP,
}

MATH_SPECIFIC_ENCODINGS = {
    'math_experience': MATH_EXPERIENCE_MAP,
    'calculus_last_used': CALCULUS_LAST_USED_MAP,
}

# University ranking encoding is applied separately from the valid_users file
VALIDUSER_ENCODINGS = {
    'university_ranking': UNIVERSITY_RANKING_MAP,
}

# ============================================================================
# Covariate column definitions for IPW
# ============================================================================

# Covariates used for Python IPW analysis
PYTHON_IPW_COVARIATES = [
    'university_ranking_num',
    'major_num',                # Major category (ordered by coding proficiency)
    'grade_num',
    'class_ranking_num',
    'first_gen_num',
    'economic_status_num',
    'programming_frequency_num',
    'captest_score'
]

# Covariates used for Math IPW analysis
MATH_IPW_COVARIATES = [
    'university_ranking_num',
    'major_num',                # Major category (ordered by mathematical proficiency)
    'grade_num',
    'class_ranking_num',
    'first_gen_num',
    'economic_status_num',
    'math_experience_num',
    'captest_score'
]
