"""
All LLM prompts for ResumeAI.

Each function returns a fully formatted prompt string.
The model is instructed to respond ONLY in valid JSON matching the schema shown.
Resume text is embedded inside <resume> XML tags and truncated to ~3000 tokens.
"""

from __future__ import annotations

_MAX_RESUME_CHARS = 12000  # ~3000 tokens at ~4 chars/token


def _truncate(text: str) -> str:
    if len(text) > _MAX_RESUME_CHARS:
        return text[:_MAX_RESUME_CHARS] + "\n[...truncated for length...]"
    return text


def ats_prompt(resume_text: str, job_description: str = "") -> str:
    resume = _truncate(resume_text)
    jd_block = (
        f"\n<job_description>{job_description.strip()}</job_description>"
        if job_description.strip()
        else ""
    )
    return f"""You are an expert ATS (Applicant Tracking System) resume analyst.

Analyse the resume below and return ONLY a valid JSON object. Do not write anything before or after the JSON. No markdown, no explanation, no code fences.

CRITICAL INSTRUCTIONS:
1. You MUST extract at least 10-15 keywords from the resume and job description combined
2. For keyword_analysis, include ALL technical skills, tools, languages, frameworks, and domain terms found in the resume
3. If a job description is provided, also include keywords from it and mark them present/absent in the resume
4. keyword_analysis must NEVER be an empty array - always extract keywords from the resume itself
5. top_issues must contain 5 specific, actionable issues found in THIS resume - not generic advice

Scoring formula:
- 40 points: keyword coverage (how many relevant keywords are present)
- 30 points: section completeness (summary, experience, skills, education, projects all present and populated)
- 20 points: quantified achievements (numbers, percentages, metrics found in bullets)
- 10 points: formatting quality (clear headers, consistent structure, no walls of text)

Grade: A=90-100, B=75-89, C=60-74, D=45-59, F=0-44

Return this exact JSON structure:
{{
  "overall_score": 65,
  "grade": "C",
  "keyword_analysis": [
    {{"keyword": "Python", "present": true, "importance": "high"}},
    {{"keyword": "React", "present": true, "importance": "high"}},
    {{"keyword": "SQL", "present": false, "importance": "high"}},
    {{"keyword": "Docker", "present": false, "importance": "medium"}},
    {{"keyword": "REST API", "present": true, "importance": "medium"}},
    {{"keyword": "Git", "present": true, "importance": "medium"}},
    {{"keyword": "Agile", "present": false, "importance": "low"}},
    {{"keyword": "Node.js", "present": true, "importance": "high"}},
    {{"keyword": "AWS", "present": false, "importance": "high"}},
    {{"keyword": "TypeScript", "present": false, "importance": "medium"}}
  ],
  "section_scores": {{
    "summary": 0,
    "experience": 75,
    "skills": 80,
    "education": 90,
    "projects": 70
  }},
  "missing_sections": ["Summary"],
  "top_issues": [
    "No professional summary section - recruiters skip resumes without a summary",
    "Experience bullets lack quantified outcomes - add numbers, percentages, or impact metrics",
    "Missing cloud platform skills (AWS/GCP/Azure) which are required for most software roles",
    "No mention of team size or project scale in experience bullets",
    "Skills section lists tools without grouping by category making it hard to scan"
  ]
}}

<resume>{resume}</resume>{jd_block}

Remember: Return ONLY the JSON object. Nothing else."""


def fix_prompt(resume_text: str, job_description: str = "") -> str:
    resume = _truncate(resume_text)
    jd_hint = (
        f" The candidate is targeting: {job_description[:300]}"
        if job_description.strip()
        else ""
    )
    return f"""You are an expert resume coach who transforms weak resumes into powerful, ATS-optimised documents.{jd_hint}

Analyse the resume below section by section and return ONLY a valid JSON array. Do not write anything before or after the JSON. No markdown, no explanation, no code fences.

CRITICAL INSTRUCTIONS:
1. You MUST generate at least 3 BEFORE/AFTER fix pairs for EVERY section that has content
2. The "fixes" array must NEVER be empty for any section that exists in the resume
3. Rewrite weak bullets into STAR format: Action Verb + Task + Result with a metric
4. Every rewritten bullet must start with a strong past-tense action verb (Led, Built, Reduced, Increased, Designed, Implemented, etc.)
5. Every rewritten bullet must include a quantified outcome (%, number, time saved, revenue, users, etc.)
6. The "reason" field must name exactly what was improved (e.g. "Added team size + 40% metric + action verb")

STAR format example:
- WEAK: "Responsible for the website"
- STRONG: "Redesigned company website using React and Node.js, reducing page load time by 60% and increasing user engagement by 35%"

Return this exact JSON structure (array of section objects):
[
  {{
    "section_name": "Experience",
    "issues": [
      "Bullets use passive language instead of action verbs",
      "No quantified results or metrics in any bullet point",
      "Job responsibilities listed instead of achievements"
    ],
    "fixes": [
      {{
        "original": "Responsible for managing the development team",
        "rewritten": "Led a cross-functional team of 6 engineers delivering 4 product features per sprint, reducing time-to-production by 30%",
        "reason": "Replaced passive phrase with action verb, added team size, deliverable cadence, and quantified time improvement"
      }},
      {{
        "original": "Worked on the company website",
        "rewritten": "Rebuilt company website using React and TypeScript, improving Lighthouse performance score from 45 to 92 and cutting bounce rate by 28%",
        "reason": "Added specific technologies, before/after performance metrics, and business impact"
      }},
      {{
        "original": "Helped with customer support",
        "rewritten": "Resolved 50+ customer support tickets weekly with 97% satisfaction rating, reducing average resolution time from 48 hours to 6 hours",
        "reason": "Added volume metric, satisfaction score, and quantified time improvement"
      }}
    ],
    "missing_elements": [
      "Technologies used in each role",
      "Team size and scope of responsibility",
      "Promotions or growth indicators"
    ]
  }},
  {{
    "section_name": "Skills",
    "issues": [
      "Skills listed as a flat list without categorisation",
      "Missing industry-standard tools for the target role"
    ],
    "fixes": [
      {{
        "original": "Python, JavaScript, React, some cloud experience",
        "rewritten": "Languages: Python, JavaScript, TypeScript | Frameworks: React, Node.js, FastAPI | Tools: Git, Docker, VS Code | Cloud: AWS (EC2, S3) - beginner",
        "reason": "Grouped skills by category, replaced vague 'some cloud experience' with specific service names and honest level"
      }}
    ],
    "missing_elements": [
      "Version control tools",
      "CI/CD or DevOps tools",
      "Database technologies"
    ]
  }}
]

Now analyse this actual resume and apply all rules above. Extract the REAL content from the resume and generate fixes for REAL bullets found in it:

<resume>{resume}</resume>

Remember: Return ONLY the JSON array. Nothing else. The fixes array must never be empty."""


def career_prompt(resume_text: str, target_role: str = "") -> str:
    resume = _truncate(resume_text)
    target_hint = (
        f"\nIMPORTANT: The user's target role is '{target_role}'. This MUST appear as the first object in the array with honest match scoring."
        if target_role.strip()
        else ""
    )
    return f"""You are a senior career strategist and talent advisor with 15 years of experience in tech recruitment.{target_hint}

Analyse the resume below and return ONLY a valid JSON array of exactly 3 career role objects. Do not write anything before or after the JSON. No markdown, no explanation, no code fences.

CRITICAL INSTRUCTIONS:
1. Base ALL analysis on the actual content of this specific resume - not generic advice
2. match_reasons must reference specific skills, experience, or achievements from THIS resume
3. skill_gaps must be specific technologies or competencies missing from THIS resume
4. The 3 roles must be genuinely different career paths (not variations of the same role)
5. match_score must be honest - never give more than 85 unless the candidate is nearly perfectly qualified
6. Auto-detect seniority from years of experience and depth of skills in the resume

Return this exact JSON structure:
[
  {{
    "role_title": "Full Stack Developer",
    "match_score": 72,
    "match_reasons": [
      "React and Node.js experience from 2 years of project work directly maps to full stack requirements",
      "REST API development experience shown in Projects section aligns with backend responsibilities",
      "JavaScript proficiency across frontend and backend reduces onboarding friction"
    ],
    "skill_gaps": [
      "PostgreSQL or MySQL - no relational database experience shown in resume",
      "Docker and containerisation - required for most full stack roles in 2025",
      "Testing frameworks (Jest, Cypress) - no testing experience mentioned"
    ],
    "time_to_ready": "2-3 months with focused upskilling on databases and DevOps",
    "recommended_project": "Build a full-stack task management app with React frontend, Node.js/Express backend, PostgreSQL database, JWT authentication, and deploy it on Railway with a CI/CD pipeline",
    "seniority_target": "Junior"
  }},
  {{
    "role_title": "Backend Developer",
    "match_score": 65,
    "match_reasons": [
      "Python experience shown in resume is directly applicable to backend service development",
      "API development background provides foundation for microservice architecture",
      "Problem-solving projects demonstrate ability to architect solutions independently"
    ],
    "skill_gaps": [
      "System design patterns - no evidence of scalability or architecture thinking",
      "Message queues (RabbitMQ, Kafka) - required for distributed backend systems",
      "Database optimisation - no SQL or query performance experience shown"
    ],
    "time_to_ready": "3-4 months with focus on system design and databases",
    "recommended_project": "Build a RESTful API with FastAPI, PostgreSQL, Redis caching, and background job processing - deploy on Railway with proper logging and error handling",
    "seniority_target": "Junior"
  }},
  {{
    "role_title": "DevOps Engineer",
    "match_score": 40,
    "match_reasons": [
      "Technical background provides foundation for infrastructure tooling",
      "Scripting experience transferable to automation tasks",
      "Systems thinking demonstrated in project architecture decisions"
    ],
    "skill_gaps": [
      "Linux system administration - no evidence of server management experience",
      "Kubernetes and container orchestration - core DevOps skill not present",
      "Infrastructure as Code (Terraform, Ansible) - no IaC experience shown"
    ],
    "time_to_ready": "6-9 months - significant upskilling required across multiple domains",
    "recommended_project": "Set up a complete CI/CD pipeline using GitHub Actions, Docker, and deploy a containerised app to a cloud VM with monitoring via Grafana",
    "seniority_target": "Junior"
  }}
]

Now analyse THIS specific resume:

<resume>{resume}</resume>

Remember: Return ONLY the JSON array of exactly 3 objects. Base everything on the actual resume content."""


def roadmap_prompt(resume_text: str, target_role: str, skill_gaps: list[str]) -> str:
    resume = _truncate(resume_text)
    gaps_str = ", ".join(skill_gaps) if skill_gaps else "to be inferred from resume and target role"
    return f"""You are a senior learning architect and career coach who builds precise, actionable upskilling plans.

Create a personalised 3-phase learning roadmap for this candidate targeting: "{target_role}"
Identified skill gaps: {gaps_str}

Return ONLY a valid JSON object. Do not write anything before or after the JSON. No markdown, no explanation, no code fences.

CRITICAL INSTRUCTIONS:
1. Each phase MUST contain 3-5 skills - never just 1
2. Phase 1: only skills with zero prerequisites the candidate can start TODAY
3. Phase 2: must explicitly reference building on Phase 1 work
4. Phase 3: portfolio readiness and interview prep ONLY - no brand new skill introductions
5. Never suggest skills already present in the resume
6. why_it_matters MUST reference the specific role "{target_role}" - no generic learning advice
7. resource_type must be one of: "official docs", "YouTube crash course", "Kaggle project", "open source contribution", "project-based course", "LeetCode practice", "freeCodeCamp", "GitHub project"
8. estimated_hours must be realistic (10-30 hours per skill for Phase 1, 20-50 for Phase 2)
9. total_estimated_hours must equal the sum of all skill estimated_hours across all phases

Return this exact JSON structure:
{{
  "target_role": "{target_role}",
  "current_level": "Junior",
  "phases": [
    {{
      "phase_number": 1,
      "duration": "0-30 days",
      "goal": "Build the 3 most critical foundational skills for {target_role} that require no prerequisites",
      "skills": [
        {{
          "skill_name": "SQL Fundamentals",
          "why_it_matters": "Every {target_role} role requires SQL for querying databases - it appears in 90% of job descriptions",
          "resource_type": "freeCodeCamp",
          "estimated_hours": 20
        }},
        {{
          "skill_name": "Git and GitHub workflow",
          "why_it_matters": "All {target_role} teams use Git for collaboration - you cannot get hired without it",
          "resource_type": "official docs",
          "estimated_hours": 10
        }},
        {{
          "skill_name": "REST API concepts",
          "why_it_matters": "{target_role} roles require building or consuming APIs daily - this is non-negotiable",
          "resource_type": "YouTube crash course",
          "estimated_hours": 15
        }}
      ],
      "milestone": "Complete a mini-project using all 3 Phase 1 skills and push it to GitHub with a proper README"
    }},
    {{
      "phase_number": 2,
      "duration": "1-3 months",
      "goal": "Build on Phase 1 foundations with intermediate {target_role} skills that require the Phase 1 groundwork",
      "skills": [
        {{
          "skill_name": "Docker and containerisation",
          "why_it_matters": "All modern {target_role} teams deploy with Docker - required for any mid-level position",
          "resource_type": "project-based course",
          "estimated_hours": 30
        }},
        {{
          "skill_name": "Cloud platform basics (AWS or GCP)",
          "why_it_matters": "{target_role} roles increasingly require cloud deployment knowledge - it appears in 70% of job listings",
          "resource_type": "official docs",
          "estimated_hours": 40
        }},
        {{
          "skill_name": "System design fundamentals",
          "why_it_matters": "Mid-level {target_role} interviews always include system design questions - start learning early",
          "resource_type": "YouTube crash course",
          "estimated_hours": 25
        }}
      ],
      "milestone": "Deploy a working application that uses Phase 1 + Phase 2 skills end-to-end on a free cloud tier"
    }},
    {{
      "phase_number": 3,
      "duration": "3-6 months",
      "goal": "Build a portfolio project and prepare for {target_role} technical interviews",
      "skills": [
        {{
          "skill_name": "Portfolio project development",
          "why_it_matters": "{target_role} interviewers expect a live demonstrable project - this is your proof of competence",
          "resource_type": "GitHub project",
          "estimated_hours": 60
        }},
        {{
          "skill_name": "Technical interview preparation",
          "why_it_matters": "{target_role} interviews test DSA and problem solving - 4 weeks of daily practice makes the difference",
          "resource_type": "LeetCode practice",
          "estimated_hours": 40
        }},
        {{
          "skill_name": "Open source contribution",
          "why_it_matters": "Contributing to open source proves real-world {target_role} skills to hiring managers beyond personal projects",
          "resource_type": "open source contribution",
          "estimated_hours": 30
        }}
      ],
      "milestone": "Publish a complete portfolio project with README, live demo URL, architecture diagram, and apply to 10 {target_role} positions"
    }}
  ],
  "total_estimated_hours": 270
}}

Now create the roadmap for THIS specific candidate targeting "{target_role}" with skill gaps: {gaps_str}

<resume>{resume}</resume>

Remember: Return ONLY the JSON object. Each phase must have 3-5 skills. Never just 1."""