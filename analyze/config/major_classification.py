"""
Major Classification Scheme for Educational Data Analysis

This module defines a consistent classification of academic majors into 8 categories,
with different ordinal encodings for Python and Math courses based on domain expertise.

Classification Categories (8 classes):
1. CS (Computer Science & Related): CS, Software Engineering, AI, Data Science, Network Security
2. EE (Electronics & Information): Electronic Engineering, Communication, Information Engineering
3. Engineering (Other): Mechanical, Chemical, Civil, Materials Engineering, etc.
4. Math & Stat: Mathematics, Statistics (pure quantitative sciences)
5. Natural Science: Physics, Chemistry, Biology (traditional natural sciences)
6. Applied Science: Agriculture, Medicine (applied fields, non-engineering aspects)
7. Business: Finance, Accounting, Management, Economics
8. Humanities & Social Sciences: Languages, Law, Education, Arts

Encoding Strategy:
- Python Course (Basic Python): Ordered by expected coding proficiency
  CS/EE(7) > Math&Stat(6) > Natural Science(5) > Other Engineering(4) > Applied Science(3) > Business(2) > Humanities(1)

  Note: CS and EE are encoded identically (7) since the course teaches only basic Python.
  Natural Science separated from Math&Stat: physics/chemistry/biology have similar computational needs.

- Math Course (Game Theory): Ordered by expected mathematical proficiency
  Math&Stat(8) > Natural Science(7) > CS/EE(6) > Other Engineering(4) > Applied Science(3) > Business(2) > Humanities(1)

  Note: Math&Stat highest (pure math). Natural Science 2nd (strong calculus/analysis background).
  CS/EE tied at 3rd (optimization/algorithms vs. signal processing).

Rationale:
- Natural Science (Physics/Chemistry/Biology) separated from Math/Stat: traditional science disciplines
- Math/Stat remains highest for mathematical rigor
- Natural Science ranked by strong calculus/analysis requirements (physics > chemistry > biology on average)
- For Python: Natural Science between Math/Stat and Engineering (computational modeling needs)
- For Math: Natural Science high due to strong theoretical math training (calculus, linear algebra)
"""

# ============================================================================
# Category 1: Computer Science & Related
# ============================================================================
CS_MAJORS = {
    # Core CS
    '计算机科学与技术', '计算机科学与技术（师）', '计算机科学与技术（java方向）', '计算机类',
    '软件工程',
    '计算机技术',

    # AI & Data Science
    '人工智能', '人工智能与数码媒体',
    '数据科学与大数据技术', '数据科学与大大数据技术', '数据科学与大数据技术专业',
    '数据科学与大数据统计',
    '智能科学与技术',

    # Networks & Security
    '网络工程', '物联网工程',
    '网络空间安全', '网络安全与执法',

    # Digital Media
    '数字媒体技术',
}

# ============================================================================
# Category 2: EE (Electronics & Information Engineering)
# ============================================================================
EE_MAJORS = {
    # Electronic Engineering
    '电子信息工程', '电子信息', '电子信息科学与技术', '电子科学与技术',
    '电子工程', '电信',
    '微电子科学与工程',
    '光电信息科学与工程',
    '新一代电子信息技术（含量子技术等）',
    '集成电路设计与集成系统',

    # Communication & Information Engineering
    '通信工程', '通信与信息工程', '信息与通信工程',
    '信息管理与信息系统',

    # Medical Information Engineering
    '医学信息工程', '医学影像技术',
    '生物医学工程',
}

# ============================================================================
# Category 3: Engineering (Other, Non-CS, Non-EE)
# ============================================================================
OTHER_ENGINEERING_MAJORS = {
    # Electrical & Automation (lower coding than EE)
    '电气工程及其自动化', '电气工程',
    '自动化',
    '测控技术与仪器',

    # Mechanical & Vehicle Engineering
    '机械工程', '机械设计制造及其自动化', '机械设计制造及自动化',
    '车辆工程', '车辆工程（英语强化）', '车辆工程&金融',
    '装甲车辆工程',
    '智能制造工程', '智能建造',

    # Materials & Chemical Engineering
    '材料成型及控制工程', '材料科学与工程', '材料化学',
    '金属材料专业', '金属材料工程（中日精英班）',
    '功能材料',
    '化学工程与工艺', '化工与制药', '精细化工', '制药工程',

    # Civil & Construction Engineering
    '建筑学',
    '工程力学', '力学',
    '交通运输', '交通工程',

    # Energy & Environment Engineering
    '能源与动力工程',
    '安全工程',
    '环境工程',
    '水利水电工程', '水利工程',

    # Resource Engineering
    '石油工程', '采矿工程',
    '海洋工程', '海洋资源开发技术', '海洋资源开发',
    '船舶工程',

    # Food Engineering
    '食品科学与工程',
}

# ============================================================================
# Category 4: Math & Statistics (Pure Quantitative Sciences)
# ============================================================================
MATH_STAT_MAJORS = {
    # Mathematics
    '数学与应用数学', '数学与应用数学（师范）',
    '信息与计算科学',
    '基础数学',
    '数学类',

    # Statistics
    '统计学', '应用统计', '应用统计学',
    '概率与统计',
}

# ============================================================================
# Category 5: Natural Science (Physics, Chemistry, Biology)
# ============================================================================
NATURAL_SCIENCE_MAJORS = {
    # Physics
    '物理学', '物理化学',

    # Chemistry
    '化学',

    # Biology
    '生物科学师范', '生物科学（师范）',
    '生物技术',
    '生物工程',
}

# ============================================================================
# Category 6: Applied Science (Agriculture, Medicine - Non-Engineering)
# ============================================================================
APPLIED_SCIENCE_MAJORS = {
    # Agriculture & Environment
    '植物保护',
    '水产养殖',

    # Medicine (clinical/applied, not engineering)
    '临床医学', '中医学', '医学检验技术', '运动康复',
}

# ============================================================================
# Category 7: Business & Economics
# ============================================================================
BUSINESS_MAJORS = {
    # Finance & Economics
    '金融学', '金融', '金融工程',
    '保险（精算）',
    '国际经济与贸易',

    # Accounting & Management
    '会计学',
    '工商管理大类',
    '人力资源管理',
    '公共事业管理',
    '旅游管理',
    '国际商务',
    '商务英语',

    # Special Business Programs
    '悉商',  # Sydney Business School program
    '数字社会与数据治理',

    # E-commerce (business-oriented, not technical)
    '电子商务',
}

# ============================================================================
# Category 8: Humanities & Social Sciences
# ============================================================================
HUMANITIES_MAJORS = {
    # Languages
    '英语', '英文', '英语语言文学',
    '汉语国际教育', '汉语国际教育专业',
    '汉语言文学',
    '德语', '俄语', '西班牙语*国际新闻传播',
    '印度尼西亚语（印英复语）',
    '阿拉伯语', '斯瓦希里语',
    '翻译',

    # Law & Politics
    '法学', '知识产权',
    '政治学', '外交学',
    '侦查学',

    # Education
    '教育技术学',

    # Media & Communication
    '传播学', '新闻与传播',

    # Arts & Design
    '音乐',
    '视觉传达设计', '视觉传达',
    '产品设计',

    # Social Sciences
    '应用心理学',
    '社会工作',

    # Archives & Administration
    '档案学', '现代文秘',

    # Archaeology
    '考古', '考古地信双学位',
}

# ============================================================================
# Classification Functions
# ============================================================================

def classify_major(major_name: str) -> str:
    """
    Classify a major into one of 8 categories.

    Args:
        major_name: Name of the major (Chinese)

    Returns:
        Category name: 'CS', 'EE', 'Other Engineering', 'Math & Stat',
                      'Natural Science', 'Applied Science', 'Business', or 'Humanities'
    """
    if not major_name or not isinstance(major_name, str):
        return 'Unknown'

    major_name = major_name.strip()

    if major_name in CS_MAJORS:
        return 'CS'
    elif major_name in EE_MAJORS:
        return 'EE'
    elif major_name in OTHER_ENGINEERING_MAJORS:
        return 'Other Engineering'
    elif major_name in MATH_STAT_MAJORS:
        return 'Math & Stat'
    elif major_name in NATURAL_SCIENCE_MAJORS:
        return 'Natural Science'
    elif major_name in APPLIED_SCIENCE_MAJORS:
        return 'Applied Science'
    elif major_name in BUSINESS_MAJORS:
        return 'Business'
    elif major_name in HUMANITIES_MAJORS:
        return 'Humanities'
    else:
        return 'Unknown'


# ============================================================================
# Encoding Maps for IPW Analysis
# ============================================================================

# For Python course: Ordered by expected coding proficiency
# For basic Python course: CS and EE have equivalent programming foundations
MAJOR_CATEGORY_ENCODING_PYTHON = {
    'CS': 7,                    # Highest coding proficiency (tied with EE)
    'EE': 7,                    # Highest coding proficiency (tied with CS)
    'Math & Stat': 6,           # Strong theory, computational methods
    'Natural Science': 5,       # Computational modeling, data analysis
    'Other Engineering': 4,     # Moderate coding (domain-specific)
    'Applied Science': 3,       # Some coding for data analysis
    'Business': 2,              # Limited coding (data tools)
    'Humanities': 1,            # Minimal coding
    'Unknown': 0,
}

# For Math course: Ordered by expected mathematical proficiency
# For game theory: Math/Stat highest, then Natural Science, then CS/EE
MAJOR_CATEGORY_ENCODING_MATH = {
    'Math & Stat': 8,           # Highest mathematical rigor (pure math)
    'Natural Science': 7,       # Strong calculus/analysis (physics/chem/bio)
    'CS': 6,                    # Strong math foundations (tied with EE)
    'EE': 6,                    # Strong math foundations (tied with CS)
    'Other Engineering': 4,     # Moderate math (applied)
    'Applied Science': 3,       # Applied statistics
    'Business': 2,              # Basic math & statistics
    'Humanities': 1,            # Minimal math
    'Unknown': 0,
}


def get_major_encoding(course_type: str):
    """
    Get the appropriate major encoding map for the course type.

    Args:
        course_type: 'python' or 'math'

    Returns:
        Dictionary mapping category names to numeric codes
    """
    if course_type.lower() == 'python':
        return MAJOR_CATEGORY_ENCODING_PYTHON
    elif course_type.lower() == 'math':
        return MAJOR_CATEGORY_ENCODING_MATH
    else:
        raise ValueError(f"Unknown course_type: {course_type}. Must be 'python' or 'math'.")


# ============================================================================
# Summary Statistics
# ============================================================================

def print_classification_summary():
    """Print summary of major classification scheme."""
    print("=" * 80)
    print("MAJOR CLASSIFICATION SUMMARY (8 Categories)")
    print("=" * 80)

    categories = [
        ("1. CS (Computer Science & Related)", CS_MAJORS),
        ("2. EE (Electronics & Information Engineering)", EE_MAJORS),
        ("3. Other Engineering (Non-CS, Non-EE)", OTHER_ENGINEERING_MAJORS),
        ("4. Math & Statistics (Pure Quantitative Sciences)", MATH_STAT_MAJORS),
        ("5. Natural Science (Physics, Chemistry, Biology)", NATURAL_SCIENCE_MAJORS),
        ("6. Applied Science (Agriculture, Medicine - Non-Engineering)", APPLIED_SCIENCE_MAJORS),
        ("7. Business & Economics", BUSINESS_MAJORS),
        ("8. Humanities & Social Sciences", HUMANITIES_MAJORS),
    ]

    total_majors = 0
    for category_name, majors_set in categories:
        count = len(majors_set)
        total_majors += count
        print(f"\n{category_name}: {count} majors")
        print("-" * 80)
        # Print first 10 examples
        examples = list(majors_set)[:10]
        for major in examples:
            print(f"  - {major}")
        if len(majors_set) > 10:
            print(f"  ... and {len(majors_set) - 10} more")

    print("\n" + "=" * 80)
    print(f"Total classified majors: {total_majors}")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("ENCODING FOR PYTHON COURSE (Basic Python - by coding proficiency)")
    print("=" * 80)
    print("Note: CS and EE tied at highest (both strong in programming)")
    # Group by code to show ties
    python_by_code = {}
    for category, code in MAJOR_CATEGORY_ENCODING_PYTHON.items():
        if code > 0:
            if code not in python_by_code:
                python_by_code[code] = []
            python_by_code[code].append(category)
    for code in sorted(python_by_code.keys(), reverse=True):
        categories = ', '.join(sorted(python_by_code[code]))
        print(f"  {code}: {categories}")

    print("\n" + "=" * 80)
    print("ENCODING FOR MATH COURSE (Game Theory - by mathematical proficiency)")
    print("=" * 80)
    print("Note: Math&Stat(8) > Natural Science(7) > CS/EE tied(6)")
    # Group by code to show ties
    math_by_code = {}
    for category, code in MAJOR_CATEGORY_ENCODING_MATH.items():
        if code > 0:
            if code not in math_by_code:
                math_by_code[code] = []
            math_by_code[code].append(category)
    for code in sorted(math_by_code.keys(), reverse=True):
        categories = ', '.join(sorted(math_by_code[code]))
        print(f"  {code}: {categories}")


if __name__ == "__main__":
    print_classification_summary()
