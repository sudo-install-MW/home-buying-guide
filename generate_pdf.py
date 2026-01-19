#!/usr/bin/env python3
"""
Home Buying Readiness Report - PDF Generator
Generates a beautiful PDF report from calculator results
"""

import json
import sys
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def create_pdf_report(data, output_path="home_buying_report.pdf"):
    """Generate a beautiful PDF report from the calculator data."""

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Define colors
    primary_color = colors.HexColor("#2563eb")
    success_color = colors.HexColor("#10b981")
    warning_color = colors.HexColor("#f59e0b")
    danger_color = colors.HexColor("#ef4444")
    gray_color = colors.HexColor("#6b7280")
    light_gray = colors.HexColor("#f3f4f6")
    dark_gray = colors.HexColor("#1f2937")

    # Define styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=primary_color,
        alignment=TA_CENTER,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=gray_color,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=dark_gray,
        spaceBefore=20,
        spaceAfter=10,
        borderPadding=5
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=dark_gray,
        spaceAfter=8
    )

    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=10,
        textColor=gray_color
    )

    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=12,
        textColor=dark_gray,
        fontName='Helvetica-Bold'
    )

    # Build the document
    story = []

    # Header
    story.append(Paragraph("🏠 Home Buying Readiness Report", title_style))
    story.append(Paragraph(f"Generated on {data.get('generatedAt', datetime.now().strftime('%B %d, %Y at %I:%M %p'))}", subtitle_style))

    # Divider
    story.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceBefore=10, spaceAfter=20))

    # Affordability Verdict Box
    verdict = data.get('readinessStatus', '')
    if '✅' in verdict or 'Ready' in verdict:
        verdict_color = success_color
        verdict_bg = colors.HexColor("#d1fae5")
    elif '🔶' in verdict or 'Almost' in verdict:
        verdict_color = warning_color
        verdict_bg = colors.HexColor("#fef3c7")
    else:
        verdict_color = danger_color
        verdict_bg = colors.HexColor("#fee2e2")

    verdict_style = ParagraphStyle(
        'Verdict',
        parent=styles['Normal'],
        fontSize=18,
        textColor=verdict_color,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    target_price = data.get('targetHomePrice', '0')
    if target_price and target_price != '0':
        target_price_formatted = f"${int(float(target_price)):,}"
    else:
        target_price_formatted = "N/A"

    verdict_table = Table(
        [[Paragraph(f"Target Home Price: {target_price_formatted}", subtitle_style)],
         [Paragraph(verdict.replace('✅', '✓').replace('🔶', '⚠').replace('🔴', '✗'), verdict_style)]],
        colWidths=[6.5*inch]
    )
    verdict_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), verdict_bg),
        ('BOX', (0, 0), (-1, -1), 2, verdict_color),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(verdict_table)
    story.append(Spacer(1, 20))

    # Key Results Section
    story.append(Paragraph("📊 Key Results", section_header_style))

    results_data = [
        ['Monthly Payment', data.get('monthlyPayment', 'N/A')],
        ['Down Payment Needed', data.get('downPaymentNeeded', 'N/A')],
        ['Closing Costs (Est.)', data.get('closingCosts', 'N/A')],
        ['Total Cash Needed', data.get('totalCashNeeded', 'N/A')],
    ]

    results_table = Table(results_data, colWidths=[3.25*inch, 3.25*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), light_gray),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (0, -1), gray_color),
        ('TEXTCOLOR', (1, 0), (1, -1), dark_gray),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(results_table)
    story.append(Spacer(1, 20))

    # DTI Analysis Section
    story.append(Paragraph("📈 Debt-to-Income Analysis", section_header_style))

    dti = data.get('dti', {})
    housing_dti = dti.get('housingDTI', 'N/A')
    total_dti = dti.get('totalDTI', 'N/A')

    # Determine DTI status colors
    def get_dti_color(dti_str, threshold):
        try:
            dti_val = float(dti_str.replace('%', ''))
            if dti_val <= threshold:
                return success_color
            elif dti_val <= threshold + 7:
                return warning_color
            else:
                return danger_color
        except:
            return gray_color

    housing_color = get_dti_color(housing_dti, 28)
    total_color = get_dti_color(total_dti, 36)

    dti_data = [
        ['Metric', 'Your Value', 'Recommended Max', 'Status'],
        ['Housing DTI', housing_dti, '28%', '✓ Good' if housing_color == success_color else ('⚠ High' if housing_color == warning_color else '✗ Too High')],
        ['Total DTI', total_dti, '36%', '✓ Good' if total_color == success_color else ('⚠ High' if total_color == warning_color else '✗ Too High')],
    ]

    dti_table = Table(dti_data, colWidths=[1.6*inch, 1.6*inch, 1.6*inch, 1.6*inch])
    dti_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), dark_gray),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(dti_table)

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<i>Housing DTI: Percentage of income going to housing costs. Total DTI: Percentage including all debts.</i>",
        ParagraphStyle('Note', parent=normal_style, fontSize=9, textColor=gray_color)
    ))
    story.append(Spacer(1, 20))

    # Your Financial Profile Section
    story.append(Paragraph("💰 Your Financial Profile", section_header_style))

    inputs = data.get('inputs', {})

    income_data = [
        ['Income Information', ''],
        ['Annual Gross Income', f"${int(float(inputs.get('annualIncome', 0) or 0)):,}"],
        ['Additional Income', f"${int(float(inputs.get('additionalIncome', 0) or 0)):,}"],
        ['Credit Score', inputs.get('creditScore', 'N/A')],
        ['Total Savings', f"${int(float(inputs.get('totalSavings', 0) or 0)):,}"],
        ['Monthly Savings Rate', f"${int(float(inputs.get('monthlySavings', 0) or 0)):,}"],
    ]

    income_table = Table(income_data, colWidths=[3.25*inch, 3.25*inch])
    income_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('SPAN', (0, 0), (1, 0)),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('BACKGROUND', (0, 1), (0, -1), light_gray),
        ('TEXTCOLOR', (0, 1), (0, -1), gray_color),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(income_table)
    story.append(Spacer(1, 15))

    # Monthly Debts
    debts = data.get('monthlyDebts', {})

    debts_data = [
        ['Monthly Debt Payments', ''],
        ['Car Payment(s)', f"${int(float(debts.get('carPayment', 0) or 0)):,}"],
        ['Student Loans', f"${int(float(debts.get('studentLoans', 0) or 0)):,}"],
        ['Credit Card Minimums', f"${int(float(debts.get('creditCards', 0) or 0)):,}"],
        ['Other Debts', f"${int(float(debts.get('otherDebt', 0) or 0)):,}"],
    ]

    # Calculate total monthly debt
    total_debt = sum([
        float(debts.get('carPayment', 0) or 0),
        float(debts.get('studentLoans', 0) or 0),
        float(debts.get('creditCards', 0) or 0),
        float(debts.get('otherDebt', 0) or 0)
    ])
    debts_data.append(['Total Monthly Debt', f"${int(total_debt):,}"])

    debts_table = Table(debts_data, colWidths=[3.25*inch, 3.25*inch])
    debts_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#7c3aed")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('SPAN', (0, 0), (1, 0)),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('BACKGROUND', (0, 1), (0, -1), light_gray),
        ('TEXTCOLOR', (0, 1), (0, -1), gray_color),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#ede9fe")),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(debts_table)
    story.append(Spacer(1, 20))

    # Loan Details Section
    story.append(Paragraph("📋 Loan Configuration", section_header_style))

    loan_data = [
        ['Down Payment', inputs.get('downPaymentPercent', 'N/A')],
        ['Loan Type', inputs.get('loanType', 'N/A').title()],
        ['Loan Term', inputs.get('loanTerm', 'N/A')],
        ['Interest Rate', inputs.get('interestRate', 'N/A')],
    ]

    loan_table = Table(loan_data, colWidths=[3.25*inch, 3.25*inch])
    loan_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), light_gray),
        ('TEXTCOLOR', (0, 0), (0, -1), gray_color),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e5e7eb")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(loan_table)
    story.append(Spacer(1, 25))

    # Next Steps Section
    story.append(Paragraph("📝 Recommended Next Steps", section_header_style))

    next_steps = []

    # Generate personalized next steps based on the data
    try:
        savings = float(inputs.get('totalSavings', 0) or 0)
        total_cash = data.get('totalCashNeeded', '$0').replace('$', '').replace(',', '')
        total_cash_float = float(total_cash) if total_cash else 0

        if savings < total_cash_float:
            gap = total_cash_float - savings
            next_steps.append(f"Save ${int(gap):,} more for down payment, closing costs, and reserves")
    except:
        pass

    try:
        credit_score = int(inputs.get('creditScore', 0) or 0)
        if credit_score < 700:
            next_steps.append("Work on improving your credit score above 700 for better interest rates")
        elif credit_score >= 700:
            next_steps.append("Your credit score is good - consider getting pre-approved for a mortgage")
    except:
        pass

    if '✅' in verdict or 'Ready' in verdict:
        next_steps.append("You're ready! Start interviewing real estate agents in your target area")
        next_steps.append("Get pre-approved with 2-3 lenders to compare rates")
    elif '🔶' in verdict or 'Almost' in verdict:
        next_steps.append("Consider paying down existing debts to improve your DTI ratio")
        next_steps.append("Continue saving while monitoring interest rates")
    else:
        next_steps.append("Focus on increasing income or reducing monthly debts")
        next_steps.append("Consider looking at homes in a lower price range")

    for i, step in enumerate(next_steps, 1):
        bullet_style = ParagraphStyle(
            'Bullet',
            parent=normal_style,
            fontSize=11,
            leftIndent=20,
            spaceBefore=5,
            spaceAfter=5
        )
        story.append(Paragraph(f"<b>{i}.</b> {step}", bullet_style))

    story.append(Spacer(1, 30))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=gray_color, spaceBefore=10, spaceAfter=10))

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=gray_color,
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        "This report is for informational purposes only and does not constitute financial advice.<br/>"
        "Consult with a mortgage professional for personalized guidance.",
        footer_style
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Generated by Home Buying Readiness Calculator",
        footer_style
    ))

    # Build the PDF
    doc.build(story)
    return output_path


if __name__ == "__main__":
    # Read JSON data from stdin or file
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            data = json.load(f)
        output_path = sys.argv[2] if len(sys.argv) > 2 else "home_buying_report.pdf"
    else:
        data = json.load(sys.stdin)
        output_path = "home_buying_report.pdf"

    create_pdf_report(data, output_path)
    print(f"PDF generated: {output_path}")
