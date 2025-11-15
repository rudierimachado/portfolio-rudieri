from flask import Flask, render_template, request, jsonify, redirect, session, flash
import requests
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import base64
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'rudieri_advanced_portfolio_2024')

# Configurações
GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME', 'rudirimachado')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '31270032')
# Rota de teste - adicionar no início do app.py
@app.route('/test')
def test():
    return """
    <h1>✅ FUNCIONANDO!</h1>
    <p>Flask está rodando no Render!</p>
    <a href="/admin">Ir para Admin</a>
    """

@app.route('/debug')  
def debug():
    try:
        user_data, categorized_projects, all_projects = organize_all_projects()
        return f"<h1>✅ Função OK!</h1><p>Projetos encontrados: {len(all_projects)}</p>"
    except Exception as e:
        return f"<h1>❌ Erro:</h1><p>{str(e)}</p>"
def load_project_data():
    """Carrega dados dos projetos incluindo galerias"""
    try:
        with open('portfolio_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            'custom_projects': [],
            'github_metadata': {},
            'project_galleries': {}  # Nova estrutura para galerias
        }

def save_project_data(data):
    """Salva dados dos projetos"""
    try:
        with open('portfolio_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return False

def process_uploaded_file(file):
    """Processa arquivo de imagem/GIF para base64"""
    try:
        file_data = file.read()
        file_b64 = base64.b64encode(file_data).decode('utf-8')
        file_ext = file.filename.split('.')[-1].lower()
        
        # Determina o MIME type
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
        print(f"Erro ao processar arquivo: {e}")
        return None

def get_github_data():
    """Busca dados completos do GitHub"""
    try:
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if GITHUB_TOKEN:
            headers['Authorization'] = f'token {GITHUB_TOKEN}'
        
        # Dados do usuário
        user_response = requests.get(f'https://api.github.com/users/{GITHUB_USERNAME}', 
                                   headers=headers, timeout=10)
        user_data = user_response.json() if user_response.status_code == 200 else {}
        
        # Repositórios
        repos_response = requests.get(f'https://api.github.com/users/{GITHUB_USERNAME}/repos',
                                    headers=headers, 
                                    params={'sort': 'updated', 'per_page': 100}, 
                                    timeout=10)
        repos_data = repos_response.json() if repos_response.status_code == 200 else []
        
        return user_data, repos_data
    except Exception as e:
        print(f"Erro GitHub: {e}")
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
    user_data, repos_data = get_github_data()
    portfolio_data = load_project_data()
    github_metadata = portfolio_data.get('github_metadata', {})
    galleries = portfolio_data.get('project_galleries', {})
    
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
        
        # Categorização (usa custom se definida, senão auto-detecta)
        category = metadata.get('category') or auto_categorize_github_repo(
            repo['name'], 
            repo.get('language'), 
            repo.get('description')
        )
        
        # Título (usa custom se definido, senão formata automaticamente)
        title = metadata.get('title') or repo['name'].replace('-', ' ').replace('_', ' ').title()
        
        # Descrição (usa custom se definida, senão do GitHub)
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
    
    return user_data, processed_projects

def organize_all_projects():
    """Organiza TODOS os projetos por categoria"""
    user_data, github_projects = process_github_projects()
    portfolio_data = load_project_data()
    custom_projects = portfolio_data.get('custom_projects', [])
    galleries = portfolio_data.get('project_galleries', {})
    
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
    
    return user_data, categorized, all_projects

@app.route('/')
def portfolio():
    """Página principal do portfólio"""
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
    
    return render_template('portfolio.html', **portfolio_info)

@app.route('/admin')
def admin_dashboard():
    """Dashboard administrativo avançado"""
    if 'admin_logged' not in session:
        return redirect('/admin/login')
    
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
    
    return render_template('admin.html', **admin_data)

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
        
        # Dados do formulário
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
        
        # Salva projeto
        portfolio_data = load_project_data()
        portfolio_data['custom_projects'].append(project)
        
        if save_project_data(portfolio_data):
            return jsonify({'success': True, 'project': project})
        else:
            return jsonify({'error': 'Erro ao salvar projeto'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/github/<github_id>', methods=['PUT'])
def api_update_github_project(github_id):
    """Atualiza metadados de projeto do GitHub"""
    if 'admin_logged' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    try:
        portfolio_data = load_project_data()
        
        # Atualiza metadados
        metadata = {
            'category': request.form.get('category'),
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'demo_url': request.form.get('demo_url', ''),
            'tags': request.form.get('tags', '').split(',') if request.form.get('tags') else [],
            'featured': request.form.get('featured') == 'on'
        }
        
        # Remove valores vazios
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
        
        # Inicializa estrutura de galerias se não existir
        if 'project_galleries' not in portfolio_data:
            portfolio_data['project_galleries'] = {}
        
        # Inicializa galeria do projeto se não existir
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
        
        # Processa múltiplos arquivos
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
                    
                    # Adiciona à galeria geral
                    gallery['images'].append(image_info)
                    
                    # Organiza por módulo
                    if module_name not in gallery['modules']:
                        gallery['modules'][module_name] = []
                    gallery['modules'][module_name].append(image_info)
                    
                    # Define como imagem principal se solicitado
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
            
            # Remove da lista geral
            gallery['images'] = [img for img in gallery['images'] if img.get('id') != image_id]
            
            # Remove dos módulos
            for module in gallery['modules']:
                gallery['modules'][module] = [img for img in gallery['modules'][module] if img.get('id') != image_id]
            
            # Se era a imagem principal, define nova ou remove
            if gallery.get('main_image'):
                # Verifica se a imagem principal ainda existe
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
            
            # Encontra a imagem
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
        
        # Remove galeria do projeto também
        if project_id in portfolio_data.get('project_galleries', {}):
            del portfolio_data['project_galleries'][project_id]
        
        if save_project_data(portfolio_data):
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Erro ao deletar'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    
    # Configuração para produção
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('ENVIRONMENT', 'production') == 'development'
    
    if not debug_mode:
        print("🚀 PORTFÓLIO RUDIERI MACHADO - PRODUÇÃO")
        print("🌐 Sistema rodando em produção")
        print("📧 Email: rudirimachado@gmail.com")
        print("📱 WhatsApp: (47) 99660-9407")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)