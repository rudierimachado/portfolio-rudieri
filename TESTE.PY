import requests
import json
import pandas as pd
from datetime import datetime
import time

class TheOddsAPITester:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.the-odds-api.com/v4"
        self.session = requests.Session()
        
    def test_api_connection(self):
        """Testa se a API key está funcionando"""
        print("🔍 TESTANDO CONEXÃO COM THE ODDS API")
        print("="*50)
        
        try:
            # Endpoint simples para testar
            url = f"{self.base_url}/sports"
            params = {'api_key': self.api_key}
            
            response = self.session.get(url, params=params, timeout=10)
            
            print(f"📡 Status Code: {response.status_code}")
            print(f"🔑 API Key: {self.api_key[:8]}...")
            
            # Headers importantes
            remaining = response.headers.get('x-requests-remaining', 'N/A')
            used = response.headers.get('x-requests-used', 'N/A')
            
            print(f"📊 Requests Restantes: {remaining}")
            print(f"📊 Requests Usados: {used}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API FUNCIONANDO! {len(data)} esportes disponíveis")
                return True
            else:
                print(f"❌ Erro: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False

    def list_available_sports(self):
        """Lista todos os esportes disponíveis"""
        try:
            print("\n🏆 ESPORTES DISPONÍVEIS")
            print("="*30)
            
            url = f"{self.base_url}/sports"
            params = {'api_key': self.api_key}
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                sports = response.json()
                
                print(f"Total de esportes: {len(sports)}")
                print("\n📋 Lista de esportes:")
                
                for sport in sports:
                    print(f"   🏃 {sport['title']} (key: {sport['key']})")
                    if 'description' in sport:
                        print(f"      📝 {sport['description']}")
                
                return sports
            else:
                print(f"❌ Erro ao listar esportes: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return []

    def get_soccer_odds(self, sport_key="soccer_brazil_campeonato"):
        """Pega odds específicas do futebol brasileiro"""
        try:
            print(f"\n⚽ ODDS DO FUTEBOL - {sport_key}")
            print("="*50)
            
            url = f"{self.base_url}/sports/{sport_key}/odds"
            
            params = {
                'api_key': self.api_key,
                'regions': 'us,uk,eu',  # Múltiplas regiões
                'markets': 'h2h',  # Head to head (1X2)
                'oddsFormat': 'decimal',
                'dateFormat': 'iso'
            }
            
            print(f"📡 Consultando: {url}")
            print(f"⚙️  Parâmetros: {params}")
            
            response = self.session.get(url, params=params)
            
            # Headers de quota
            remaining = response.headers.get('x-requests-remaining', 'N/A')
            used = response.headers.get('x-requests-used', 'N/A')
            
            print(f"\n📊 Quota Info:")
            print(f"   Restantes: {remaining}")
            print(f"   Usados: {used}")
            
            if response.status_code == 200:
                matches = response.json()
                print(f"\n✅ {len(matches)} partidas encontradas!")
                
                if matches:
                    self.display_matches(matches)
                    self.save_data(matches, sport_key)
                else:
                    print("⚠️  Nenhuma partida ativa no momento")
                
                return matches
            else:
                print(f"❌ Erro: {response.status_code}")
                print(f"Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return []

    def try_multiple_soccer_leagues(self):
        """Tenta diferentes ligas de futebol"""
        soccer_leagues = [
            "soccer_brazil_campeonato",  # Brasileirão
            "soccer_brazil_serie_b",     # Série B
            "soccer_epl",               # Premier League
            "soccer_uefa_champs_league", # Champions League
            "soccer_fifa_world_cup",     # Copa do Mundo
            "soccer_conmebol_copa_libertadores", # Libertadores
            "soccer_spain_la_liga",      # La Liga
            "soccer_italy_serie_a",      # Serie A
            "soccer_germany_bundesliga", # Bundesliga
        ]
        
        print("\n🌎 TESTANDO MÚLTIPLAS LIGAS")
        print("="*40)
        
        all_matches = {}
        
        for league in soccer_leagues:
            print(f"\n🔍 Testando {league}...")
            
            try:
                matches = self.get_odds_simple(league)
                all_matches[league] = matches
                
                if matches:
                    print(f"✅ {league}: {len(matches)} partidas")
                else:
                    print(f"⚪ {league}: Sem partidas")
                    
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"❌ {league}: Erro - {e}")
                continue
        
        # Resumo
        print(f"\n📊 RESUMO GERAL:")
        total_matches = sum(len(matches) for matches in all_matches.values())
        working_leagues = [k for k, v in all_matches.items() if v]
        
        print(f"Total de partidas: {total_matches}")
        print(f"Ligas com dados: {len(working_leagues)}")
        
        if working_leagues:
            print("✅ Ligas funcionando:")
            for league in working_leagues:
                print(f"   • {league}: {len(all_matches[league])} jogos")
        
        return all_matches

    def get_odds_simple(self, sport_key):
        """Versão simplificada para testar múltiplas ligas"""
        try:
            url = f"{self.base_url}/sports/{sport_key}/odds"
            params = {
                'api_key': self.api_key,
                'regions': 'us',
                'markets': 'h2h',
                'oddsFormat': 'decimal'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except:
            return []

    def display_matches(self, matches):
        """Exibe as partidas de forma organizada"""
        print("\n🏆 PARTIDAS ENCONTRADAS:")
        print("="*60)
        
        for i, match in enumerate(matches[:5], 1):  # Primeiras 5 partidas
            print(f"\n🎮 JOGO #{i}")
            print(f"   🏠 Casa: {match.get('home_team', 'N/A')}")
            print(f"   ✈️  Fora: {match.get('away_team', 'N/A')}")
            print(f"   📅 Data: {match.get('commence_time', 'N/A')}")
            print(f"   🏟️  Esporte: {match.get('sport_title', 'N/A')}")
            
            # Mostra bookmakers e odds
            bookmakers = match.get('bookmakers', [])
            print(f"   📊 Bookmakers: {len(bookmakers)}")
            
            if bookmakers:
                # Pega primeiro bookmaker como exemplo
                first_book = bookmakers[0]
                print(f"   📖 Exemplo ({first_book.get('title', 'N/A')}):")
                
                markets = first_book.get('markets', [])
                for market in markets:
                    if market.get('key') == 'h2h':  # Head to head
                        outcomes = market.get('outcomes', [])
                        print(f"      💰 Odds H2H:")
                        for outcome in outcomes:
                            name = outcome.get('name', 'N/A')
                            price = outcome.get('price', 'N/A')
                            print(f"         {name}: {price}")

    def save_data(self, matches, sport_key):
        """Salva dados em arquivos"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # JSON completo
            json_file = f"odds_{sport_key}_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(matches, f, indent=2, ensure_ascii=False)
            
            # CSV simplificado
            csv_data = []
            for match in matches:
                base_data = {
                    'sport': match.get('sport_title', ''),
                    'home_team': match.get('home_team', ''),
                    'away_team': match.get('away_team', ''),
                    'commence_time': match.get('commence_time', ''),
                    'bookmakers_count': len(match.get('bookmakers', []))
                }
                
                # Adiciona odds do primeiro bookmaker
                bookmakers = match.get('bookmakers', [])
                if bookmakers:
                    first_book = bookmakers[0]
                    base_data['bookmaker'] = first_book.get('title', '')
                    
                    # Pega odds H2H
                    for market in first_book.get('markets', []):
                        if market.get('key') == 'h2h':
                            for outcome in market.get('outcomes', []):
                                name = outcome.get('name', '').lower().replace(' ', '_')
                                base_data[f'odds_{name}'] = outcome.get('price', '')
                
                csv_data.append(base_data)
            
            if csv_data:
                df = pd.DataFrame(csv_data)
                csv_file = f"odds_{sport_key}_{timestamp}.csv"
                df.to_csv(csv_file, index=False, encoding='utf-8')
                
                print(f"\n💾 Arquivos salvos:")
                print(f"   📄 JSON: {json_file}")
                print(f"   📊 CSV: {csv_file}")
            
        except Exception as e:
            print(f"⚠️  Erro ao salvar: {e}")

# =====================
# TESTE PRINCIPAL
# =====================

def main():
    print("🎯 TESTE THE ODDS API")
    print("="*30)
    
    # Sua chave de API
    api_key = "f2948d80497a6c7b65fedae31d862a3b"
    
    # ⚠️ AVISO DE SEGURANÇA
    print("⚠️  AVISO: Você compartilhou sua chave de API publicamente!")
    print("🔒 Recomendo regenerar uma nova chave depois do teste")
    print("🔗 Acesse: https://the-odds-api.com/ > Account > Regenerate Key")
    print()
    
    # Inicializa tester
    tester = TheOddsAPITester(api_key)
    
    # Teste 1: Conexão básica
    if not tester.test_api_connection():
        print("❌ Falha na conexão. Verifique a chave de API.")
        return
    
    # Teste 2: Lista esportes disponíveis
    sports = tester.list_available_sports()
    
    # Teste 3: Tenta pegar odds do Brasileirão
    if sports:
        print("\n" + "="*60)
        choice = input("🤔 Deseja testar odds específicas? (y/n): ").lower()
        
        if choice == 'y':
            # Testa múltiplas ligas
            all_matches = tester.try_multiple_soccer_leagues()
            
            if any(all_matches.values()):
                print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
                print("🎉 A API está funcionando perfeitamente!")
            else:
                print("\n⚠️  API funciona, mas sem partidas no momento")
                print("💡 Isso é normal - depende da temporada esportiva")
        else:
            print("\n✅ Teste básico concluído!")
    
    print(f"\n🔍 PRÓXIMOS PASSOS:")
    print("1. 🔒 Regenere sua API key por segurança")
    print("2. 📊 Você tem ~500 requests/mês gratuitos")
    print("3. 🎯 Use a API para seus projetos!")

if __name__ == "__main__":
    try:
        import requests, pandas
        main()
    except ImportError:
        print("📦 Instalando dependências...")
        import subprocess
        subprocess.run(["pip", "install", "requests", "pandas"])
        main()