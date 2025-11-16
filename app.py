from flask import Flask, render_template, request, jsonify, redirect, session, flash, Response, render_template_string
import requests
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import base64
import uuid
import traceback
import time
from weasyprint import HTML, CSS
from io import BytesIO
from resume_generator import generate_complete_resume

load_dotenv()

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'rudieri_advanced_portfolio_2024')

# Configurações
GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME', 'rudirimachado')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '31270032')

print(f"🔧 Configurações carregadas:")
print(f"   - GITHUB_USERNAME: {GITHUB_USERNAME}")
print(f"   - GITHUB_TOKEN: {'✅ Configurado' if GITHUB_TOKEN else '❌ Não configurado'}")
print(f"   - ADMIN_PASSWORD: {'✅ Configurado' if ADMIN_PASSWORD else '❌ Não configurado'}")

def load_project_data():
    """Carrega dados dos projetos incluindo galerias"""
    try:
        with open('portfolio_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"📂 Dados carregados: {len(data.get('custom_projects', []))} custom, {len(data.get('github_metadata', {}))} github meta")
            return data
    except Exception as e:
        print(f"📂 Criando arquivo de dados novo: {e}")
        return {
            'custom_projects': [],
            'github_metadata': {},
            'project_galleries': {}
        }

def save_project_data(data):
    """Salva dados dos projetos"""
    try:
        with open('portfolio_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("💾 Dados salvos com sucesso")
        return True
    except Exception as e:
        print(f"💾 Erro ao salvar: {e}")
        return False

def process_uploaded_file(file):
    """Processa arquivo de imagem/GIF para base64"""
    try:
        file_data = file.read()
        file_b64 = base64.b64encode(file_data).decode('utf-8')
        file_ext = file.filename.split('.')[-1].lower()
        
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        
        mime_type = mime_types.get(file_ext, 'image/png')
        
        return {
            'data': f"data:{mime_type};base64,{file_b64}",
            'filename': file.filename,
            'size': len(file_data),
            'type': file_ext,
            'mime_type': mime_type
        }
    except Exception as e:
        print(f"📁 Erro ao processar arquivo: {e}")
        return None

def get_github_data():
    """Busca dados completos do GitHub com debug detalhado"""
    try:
        print(f"🔍 === INICIANDO BUSCA GITHUB ===")
        print(f"👤 Username: {GITHUB_USERNAME}")
        print(f"🔑 Token: {'✅ Configurado (' + str(len(GITHUB_TOKEN)) + ' chars)' if GITHUB_TOKEN else '❌ Não configurado'}")
        
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Portfolio-Rudieri-App'
        }
        
        if GITHUB_TOKEN:
            headers['Authorization'] = f'token {GITHUB_TOKEN}'
            print("✅ Header Authorization adicionado")
        
        # Dados do usuário
        print("👤 Buscando dados do usuário...")
        user_url = f'https://api.github.com/users/{GITHUB_USERNAME}'
        print(f"🌐 URL: {user_url}")
        
        user_response = requests.get(user_url, headers=headers, timeout=15)
        print(f"👤 Response Status: {user_response.status_code}")
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"✅ User OK - Nome: {user_data.get('name', 'N/A')}")
            print(f"✅ Public Repos: {user_data.get('public_repos', 0)}")
        else:
            print(f"❌ Erro User: {user_response.status_code} - {user_response.text}")
            user_data = {}
        
        # Pausa para rate limit
        time.sleep(0.5)
        
        # Repositórios
        print("📁 Buscando repositórios...")
        repos_url = f'https://api.github.com/users/{GITHUB_USERNAME}/repos'
        repos_params = {'sort': 'updated', 'per_page': 100}
        print(f"🌐 URL: {repos_url}")
        print(f"📋 Params: {repos_params}")
        
        repos_response = requests.get(repos_url, headers=headers, params=repos_params, timeout=15)
        print(f"📁 Response Status: {repos_response.status_code}")
        
        if repos_response.status_code == 200:
            repos_data = repos_response.json()
            print(f"✅ Repos OK - Encontrados: {len(repos_data)} repositórios")
            
            # Debug primeiros repos
            if repos_data:
                print("📋 Primeiros 3 repositórios:")
                for i, repo in enumerate(repos_data[:3]):
                    print(f"  {i+1}. {repo['name']} ({repo.get('language', 'N/A')})")
        else:
            print(f"❌ Erro Repos: {repos_response.status_code} - {repos_response.text}")
            repos_data = []
        
        print(f"🔍 === BUSCA GITHUB FINALIZADA ===")
        print(f"📊 Resultado: User={len(user_data)} keys, Repos={len(repos_data)} items")
        
        return user_data, repos_data
        
    except Exception as e:
        print(f"💥 ERRO FATAL GitHub API: {e}")
        print(f"💥 Stack trace: {traceback.format_exc()}")
        return {}, []

def auto_categorize_github_repo(repo_name, language, description):
    """Categorização inteligente automática"""
    text = f"{repo_name} {description or ''}".lower()
    
    # RPA/Automação
    rpa_keywords = ['rpa', 'bot', 'robot', 'automation', 'scraping', 'selenium', 'scraper', 
                   'spider', 'crawler', 'extractor', 'monitor', 'notificador', 'quickbook']
    if any(keyword in text for keyword in rpa_keywords):
        return 'rpa'
    
    # Sistemas/Apps
    system_keywords = ['system', 'erp', 'sysrohden', 'app', 'dashboard', 'admin', 
                      'manager', 'platform', 'cms', 'crm', 'portal']
    if any(keyword in text for keyword in system_keywords):
        return 'sistema'
    
    # APIs
    api_keywords = ['api', 'rest', 'endpoint', 'service', 'microservice', 'backend']
    if any(keyword in text for keyword in api_keywords):
        return 'api'
    
    # Web/Frontend
    web_keywords = ['website', 'web', 'frontend', 'react', 'vue', 'angular', 'html', 'css']
    if any(keyword in text for keyword in web_keywords):
        return 'web'
    
    # Mobile
    mobile_keywords = ['mobile', 'android', 'ios', 'flutter', 'react-native']
    if any(keyword in text for keyword in mobile_keywords):
        return 'mobile'
    
    return 'outros'

def get_project_gallery(project_id, gallery_data):
    """Obtém galeria de um projeto específico"""
    return gallery_data.get(project_id, {
        'main_image': '',
        'images': [],
        'modules': {}
    })

def process_github_projects():
    """Processa e combina projetos do GitHub com metadados locais"""
    print(f"🔄 === PROCESSANDO PROJETOS GITHUB ===")
    
    try:
        user_data, repos_data = get_github_data()
        print(f"📊 API retornou: User keys={list(user_data.keys()) if user_data else 'vazio'}")
        print(f"📊 API retornou: {len(repos_data)} repositórios")
        
        portfolio_data = load_project_data()
        github_metadata = portfolio_data.get('github_metadata', {})
        galleries = portfolio_data.get('project_galleries', {})
        
        print(f"📂 Metadados locais: {len(github_metadata)} projetos")
        print(f"🖼️ Galerias locais: {len(galleries)} projetos")
        
        colors = [
            'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
            'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
            'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
            'linear-gradient(135deg, #feca57 0%, #ff9ff3 100%)',
            'linear-gradient(135deg, #54a0ff 0%, #5f27cd 100%)'
        ]
        
        processed_projects = []
        
        for i, repo in enumerate(repos_data):
            repo_id = str(repo['id'])
            metadata = github_metadata.get(repo_id, {})
            gallery = get_project_gallery(f"github_{repo_id}", galleries)
            
            # Categorização
            category = metadata.get('category') or auto_categorize_github_repo(
                repo['name'], 
                repo.get('language'), 
                repo.get('description')
            )
            
            # Título
            title = metadata.get('title') or repo['name'].replace('-', ' ').replace('_', ' ').title()
            
            # Descrição
            description = metadata.get('description') or repo.get('description') or f"Projeto desenvolvido em {repo.get('language', 'Python')}"
            
            project = {
                'id': f"github_{repo_id}",
                'github_id': repo_id,
                'title': title,
                'description': description,
                'category': category,
                'source': 'github',
                'github_url': repo['html_url'],
                'demo_url': repo.get('homepage') or metadata.get('demo_url', ''),
                'language': repo.get('language') or 'N/A',
                'color': colors[i % len(colors)],
                'main_image': gallery.get('main_image', ''),
                'gallery': gallery.get('images', []),
                'modules': gallery.get('modules', {}),
                'tags': metadata.get('tags', []),
                'featured': metadata.get('featured', False),
                'created_at': repo['created_at'],
                'updated_at': repo['updated_at'],
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'size': repo.get('size', 0)
            }
            
            processed_projects.append(project)
            
            if i < 3:  # Debug dos primeiros 3
                print(f"✅ Projeto {i+1}: {title} ({category})")
        
        print(f"🔄 === PROCESSAMENTO FINALIZADO ===")
        print(f"📊 Resultado: {len(processed_projects)} projetos processados")
        
        return user_data, processed_projects
        
    except Exception as e:
        print(f"💥 ERRO process_github_projects: {e}")
        print(f"💥 Stack: {traceback.format_exc()}")
        return {}, []

def organize_all_projects():
    """Organiza TODOS os projetos por categoria"""
    print(f"📋 === ORGANIZANDO TODOS OS PROJETOS ===")
    
    try:
        user_data, github_projects = process_github_projects()
        portfolio_data = load_project_data()
        custom_projects = portfolio_data.get('custom_projects', [])
        galleries = portfolio_data.get('project_galleries', {})
        
        print(f"📊 GitHub projects: {len(github_projects)}")
        print(f"📊 Custom projects: {len(custom_projects)}")
        
        # Adiciona galeria aos projetos customizados
        for project in custom_projects:
            gallery = get_project_gallery(project['id'], galleries)
            project.update({
                'main_image': gallery.get('main_image', project.get('image', '')),
                'gallery': gallery.get('images', []),
                'modules': gallery.get('modules', {})
            })
        
        # Combina todos os projetos
        all_projects = github_projects + custom_projects
        print(f"📊 Total projects: {len(all_projects)}")
        
        # Organiza por categoria
        categorized = {
            'sistema': [],
            'rpa': [],
            'api': [],
            'web': [],
            'mobile': [],
            'outros': []
        }
        
        for project in all_projects:
            category = project.get('category', 'outros')
            if category in categorized:
                categorized[category].append(project)
            else:
                categorized['outros'].append(project)
        
        # Ordena por featured primeiro, depois por data de atualização
        for category in categorized:
            categorized[category].sort(key=lambda x: (not x.get('featured', False), x.get('updated_at', '')), reverse=True)
        
        # Debug das categorias
        print(f"📋 Projetos por categoria:")
        for cat, projects in categorized.items():
            print(f"  - {cat}: {len(projects)} projetos")
        
        print(f"📋 === ORGANIZAÇÃO FINALIZADA ===")
        
        return user_data, categorized, all_projects
        
    except Exception as e:
        print(f"💥 ERRO organize_all_projects: {e}")
        print(f"💥 Stack: {traceback.format_exc()}")
        return {}, {
            'sistema': [], 'rpa': [], 'api': [], 
            'web': [], 'mobile': [], 'outros': []
        }, []

# ===== ROTAS DE DEBUG =====

@app.route('/test')
def test():
    return """
    <h1>✅ FUNCIONANDO!</h1>
    <p>Flask está rodando no Render!</p>
    <a href="/admin">Ir para Admin</a>
    <a href="/admin/debug-github">Debug GitHub</a>
    """

@app.route('/admin/debug-github')
def debug_github():
    if 'admin_logged' not in session:
        return redirect('/admin/login')
    
    try:
        debug_info = []
        
        # Teste 1: Verificar variáveis
        debug_info.append(f"✅ GITHUB_USERNAME: {GITHUB_USERNAME}")
        debug_info.append(f"✅ GITHUB_TOKEN configurado: {'Sim' if GITHUB_TOKEN else 'Não'}")
        debug_info.append(f"✅ Token length: {len(GITHUB_TOKEN) if GITHUB_TOKEN else 0}")
        
        # Teste 2: Testar API diretamente
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if GITHUB_TOKEN:
            headers['Authorization'] = f'token {GITHUB_TOKEN}'
        
        debug_info.append("=" * 50)
        debug_info.append("🔍 TESTE API GITHUB DIRETA:")
        
        # Teste usuário
        user_response = requests.get(f'https://api.github.com/users/{GITHUB_USERNAME}', 
                                   headers=headers, timeout=10)
        
        debug_info.append(f"👤 User API Status: {user_response.status_code}")
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            debug_info.append(f"✅ Nome: {user_data.get('name', 'N/A')}")
            debug_info.append(f"✅ Public repos: {user_data.get('public_repos', 0)}")
            debug_info.append(f"✅ Bio: {user_data.get('bio', 'N/A')}")
        else:
            debug_info.append(f"❌ Erro User: {user_response.text}")
        
        # Teste repositórios
        repos_response = requests.get(f'https://api.github.com/users/{GITHUB_USERNAME}/repos',
                                    headers=headers, timeout=10)
        
        debug_info.append(f"📁 Repos API Status: {repos_response.status_code}")
        
        if repos_response.status_code == 200:
            repos_data = repos_response.json()
            debug_info.append(f"✅ Repos encontrados: {len(repos_data)}")
            
            if repos_data:
                debug_info.append("📋 Primeiros 5 repos:")
                for repo in repos_data[:5]:
                    debug_info.append(f"  - {repo['name']} ({repo.get('language', 'N/A')})")
        else:
            debug_info.append(f"❌ Erro Repos: {repos_response.text}")
        
        # Teste função completa
        debug_info.append("=" * 50)
        debug_info.append("🔄 TESTE FUNÇÃO get_github_data():")
        
        try:
            user_result, repos_result = get_github_data()
            debug_info.append(f"✅ Função retornou:")
            debug_info.append(f"  - User: {type(user_result)} com {len(user_result)} keys")
            debug_info.append(f"  - Repos: {type(repos_result)} com {len(repos_result) if isinstance(repos_result, list) else 'erro'} items")
        except Exception as func_error:
            debug_info.append(f"❌ Erro na função: {str(func_error)}")
            debug_info.append(f"❌ Stack: {traceback.format_exc()}")
        
        html = f"""
        <h1>🔍 Debug GitHub API</h1>
        <pre style="background: #f0f0f0; padding: 20px; border-radius: 10px; overflow-x: auto;">
        {chr(10).join(debug_info)}
        </pre>
        <div style="margin-top: 20px;">
            <a href="/admin" style="background: #6366f1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">Voltar Admin</a>
            <a href="/admin/test-functions" style="background: #10b981; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Test Functions</a>
        </div>
        """
        
        return html
        
    except Exception as e:
        return f"""
        <h1>❌ Erro no Debug</h1>
        <pre>{str(e)}</pre>
        <pre>{traceback.format_exc()}</pre>
        <a href="/admin">Voltar</a>
        """

@app.route('/admin/test-functions')
def test_functions():
    if 'admin_logged' not in session:
        return redirect('/admin/login')
    
    try:
        debug_info = []
        
        # Teste process_github_projects
        debug_info.append("🔄 TESTE process_github_projects():")
        try:
            user_data, github_projects = process_github_projects()
            debug_info.append(f"✅ User data keys: {list(user_data.keys()) if user_data else 'vazio'}")
            debug_info.append(f"✅ GitHub projects: {len(github_projects)}")
            
            if github_projects:
                debug_info.append("📋 Primeiro projeto:")
                proj = github_projects[0]
                debug_info.append(f"  - Título: {proj.get('title', 'N/A')}")
                debug_info.append(f"  - Categoria: {proj.get('category', 'N/A')}")
                debug_info.append(f"  - Language: {proj.get('language', 'N/A')}")
                debug_info.append(f"  - Stars: {proj.get('stars', 0)}")
                
        except Exception as e:
            debug_info.append(f"❌ Erro: {str(e)}")
            debug_info.append(f"❌ Stack: {traceback.format_exc()}")
        
        # Teste organize_all_projects
        debug_info.append("=" * 50)
        debug_info.append("🔄 TESTE organize_all_projects():")
        try:
            user_data, categorized_projects, all_projects = organize_all_projects()
            debug_info.append(f"✅ Total projects: {len(all_projects)}")
            debug_info.append(f"✅ Categorias: {list(categorized_projects.keys())}")
            
            for cat, projects in categorized_projects.items():
                debug_info.append(f"  - {cat}: {len(projects)} projetos")
                
        except Exception as e:
            debug_info.append(f"❌ Erro: {str(e)}")
            debug_info.append(f"❌ Stack: {traceback.format_exc()}")
        
        # Teste portfolio principal
        debug_info.append("=" * 50)
        debug_info.append("🔄 TESTE função portfolio():")
        try:
            user_data, categorized_projects, all_projects = organize_all_projects()
            
            portfolio_info = {
                'name': user_data.get('name') or 'Rudieri Machado',
                'avatar': user_data.get('avatar_url') or '',
                'bio': user_data.get('bio') or 'Desenvolvedor Full Stack & Especialista RPA',
                'projects': categorized_projects,
                'stats': {
                    'total': len(all_projects),
                    'systems': len(categorized_projects['sistema']),
                    'rpa': len(categorized_projects['rpa'])
                }
            }
            
            debug_info.append(f"✅ Portfolio info gerado:")
            debug_info.append(f"  - Nome: {portfolio_info['name']}")
            debug_info.append(f"  - Avatar: {'✅ Sim' if portfolio_info['avatar'] else '❌ Não'}")
            debug_info.append(f"  - Stats total: {portfolio_info['stats']['total']}")
            
        except Exception as e:
            debug_info.append(f"❌ Erro: {str(e)}")
            debug_info.append(f"❌ Stack: {traceback.format_exc()}")
        
        html = f"""
        <h1>🧪 Test Functions</h1>
        <pre style="background: #f0f0f0; padding: 20px; border-radius: 10px; overflow-x: auto;">
        {chr(10).join(debug_info)}
        </pre>
        <div style="margin-top: 20px;">
            <a href="/admin" style="background: #6366f1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">Voltar Admin</a>
            <a href="/admin/debug-github" style="background: #ef4444; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Debug API</a>
        </div>
        """
        
        return html
        
    except Exception as e:
        return f"""
        <h1>❌ Erro no Test</h1>
        <pre>{str(e)}</pre>
        <pre>{traceback.format_exc()}</pre>
        <a href="/admin">Voltar</a>
        """

# ===== ROTAS PRINCIPAIS =====

@app.route('/')
def portfolio():
    """Página principal do portfólio"""
    try:
        print(f"🏠 === CARREGANDO PÁGINA PRINCIPAL ===")
        
        user_data, categorized_projects, all_projects = organize_all_projects()
        
        portfolio_info = {
            'name': user_data.get('name') or 'Rudieri Machado',
            'avatar': user_data.get('avatar_url') or '',
            'bio': user_data.get('bio') or 'Desenvolvedor Full Stack & Especialista RPA. Criador e mantenedor do ERP SYSROHDEN, participando desde sua concepção até hoje no desenvolvimento de novos módulos.',
            'github_url': user_data.get('html_url') or f'https://github.com/{GITHUB_USERNAME}',
            'location': user_data.get('location') or 'Brasil',
            'email': 'rudirimachado@gmail.com',
            'whatsapp': '47996609407',
            'instagram': 'https://www.instagram.com/rudieri.machado',
            'projects': categorized_projects,
            'stats': {
                'experience': '5+',
                'systems': len(categorized_projects['sistema']),
                'rpa': len(categorized_projects['rpa']),
                'total': len(all_projects),
                'languages': len(set([p.get('language', 'N/A') for p in all_projects if p.get('language')]))
            }
        }
        
        print(f"🏠 Portfolio carregado - {portfolio_info['stats']['total']} projetos")
        
        return render_template('portfolio.html', **portfolio_info)
        
    except Exception as e:
        print(f"💥 ERRO portfolio(): {e}")
        print(f"💥 Stack: {traceback.format_exc()}")
        
        # Fallback simples
        return f"""
        <h1>🎯 Portfólio Rudieri Machado</h1>
        <p>✅ Sistema funcionando no Render!</p>
        <p>❌ Erro ao carregar projetos: {str(e)}</p>
        <p>📧 Email: rudirimachado@gmail.com</p>
        <p>📱 WhatsApp: (47) 99660-9407</p>
        <a href="/admin" style="background: #6366f1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Admin Panel</a>
        <a href="/admin/debug-github" style="background: #ef4444; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-left: 10px;">Debug</a>
        """

@app.route('/admin')
def admin_dashboard():
    """Dashboard administrativo avançado"""
    if 'admin_logged' not in session:
        return redirect('/admin/login')
    
    try:
        print(f"🔧 === CARREGANDO ADMIN DASHBOARD ===")
        
        user_data, github_projects = process_github_projects()
        portfolio_data = load_project_data()
        custom_projects = portfolio_data.get('custom_projects', [])
        
        admin_data = {
            'user': user_data,
            'github_projects': github_projects,
            'custom_projects': custom_projects,
            'total_projects': len(github_projects) + len(custom_projects),
            'categories': ['sistema', 'rpa', 'api', 'web', 'mobile', 'outros']
        }
        
        print(f"🔧 Admin carregado - {admin_data['total_projects']} projetos total")
        
        return render_template('admin.html', **admin_data)
        
    except Exception as e:
        print(f"💥 ERRO admin_dashboard(): {e}")
        print(f"💥 Stack: {traceback.format_exc()}")
        
        return f"""
        <h1>❌ Erro no Admin</h1>
        <p>Erro: {str(e)}</p>
        <a href="/admin/debug-github">Debug GitHub</a>
        <a href="/admin/logout">Logout</a>
        """

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Login administrativo"""
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        if password == ADMIN_PASSWORD:
            session['admin_logged'] = True
            flash('Login realizado com sucesso!', 'success')
            return redirect('/admin')
        else:
            flash('Senha incorreta!', 'error')
    
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    """Logout administrativo"""
    session.pop('admin_logged', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect('/')

# API Routes para Projetos
@app.route('/api/projects', methods=['GET'])
def api_get_projects():
    """Lista todos os projetos"""
    if 'admin_logged' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    user_data, github_projects = process_github_projects()
    portfolio_data = load_project_data()
    custom_projects = portfolio_data.get('custom_projects', [])
    
    return jsonify({
        'github_projects': github_projects,
        'custom_projects': custom_projects,
        'user': user_data
    })

@app.route('/api/projects/custom', methods=['POST'])
def api_create_custom_project():
    """Cria projeto customizado"""
    if 'admin_logged' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    try:
        project_id = f"custom_{uuid.uuid4().hex[:8]}"
        
        project = {
            'id': project_id,
            'title': request.form.get('title', '').strip(),
            'description': request.form.get('description', '').strip(),
            'category': request.form.get('category', 'outros'),
            'source': 'custom',
            'github_url': request.form.get('github_url', '').strip(),
            'demo_url': request.form.get('demo_url', '').strip(),
            'language': request.form.get('language', '').strip(),
            'tags': request.form.get('tags', '').split(',') if request.form.get('tags') else [],
            'featured': request.form.get('featured') == 'on',
            'color': request.form.get('color', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        portfolio_data = load_project_data()
        portfolio_data['custom_projects'].append(project)
        
        if save_project_data(portfolio_data):
            print(f"✅ Projeto customizado criado: {project['title']}")
            return jsonify({'success': True, 'project': project})
        else:
            return jsonify({'error': 'Erro ao salvar projeto'}), 500
            
    except Exception as e:
        print(f"❌ Erro criar projeto custom: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/github/<github_id>', methods=['PUT'])
def api_update_github_project(github_id):
    """Atualiza metadados de projeto do GitHub"""
    if 'admin_logged' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    try:
        portfolio_data = load_project_data()
        
        metadata = {
            'category': request.form.get('category'),
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'demo_url': request.form.get('demo_url', ''),
            'tags': request.form.get('tags', '').split(',') if request.form.get('tags') else [],
            'featured': request.form.get('featured') == 'on'
        }
        
        metadata = {k: v for k, v in metadata.items() if v}
        
        portfolio_data['github_metadata'][github_id] = metadata
        
        if save_project_data(portfolio_data):
            return jsonify({'success': True, 'metadata': metadata})
        else:
            return jsonify({'error': 'Erro ao salvar'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API Routes para Galeria de Imagens
@app.route('/api/projects/<project_id>/gallery', methods=['GET'])
def api_get_project_gallery(project_id):
    """Obtém galeria de um projeto"""
    if 'admin_logged' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    try:
        portfolio_data = load_project_data()
        galleries = portfolio_data.get('project_galleries', {})
        gallery = get_project_gallery(project_id, galleries)
        
        return jsonify({'success': True, 'gallery': gallery})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/gallery/upload', methods=['POST'])
def api_upload_project_images(project_id):
    """Upload múltiplo de imagens para projeto"""
    if 'admin_logged' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    try:
        portfolio_data = load_project_data()
        
        if 'project_galleries' not in portfolio_data:
            portfolio_data['project_galleries'] = {}
        
        if project_id not in portfolio_data['project_galleries']:
            portfolio_data['project_galleries'][project_id] = {
                'main_image': '',
                'images': [],
                'modules': {}
            }
        
        gallery = portfolio_data['project_galleries'][project_id]
        module_name = request.form.get('module', 'geral')
        is_main = request.form.get('is_main') == 'true'
        
        uploaded_images = []
        
        for file_key in request.files:
            file = request.files[file_key]
            if file and file.filename:
                processed_file = process_uploaded_file(file)
                if processed_file:
                    image_info = {
                        'id': uuid.uuid4().hex[:12],
                        'filename': processed_file['filename'],
                        'data': processed_file['data'],
                        'size': processed_file['size'],
                        'type': processed_file['type'],
                        'mime_type': processed_file['mime_type'],
                        'module': module_name,
                        'uploaded_at': datetime.now().isoformat(),
                        'description': request.form.get(f'description_{file_key}', '')
                    }
                    
                    gallery['images'].append(image_info)
                    
                    if module_name not in gallery['modules']:
                        gallery['modules'][module_name] = []
                    gallery['modules'][module_name].append(image_info)
                    
                    if is_main or not gallery['main_image']:
                        gallery['main_image'] = processed_file['data']
                    
                    uploaded_images.append(image_info)
        
        if save_project_data(portfolio_data):
            return jsonify({
                'success': True, 
                'uploaded_images': uploaded_images,
                'total_images': len(gallery['images'])
            })
        else:
            return jsonify({'error': 'Erro ao salvar imagens'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/gallery/<image_id>', methods=['DELETE'])
def api_delete_project_image(project_id, image_id):
    """Remove uma imagem específica da galeria"""
    if 'admin_logged' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    try:
        portfolio_data = load_project_data()
        galleries = portfolio_data.get('project_galleries', {})
        
        if project_id in galleries:
            gallery = galleries[project_id]
            
            gallery['images'] = [img for img in gallery['images'] if img.get('id') != image_id]
            
            for module in gallery['modules']:
                gallery['modules'][module] = [img for img in gallery['modules'][module] if img.get('id') != image_id]
            
            if gallery.get('main_image'):
                main_exists = any(img for img in gallery['images'] if img.get('data') == gallery['main_image'])
                if not main_exists:
                    gallery['main_image'] = gallery['images'][0]['data'] if gallery['images'] else ''
            
            if save_project_data(portfolio_data):
                return jsonify({'success': True})
        
        return jsonify({'error': 'Imagem não encontrada'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_id>/gallery/main', methods=['PUT'])
def api_set_main_image(project_id):
    """Define imagem principal do projeto"""
    if 'admin_logged' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    try:
        image_id = request.json.get('image_id')
        
        portfolio_data = load_project_data()
        galleries = portfolio_data.get('project_galleries', {})
        
        if project_id in galleries:
            gallery = galleries[project_id]
            
            target_image = next((img for img in gallery['images'] if img.get('id') == image_id), None)
            
            if target_image:
                gallery['main_image'] = target_image['data']
                
                if save_project_data(portfolio_data):
                    return jsonify({'success': True})
        
        return jsonify({'error': 'Imagem não encontrada'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/custom/<project_id>', methods=['DELETE'])
def api_delete_custom_project(project_id):
    """Deleta projeto customizado"""
    if 'admin_logged' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    try:
        portfolio_data = load_project_data()
        portfolio_data['custom_projects'] = [
            p for p in portfolio_data['custom_projects'] 
            if p['id'] != project_id
        ]
        
        if project_id in portfolio_data.get('project_galleries', {}):
            del portfolio_data['project_galleries'][project_id]
        
        if save_project_data(portfolio_data):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Erro ao deletar'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/backup')
def backup_data():
    """Backup dos dados do portfólio"""
    if 'admin_logged' not in session:
        return redirect('/admin/login')
    
    try:
        with open('portfolio_data.json', 'r', encoding='utf-8') as f:
            data = f.read()
        
        return Response(
            data,
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment;filename=portfolio_backup.json'}
        )
    except:
        return jsonify({'error': 'Erro ao fazer backup'})

@app.route('/admin/generate-resume')
def generate_resume_pdf():
    """Gera currículo completo e detalhado em PDF"""
    if 'admin_logged' not in session:
        return redirect('/admin/login')
    
    try:
        print(f"📄 === GERANDO CURRÍCULO PDF ===")
        
        # Buscar dados completos do perfil
        user_data, categorized_projects, all_projects = organize_all_projects()
        
        print(f"📊 Dados coletados: {len(all_projects)} projetos, {len(categorized_projects)} categorias")
        
        # Gerar PDF usando o novo gerador
        pdf_data = generate_complete_resume(user_data, categorized_projects, all_projects)
        
        # Nome do arquivo
        filename = f"Curriculo_Rudieri_Machado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        print(f"✅ PDF gerado com sucesso: {len(pdf_data)} bytes")
        
        return Response(
            pdf_data,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'application/pdf'
            }
        )
        
    except Exception as e:
        print(f"❌ Erro ao gerar currículo PDF: {e}")
        print(f"❌ Stack: {traceback.format_exc()}")
        
        # Fallback para HTML se PDF falhar
        try:
            user_data, categorized_projects, all_projects = organize_all_projects()
            
            fallback_html = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <title>Currículo - Rudieri Machado</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; margin-bottom: 30px; }}
                    .section {{ margin-bottom: 30px; }}
                    .section h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                    .error {{ background: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                </style>
            </head>
            <body>
                <div class="error">
                    <strong>⚠️ Erro na geração do PDF:</strong> {str(e)}<br>
                    Exibindo versão simplificada em HTML. Para o PDF completo, instale as dependências necessárias.
                </div>
                
                <div class="header">
                    <h1>Rudieri Machado</h1>
                    <p>Desenvolvedor Full Stack & Especialista em RPA</p>
                    <p>📧 rudirimachado@gmail.com | 📱 (47) 99660-9407 | 📍 Blumenau, SC</p>
                </div>
                
                <div class="section">
                    <h2>📊 Estatísticas</h2>
                    <p><strong>Projetos Totais:</strong> {len(all_projects)}</p>
                    <p><strong>Sistemas:</strong> {len(categorized_projects.get('sistema', []))}</p>
                    <p><strong>Automações RPA:</strong> {len(categorized_projects.get('rpa', []))}</p>
                    <p><strong>APIs:</strong> {len(categorized_projects.get('api', []))}</p>
                    <p><strong>Web Apps:</strong> {len(categorized_projects.get('web', []))}</p>
                </div>
                
                <div class="section">
                    <h2>👨‍💻 Perfil Profissional</h2>
                    <p>Desenvolvedor Full Stack apaixonado por tecnologia e inovação, com mais de 5 anos de experiência 
                    em desenvolvimento de software e especialização em automação RPA. Criador e arquiteto principal do 
                    ERP SYSROHDEN, demonstrando capacidade de liderança técnica e visão estratégica de produto.</p>
                </div>
                
                <div class="section">
                    <h2>💼 Experiência</h2>
                    <h3>Desenvolvedor Full Stack & Especialista RPA</h3>
                    <p><strong>SYSROHDEN ERP</strong> | 2019 - Presente</p>
                    <ul>
                        <li>Criador e mantenedor principal do ERP SYSROHDEN</li>
                        <li>Desenvolvimento de {len(all_projects)} projetos em diversas tecnologias</li>
                        <li>Especialização em automação RPA</li>
                        <li>Liderança técnica e arquitetura de software</li>
                    </ul>
                </div>
                
                <div class="section">
                    <h2>🎓 Formação</h2>
                    <p><strong>Tecnólogo em Análise e Desenvolvimento de Sistemas</strong><br>
                    FURB - Universidade Regional de Blumenau | 2017 - 2020</p>
                </div>
                
                <div class="section">
                    <h2>💻 Tecnologias</h2>
                    <p>Python, JavaScript, Java, C#, HTML, CSS, React, Node.js, PostgreSQL, MySQL, Docker, Git, Linux</p>
                </div>
                
                <p style="text-align: center; margin-top: 40px; color: #666;">
                    Currículo gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}<br>
                    Portfolio completo: https://portfolio-rudieri.onrender.com
                </p>
            </body>
            </html>
            """
            
            return Response(
                fallback_html,
                mimetype='text/html'
            )
            
        except Exception as fallback_error:
            return f"""
            <h1>❌ Erro Crítico ao Gerar Currículo</h1>
            <p><strong>Erro PDF:</strong> {str(e)}</p>
            <p><strong>Erro Fallback:</strong> {str(fallback_error)}</p>
            <p>Por favor, verifique as dependências do sistema.</p>
            <a href="/admin" style="background: #6366f1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Voltar ao Admin</a>
            """

if __name__ == '__main__':
    import os
    
    print("🚀 === INICIANDO PORTFÓLIO RUDIERI MACHADO ===")
    print(f"🌐 Modo: {os.environ.get('ENVIRONMENT', 'development')}")
    
    # Configuração para produção
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('ENVIRONMENT', 'production') == 'development'
    
    if not debug_mode:
        print("🚀 PORTFÓLIO RUDIERI MACHADO - PRODUÇÃO")
        print("🌐 Sistema rodando em produção")
        print("📧 Email: rudirimachado@gmail.com")
        print("📱 WhatsApp: (47) 99660-9407")
        print("🔧 Debug disponível em /admin/debug-github")
        print("🧪 Testes disponíveis em /admin/test-functions")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)