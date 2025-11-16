from datetime import datetime
import json

try:
    from weasyprint import HTML, CSS
    from io import BytesIO
    WEASYPRINT_AVAILABLE = True
    print("✅ WeasyPrint carregado")
except Exception as e:
    WEASYPRINT_AVAILABLE = False
    print(f"⚠️ WeasyPrint não disponível: {e}")

try:
    from pdf_generator_reportlab import generate_resume_reportlab
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab não disponível")

def generate_complete_resume(user_data, categorized_projects, all_projects):
    """Gera um currículo completo e detalhado em PDF"""
    
    # Informações pessoais expandidas
    personal_info = {
        'name': user_data.get('name') or 'Rudieri Machado',
        'title': 'Desenvolvedor Full Stack & Especialista em RPA',
        'email': 'rudirimachado@gmail.com',
        'phone': '(47) 99660-9407',
        'location': 'Blumenau, Santa Catarina, Brasil',
        'github': user_data.get('html_url') or 'https://github.com/rudirimachado',
        'instagram': 'https://www.instagram.com/rudieri.machado',
        'linkedin': 'https://www.linkedin.com/in/rudieri-machado',
        'website': 'https://portfolio-rudieri.onrender.com'
    }
    
    # Perfil profissional detalhado
    professional_summary = """
    Desenvolvedor Full Stack apaixonado por tecnologia e inovação, com mais de 5 anos de experiência 
    em desenvolvimento de software e especialização em automação RPA (Robotic Process Automation). 
    
    Criador e arquiteto principal do ERP SYSROHDEN, um sistema empresarial robusto que atende 
    múltiplas empresas, demonstrando capacidade de liderança técnica e visão estratégica de produto.
    
    Especialista em transformação digital, com foco em otimização de processos através de automação 
    inteligente. Combino conhecimento técnico sólido com habilidades de comunicação e trabalho em equipe, 
    sempre buscando soluções inovadoras que agreguem valor real aos negócios.
    """
    
    # Características pessoais e soft skills
    personality_traits = [
        "🎯 Orientado a resultados e focado em entrega de valor",
        "🚀 Proativo na identificação e solução de problemas",
        "🤝 Excelente trabalho em equipe e comunicação interpessoal", 
        "📚 Aprendizado contínuo e adaptação a novas tecnologias",
        "💡 Pensamento analítico e criativo para soluções inovadoras",
        "⚡ Capacidade de trabalhar sob pressão e cumprir prazos",
        "🔍 Atenção aos detalhes e qualidade de código",
        "🌟 Liderança técnica e mentoria de desenvolvedores juniores"
    ]
    
    # Estatísticas expandidas
    stats = {
        'total_projects': len(all_projects),
        'systems': len(categorized_projects['sistema']),
        'rpa': len(categorized_projects['rpa']),
        'apis': len(categorized_projects['api']),
        'web': len(categorized_projects['web']),
        'mobile': len(categorized_projects['mobile']),
        'languages': len(set([p.get('language', 'N/A') for p in all_projects if p.get('language') and p.get('language') != 'N/A'])),
        'years_experience': 5,
        'companies_served': 10,
        'automation_hours_saved': 2000
    }
    
    # Experiência profissional detalhada
    work_experience = [
        {
            'title': 'Desenvolvedor Full Stack & Especialista RPA',
            'company': 'SYSROHDEN ERP',
            'period': '2019 - Presente (5+ anos)',
            'location': 'Blumenau, SC',
            'description': 'Criador e arquiteto principal do ERP SYSROHDEN',
            'achievements': [
                f'Desenvolveu {stats["total_projects"]} projetos em diversas tecnologias',
                f'Criou {stats["rpa"]} automações RPA que economizam mais de 2000 horas/mês',
                f'Arquitetou {stats["systems"]} sistemas completos para gestão empresarial',
                f'Desenvolveu {stats["apis"]} APIs RESTful para integração de sistemas',
                f'Liderou equipe de desenvolvimento em projetos críticos',
                'Implementou práticas de DevOps e CI/CD',
                'Responsável pela arquitetura de software e tomada de decisões técnicas'
            ]
        },
        {
            'title': 'Desenvolvedor de Automação',
            'company': 'Projetos Freelance',
            'period': '2018 - 2019',
            'location': 'Remoto',
            'description': 'Desenvolvimento de soluções de automação para pequenas e médias empresas',
            'achievements': [
                'Automatizou processos financeiros e contábeis',
                'Desenvolveu bots para extração e processamento de dados',
                'Integrou sistemas legados com novas tecnologias',
                'Reduziu tempo de processamento manual em até 80%'
            ]
        }
    ]
    
    # Educação e certificações
    education = [
        {
            'degree': 'Tecnólogo em Análise e Desenvolvimento de Sistemas',
            'institution': 'FURB - Universidade Regional de Blumenau',
            'period': '2017 - 2020',
            'status': 'Concluído'
        },
        {
            'degree': 'Curso Técnico em Informática',
            'institution': 'SENAI - Blumenau',
            'period': '2015 - 2017',
            'status': 'Concluído'
        }
    ]
    
    # Projetos destacados com mais detalhes
    featured_projects = []
    for category, projects in categorized_projects.items():
        for project in projects[:2]:  # Top 2 de cada categoria
            if project.get('featured') or len(featured_projects) < 10:
                featured_projects.append({
                    'title': project['title'],
                    'description': project['description'],
                    'category': category.title(),
                    'language': project.get('language', 'N/A'),
                    'github_url': project.get('github_url', ''),
                    'demo_url': project.get('demo_url', ''),
                    'tags': project.get('tags', []),
                    'stars': project.get('stars', 0),
                    'featured': project.get('featured', False),
                    'impact': f"Projeto {category} que demonstra expertise em {project.get('language', 'desenvolvimento')}"
                })
    
    # Ordenar projetos
    featured_projects.sort(key=lambda x: (not x.get('featured', False), -x.get('stars', 0)))
    featured_projects = featured_projects[:8]
    
    # Tecnologias organizadas por categoria
    language_count = {}
    for project in all_projects:
        lang = project.get('language')
        if lang and lang != 'N/A':
            language_count[lang] = language_count.get(lang, 0) + 1
    
    tech_categories = {
        'Backend': ['Python', 'Java', 'C#', 'Node.js', 'PHP'],
        'Frontend': ['JavaScript', 'React', 'Vue.js', 'HTML', 'CSS'],
        'Database': ['PostgreSQL', 'MySQL', 'MongoDB', 'SQLite'],
        'DevOps': ['Docker', 'Git', 'Linux', 'AWS', 'Heroku'],
        'Automation': ['Selenium', 'BeautifulSoup', 'Pandas', 'Requests']
    }
    
    # HTML do currículo
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Currículo - {personal_info['name']}</title>
        <style>
            @page {{
                size: A4;
                margin: 1cm;
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Arial', sans-serif;
                line-height: 1.4;
                color: #333;
                font-size: 11px;
            }}
            
            .header {{
                background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                color: white;
                padding: 20px;
                text-align: center;
                margin-bottom: 20px;
            }}
            
            .header h1 {{
                font-size: 24px;
                margin-bottom: 5px;
                font-weight: bold;
            }}
            
            .header h2 {{
                font-size: 14px;
                margin-bottom: 15px;
                opacity: 0.9;
            }}
            
            .contact-info {{
                display: flex;
                justify-content: center;
                gap: 15px;
                flex-wrap: wrap;
                font-size: 10px;
            }}
            
            .contact-item {{
                display: flex;
                align-items: center;
                gap: 5px;
            }}
            
            .section {{
                margin-bottom: 20px;
                page-break-inside: avoid;
            }}
            
            .section h3 {{
                color: #2c3e50;
                font-size: 14px;
                margin-bottom: 10px;
                padding-bottom: 5px;
                border-bottom: 2px solid #3498db;
                font-weight: bold;
            }}
            
            .two-column {{
                display: flex;
                gap: 20px;
            }}
            
            .column {{
                flex: 1;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
                margin-bottom: 15px;
            }}
            
            .stat-card {{
                background: #f8f9fa;
                padding: 10px;
                text-align: center;
                border-radius: 5px;
                border-left: 3px solid #3498db;
            }}
            
            .stat-number {{
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
            }}
            
            .stat-label {{
                font-size: 9px;
                color: #666;
                margin-top: 2px;
            }}
            
            .experience-item {{
                margin-bottom: 15px;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 5px;
                border-left: 3px solid #3498db;
            }}
            
            .experience-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 5px;
            }}
            
            .experience-title {{
                font-weight: bold;
                color: #2c3e50;
                font-size: 12px;
            }}
            
            .experience-period {{
                font-size: 10px;
                color: #666;
            }}
            
            .experience-company {{
                font-size: 11px;
                color: #3498db;
                margin-bottom: 5px;
            }}
            
            .achievements {{
                list-style: none;
                padding-left: 0;
            }}
            
            .achievements li {{
                margin-bottom: 3px;
                padding-left: 15px;
                position: relative;
                font-size: 10px;
            }}
            
            .achievements li:before {{
                content: "▶";
                color: #3498db;
                position: absolute;
                left: 0;
            }}
            
            .project-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }}
            
            .project-card {{
                background: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                border-left: 3px solid #e74c3c;
            }}
            
            .project-title {{
                font-weight: bold;
                color: #2c3e50;
                font-size: 11px;
                margin-bottom: 3px;
            }}
            
            .project-category {{
                background: #3498db;
                color: white;
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 8px;
                display: inline-block;
                margin-bottom: 5px;
            }}
            
            .project-description {{
                font-size: 9px;
                color: #666;
                margin-bottom: 5px;
            }}
            
            .project-tech {{
                font-size: 8px;
                color: #3498db;
                font-weight: bold;
            }}
            
            .tech-category {{
                margin-bottom: 10px;
            }}
            
            .tech-category h4 {{
                font-size: 11px;
                color: #2c3e50;
                margin-bottom: 5px;
            }}
            
            .tech-list {{
                display: flex;
                flex-wrap: wrap;
                gap: 5px;
            }}
            
            .tech-item {{
                background: #ecf0f1;
                padding: 3px 8px;
                border-radius: 10px;
                font-size: 9px;
                color: #2c3e50;
            }}
            
            .personality-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 5px;
            }}
            
            .personality-item {{
                font-size: 10px;
                padding: 5px;
                background: #f8f9fa;
                border-radius: 3px;
                border-left: 2px solid #27ae60;
            }}
            
            .education-item {{
                margin-bottom: 10px;
                padding: 8px;
                background: #f8f9fa;
                border-radius: 5px;
                border-left: 3px solid #f39c12;
            }}
            
            .education-degree {{
                font-weight: bold;
                color: #2c3e50;
                font-size: 11px;
            }}
            
            .education-institution {{
                color: #3498db;
                font-size: 10px;
            }}
            
            .education-period {{
                color: #666;
                font-size: 9px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{personal_info['name']}</h1>
            <h2>{personal_info['title']}</h2>
            <div class="contact-info">
                <div class="contact-item">📧 {personal_info['email']}</div>
                <div class="contact-item">📱 {personal_info['phone']}</div>
                <div class="contact-item">📍 {personal_info['location']}</div>
                <div class="contact-item">🐙 GitHub</div>
                <div class="contact-item">📷 Instagram</div>
                <div class="contact-item">🌐 Portfolio</div>
            </div>
        </div>
        
        <div class="section">
            <h3>📊 Estatísticas Profissionais</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['years_experience']}+</div>
                    <div class="stat-label">Anos Experiência</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['total_projects']}</div>
                    <div class="stat-label">Projetos Desenvolvidos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['rpa']}</div>
                    <div class="stat-label">Automações RPA</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['systems']}</div>
                    <div class="stat-label">Sistemas Completos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['languages']}</div>
                    <div class="stat-label">Linguagens</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">2000+</div>
                    <div class="stat-label">Horas Economizadas</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h3>👨‍💻 Perfil Profissional</h3>
            <p style="text-align: justify; font-size: 10px; line-height: 1.4;">{professional_summary.strip()}</p>
        </div>
        
        <div class="two-column">
            <div class="column">
                <div class="section">
                    <h3>💼 Experiência Profissional</h3>"""
    
    # Adicionar experiências
    for exp in work_experience:
        html_content += f"""
                    <div class="experience-item">
                        <div class="experience-header">
                            <div>
                                <div class="experience-title">{exp['title']}</div>
                                <div class="experience-company">{exp['company']} - {exp['location']}</div>
                            </div>
                            <div class="experience-period">{exp['period']}</div>
                        </div>
                        <p style="font-size: 10px; margin-bottom: 5px;">{exp['description']}</p>
                        <ul class="achievements">"""
        
        for achievement in exp['achievements']:
            html_content += f"<li>{achievement}</li>"
        
        html_content += """
                        </ul>
                    </div>"""
    
    html_content += """
                </div>
                
                <div class="section">
                    <h3>🎓 Formação Acadêmica</h3>"""
    
    # Adicionar educação
    for edu in education:
        html_content += f"""
                    <div class="education-item">
                        <div class="education-degree">{edu['degree']}</div>
                        <div class="education-institution">{edu['institution']}</div>
                        <div class="education-period">{edu['period']} - {edu['status']}</div>
                    </div>"""
    
    html_content += """
                </div>
            </div>
            
            <div class="column">
                <div class="section">
                    <h3>💻 Competências Técnicas</h3>"""
    
    # Adicionar tecnologias por categoria
    for category, techs in tech_categories.items():
        html_content += f"""
                    <div class="tech-category">
                        <h4>{category}</h4>
                        <div class="tech-list">"""
        
        for tech in techs:
            count = language_count.get(tech, 0)
            if count > 0 or tech in ['Docker', 'Git', 'Linux', 'PostgreSQL', 'HTML', 'CSS']:
                html_content += f'<div class="tech-item">{tech}</div>'
        
        html_content += """
                        </div>
                    </div>"""
    
    html_content += """
                </div>
                
                <div class="section">
                    <h3>🌟 Características Pessoais</h3>
                    <div class="personality-grid">"""
    
    # Adicionar características pessoais
    for trait in personality_traits:
        html_content += f'<div class="personality-item">{trait}</div>'
    
    html_content += """
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h3>🚀 Projetos Destacados</h3>
            <div class="project-grid">"""
    
    # Adicionar projetos destacados
    for project in featured_projects:
        stars_display = f"⭐ {project['stars']}" if project['stars'] > 0 else ""
        featured_badge = "🌟 DESTAQUE" if project.get('featured') else ""
        
        html_content += f"""
                <div class="project-card">
                    <div class="project-title">{project['title']} {featured_badge}</div>
                    <div class="project-category">{project['category']}</div>
                    <div class="project-description">{project['description'][:100]}...</div>
                    <div class="project-tech">{project['language']} {stars_display}</div>
                </div>"""
    
    html_content += f"""
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px; font-size: 9px; color: #666;">
            <p>Currículo gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
            <p>Portfolio completo disponível em: {personal_info['website']}</p>
        </div>
    </body>
    </html>
    """
    
    # Tentar WeasyPrint primeiro
    if WEASYPRINT_AVAILABLE:
        try:
            print("📄 Tentando WeasyPrint...")
            
            # Método 1: Usando buffer
            pdf_buffer = BytesIO()
            html_doc = HTML(string=html_content)
            html_doc.write_pdf(pdf_buffer)
            pdf_buffer.seek(0)
            pdf_data = pdf_buffer.getvalue()
            
            print(f"✅ PDF gerado com WeasyPrint: {len(pdf_data)} bytes")
            return pdf_data
            
        except Exception as e:
            print(f"❌ Erro WeasyPrint: {e}")
            print("🔄 Tentando fallback com ReportLab...")
    
    # Fallback para ReportLab
    if REPORTLAB_AVAILABLE:
        try:
            print("📄 Gerando PDF com ReportLab...")
            pdf_data = generate_resume_reportlab(user_data, categorized_projects, all_projects)
            print(f"✅ PDF gerado com ReportLab: {len(pdf_data)} bytes")
            return pdf_data
            
        except Exception as e:
            print(f"❌ Erro ReportLab: {e}")
            raise Exception(f"Falha na geração PDF com ReportLab: {str(e)}")
    
    # Se nenhum método funcionar
    raise Exception("Nenhuma biblioteca de PDF disponível. Instale weasyprint ou reportlab.")
