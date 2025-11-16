from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime

def generate_resume_reportlab(user_data, categorized_projects, all_projects):
    """Gera currículo usando ReportLab"""
    
    # Informações pessoais
    personal_info = {
        'name': user_data.get('name') or 'Rudieri Machado',
        'title': 'Desenvolvedor Full Stack & Especialista em RPA',
        'email': 'rudirimachado@gmail.com',
        'phone': '(47) 99660-9407',
        'location': 'Blumenau, Santa Catarina, Brasil',
        'github': 'https://github.com/rudirimachado',
        'website': 'https://portfolio-rudieri.onrender.com'
    }
    
    # Estatísticas
    stats = {
        'total_projects': len(all_projects),
        'systems': len(categorized_projects.get('sistema', [])),
        'rpa': len(categorized_projects.get('rpa', [])),
        'apis': len(categorized_projects.get('api', [])),
        'web': len(categorized_projects.get('web', [])),
        'mobile': len(categorized_projects.get('mobile', [])),
        'languages': len(set([p.get('language', 'N/A') for p in all_projects if p.get('language') and p.get('language') != 'N/A'])),
        'years_experience': 5
    }
    
    # Buffer para PDF
    buffer = BytesIO()
    
    # Criar documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=6,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2c3e50')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#3498db')
    )
    
    contact_style = ParagraphStyle(
        'Contact',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=18,
        textColor=colors.HexColor('#2c3e50'),
        borderWidth=1,
        borderColor=colors.HexColor('#3498db'),
        borderPadding=6
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    # Conteúdo do documento
    story = []
    
    # Header
    story.append(Paragraph(personal_info['name'], title_style))
    story.append(Paragraph(personal_info['title'], subtitle_style))
    
    # Contatos
    contact_info = f"""
    📧 {personal_info['email']} | 📱 {personal_info['phone']} | 📍 {personal_info['location']}<br/>
    🐙 GitHub: {personal_info['github']} | 🌐 Portfolio: {personal_info['website']}
    """
    story.append(Paragraph(contact_info, contact_style))
    story.append(Spacer(1, 20))
    
    # Estatísticas
    story.append(Paragraph("📊 Estatísticas Profissionais", section_style))
    
    stats_data = [
        ['Projetos Totais', 'Anos Experiência', 'Sistemas', 'Automações RPA'],
        [str(stats['total_projects']), str(stats['years_experience']) + '+', str(stats['systems']), str(stats['rpa'])],
        ['APIs', 'Web Apps', 'Mobile', 'Linguagens'],
        [str(stats['apis']), str(stats['web']), str(stats['mobile']), str(stats['languages'])]
    ]
    
    stats_table = Table(stats_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 15))
    
    # Perfil Profissional
    story.append(Paragraph("👨‍💻 Perfil Profissional", section_style))
    
    profile_text = """
    Desenvolvedor Full Stack apaixonado por tecnologia e inovação, com mais de 5 anos de experiência 
    em desenvolvimento de software e especialização em automação RPA (Robotic Process Automation). 
    
    Criador e arquiteto principal do ERP SYSROHDEN, um sistema empresarial robusto que atende 
    múltiplas empresas, demonstrando capacidade de liderança técnica e visão estratégica de produto.
    
    Especialista em transformação digital, com foco em otimização de processos através de automação 
    inteligente. Combino conhecimento técnico sólido com habilidades de comunicação e trabalho em equipe, 
    sempre buscando soluções inovadoras que agreguem valor real aos negócios.
    """
    
    story.append(Paragraph(profile_text, normal_style))
    story.append(Spacer(1, 15))
    
    # Experiência Profissional
    story.append(Paragraph("💼 Experiência Profissional", section_style))
    
    exp_title = ParagraphStyle(
        'ExpTitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=3,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica-Bold'
    )
    
    exp_company = ParagraphStyle(
        'ExpCompany',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        textColor=colors.HexColor('#3498db')
    )
    
    story.append(Paragraph("Desenvolvedor Full Stack & Especialista RPA", exp_title))
    story.append(Paragraph("SYSROHDEN ERP | 2019 - Presente (5+ anos) | Blumenau, SC", exp_company))
    
    achievements = f"""
    • Criador e arquiteto principal do ERP SYSROHDEN<br/>
    • Desenvolveu {stats['total_projects']} projetos em diversas tecnologias<br/>
    • Criou {stats['rpa']} automações RPA que economizam mais de 2000 horas/mês<br/>
    • Arquitetou {stats['systems']} sistemas completos para gestão empresarial<br/>
    • Desenvolveu {stats['apis']} APIs RESTful para integração de sistemas<br/>
    • Liderou equipe de desenvolvimento em projetos críticos<br/>
    • Implementou práticas de DevOps e CI/CD<br/>
    • Responsável pela arquitetura de software e tomada de decisões técnicas
    """
    
    story.append(Paragraph(achievements, normal_style))
    story.append(Spacer(1, 10))
    
    # Experiência Freelance
    story.append(Paragraph("Desenvolvedor de Automação", exp_title))
    story.append(Paragraph("Projetos Freelance | 2018 - 2019 | Remoto", exp_company))
    
    freelance_achievements = """
    • Automatizou processos financeiros e contábeis<br/>
    • Desenvolveu bots para extração e processamento de dados<br/>
    • Integrou sistemas legados com novas tecnologias<br/>
    • Reduziu tempo de processamento manual em até 80%
    """
    
    story.append(Paragraph(freelance_achievements, normal_style))
    story.append(Spacer(1, 15))
    
    # Formação
    story.append(Paragraph("🎓 Formação Acadêmica", section_style))
    
    education_data = [
        ['Curso', 'Instituição', 'Período', 'Status'],
        ['Tecnólogo em Análise e Desenvolvimento de Sistemas', 'FURB - Universidade Regional de Blumenau', '2017 - 2020', 'Concluído'],
        ['Curso Técnico em Informática', 'SENAI - Blumenau', '2015 - 2017', 'Concluído']
    ]
    
    education_table = Table(education_data, colWidths=[2.5*inch, 2*inch, 1.2*inch, 1*inch])
    education_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(education_table)
    story.append(Spacer(1, 15))
    
    # Competências Técnicas
    story.append(Paragraph("💻 Competências Técnicas", section_style))
    
    tech_data = [
        ['Categoria', 'Tecnologias'],
        ['Backend', 'Python, Java, C#, Node.js, PHP'],
        ['Frontend', 'JavaScript, React, Vue.js, HTML, CSS'],
        ['Database', 'PostgreSQL, MySQL, MongoDB, SQLite'],
        ['DevOps', 'Docker, Git, Linux, AWS, Heroku'],
        ['Automation', 'Selenium, BeautifulSoup, Pandas, Requests']
    ]
    
    tech_table = Table(tech_data, colWidths=[1.5*inch, 5*inch])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(tech_table)
    story.append(Spacer(1, 15))
    
    # Características Pessoais
    story.append(Paragraph("🌟 Características Pessoais", section_style))
    
    personality_text = """
    🎯 Orientado a resultados e focado em entrega de valor<br/>
    🚀 Proativo na identificação e solução de problemas<br/>
    🤝 Excelente trabalho em equipe e comunicação interpessoal<br/>
    📚 Aprendizado contínuo e adaptação a novas tecnologias<br/>
    💡 Pensamento analítico e criativo para soluções inovadoras<br/>
    ⚡ Capacidade de trabalhar sob pressão e cumprir prazos<br/>
    🔍 Atenção aos detalhes e qualidade de código<br/>
    🌟 Liderança técnica e mentoria de desenvolvedores juniores
    """
    
    story.append(Paragraph(personality_text, normal_style))
    story.append(Spacer(1, 15))
    
    # Projetos Destacados
    story.append(Paragraph("🚀 Projetos Destacados", section_style))
    
    # Pegar top projetos
    featured_projects = []
    for category, projects in categorized_projects.items():
        for project in projects[:2]:  # Top 2 de cada categoria
            if len(featured_projects) < 8:
                featured_projects.append({
                    'title': project['title'],
                    'description': project['description'][:80] + '...' if len(project['description']) > 80 else project['description'],
                    'category': category.title(),
                    'language': project.get('language', 'N/A')
                })
    
    for i, project in enumerate(featured_projects):
        if i % 2 == 0 and i > 0:  # Quebra de linha a cada 2 projetos
            story.append(Spacer(1, 8))
        
        project_text = f"<b>{project['title']}</b> ({project['category']} - {project['language']})<br/>{project['description']}"
        story.append(Paragraph(project_text, normal_style))
        story.append(Spacer(1, 6))
    
    # Footer
    story.append(Spacer(1, 20))
    footer_text = f"""
    <i>Currículo gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}<br/>
    Portfolio completo disponível em: {personal_info['website']}</i>
    """
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    story.append(Paragraph(footer_text, footer_style))
    
    # Construir PDF
    doc.build(story)
    
    # Retornar dados do PDF
    buffer.seek(0)
    return buffer.getvalue()
