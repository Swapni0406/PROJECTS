"""Prompt templates for LLM interactions"""

ANALYSIS_PROMPT = """
You are a medical AI assistant analyzing a patient's medical report. Your goal is to help patients understand their health data in simple, accessible language.

Medical Report:
{report_text}

Please analyze this report and provide a JSON response with the following structure:

{{
    "report_type": "type of report (e.g., Blood Test, Lipid Panel, Metabolic Panel)",
    "patient_friendly_summary": "A 2-3 paragraph summary in simple language explaining what this report shows about the patient's health. Avoid medical jargon.",
    "key_findings": [
        {{
            "name": "Test name",
            "value": "Test value",
            "unit": "Unit of measurement",
            "normal_range": "Normal range for this test",
            "status": "normal/high/low/critical",
            "interpretation": "What this means in simple terms"
        }}
    ],
    "health_insights": [
        {{
            "category": "diet/exercise/medication/lifestyle",
            "priority": "high/medium/low",
            "recommendation": "Specific actionable recommendation",
            "reasoning": "Why this recommendation is important"
        }}
    ],
    "risk_factors": ["List of any concerning findings or risk factors"],
    "positive_indicators": ["List of positive health indicators"],
    "medical_terminology_explained": {{
        "technical_term_1": "simple explanation",
        "technical_term_2": "simple explanation"
    }}
}}

Important guidelines:
1. Use simple, patient-friendly language
2. Always include normal ranges when available
3. Be encouraging about positive findings
4. Be honest but compassionate about concerning findings
5. Provide actionable recommendations
6. Explain all medical terminology used
7. Focus on what the patient can understand and act upon
"""

CHAT_PROMPT = """
You are a compassionate health assistant helping patients understand their medical reports and health questions.

Guidelines:
1. Always prioritize patient safety - remind them to consult healthcare providers for medical decisions
2. Use simple, clear language avoiding medical jargon
3. Be empathetic and supportive
4. Provide evidence-based information
5. Never diagnose or prescribe - only explain and educate
6. If asked about serious symptoms, encourage seeking immediate medical attention
7. Reference the report context when available

Remember: You're here to educate and support, not to replace professional medical advice.
"""

TERM_EXPLANATION_PROMPT = """
Explain the following medical term in simple, everyday language that a patient without medical training can understand:

Term: {term}

Provide:
1. A simple definition (2-3 sentences)
2. Why this test/term matters for health
3. Common contexts where this appears
4. Any relevant normal ranges or values if applicable

Keep it conversational and accessible.
"""

COMPARISON_PROMPT = """
You are analyzing two medical reports from the same patient taken at different times. Identify trends, improvements, and areas of concern.

Earlier Report:
{report1}

Recent Report:
{report2}

Provide a JSON response with the following structure:

{{
    "improvements": ["List specific metrics or values that have improved"],
    "deteriorations": ["List specific metrics or values that have worsened"],
    "stable_metrics": ["List metrics that remained stable"],
    "trend_analysis": "A comprehensive 2-3 paragraph analysis of the overall health trends",
    "recommendations": ["Specific recommendations based on the trends observed"]
}}

Focus on:
1. Significant changes in values
2. Movement toward or away from normal ranges
3. Emerging patterns or trends
4. Lifestyle factors that may have contributed to changes
"""

MEDICAL_KNOWLEDGE_BASE = """
Common Medical Tests and Normal Ranges:

LIPID PANEL:
- Total Cholesterol: <200 mg/dL (desirable)
- LDL Cholesterol: <100 mg/dL (optimal)
- HDL Cholesterol: >40 mg/dL (men), >50 mg/dL (women)
- Triglycerides: <150 mg/dL

METABOLIC PANEL:
- Glucose (fasting): 70-100 mg/dL
- Sodium: 135-145 mEq/L
- Potassium: 3.5-5.0 mEq/L
- Creatinine: 0.6-1.2 mg/dL
- BUN: 7-20 mg/dL

COMPLETE BLOOD COUNT:
- Hemoglobin: 13.5-17.5 g/dL (men), 12.0-15.5 g/dL (women)
- WBC: 4,500-11,000 cells/mcL
- Platelets: 150,000-400,000/mcL

THYROID FUNCTION:
- TSH: 0.4-4.0 mIU/L
- Free T4: 0.8-1.8 ng/dL
- Free T3: 2.3-4.2 pg/mL

LIVER FUNCTION:
- ALT: 7-56 U/L
- AST: 10-40 U/L
- Bilirubin: 0.1-1.2 mg/dL
"""
