from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO

def generate_pdf_report(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = styles['Title']
    story.append(Paragraph("SkyRocket Analytics Report", title_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Executive Summary", styles['Heading2']))
    
    summary_data = [
        ['Metric', 'Value'],
        ['Total Queries', str(data['data_summary']['total_queries'])],
        ['Unique Queries', str(data['data_summary']['unique_queries'])],
    ]
    
    if data.get('evaluation'):
        summary_data.extend([
            ['Containment Rate', f"{data['evaluation']['containment_rate']:.1f}%"],
            ['Avg Quality Score', f"{data['evaluation']['avg_overall_quality']:.1f}/5.0"],
            ['Hallucination Rate', f"{data['evaluation']['hallucination_rate']:.1f}%"]
        ])

    t = Table(summary_data, colWidths=[3*inch, 3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Top Discovered Topics", styles['Heading2']))
    
    topics_data = [['Rank', 'Topic', 'Count', 'Percentage']]
    for topic in data['topics']['topics'][:10]:
        topics_data.append([
            str(topic['rank']),
            topic['topic_name'],
            str(topic['count']),
            f"{topic['percentage']:.1f}%"
        ])

    t_topics = Table(topics_data, colWidths=[0.5*inch, 3.5*inch, 1*inch, 1*inch])
    t_topics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(t_topics)
    story.append(Spacer(1, 20))

    if data.get('entities') and data['entities'].get('entity_counts'):
        story.append(Paragraph("Top Entities", styles['Heading2']))
        entity_data = [['Entity Type', 'Count']]
        sorted_entities = sorted(data['entities']['entity_counts'].items(), key=lambda x: x[1], reverse=True)[:10]
        for entity, count in sorted_entities:
            entity_data.append([entity.replace('_', ' ').title(), str(count)])
        
        t_entities = Table(entity_data, colWidths=[4*inch, 2*inch])
        t_entities.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(t_entities)

    doc.build(story)
    buffer.seek(0)
    return buffer
