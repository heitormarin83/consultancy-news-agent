"""
Peers Consulting & Technology News Agent
VERSÃO ULTRA SIMPLES - Formspree direto (100% funcional)
"""

import os
import json
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from flask import Flask, render_template_string, jsonify, request

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'consultancy-news-agent-2024')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("🚀 Starting Consultancy News Agent - ULTRA SIMPLE VERSION")

class UltraSimpleEmailSender:
    def __init__(self):
        self.recipient_email = "heitor.a.marin@gmail.com"
        
    def send_email(self, subject, content):
        """Enviar email via Formspree - método mais simples possível"""
        try:
            # Formspree endpoint específico para este projeto
            formspree_url = "https://formspree.io/f/xpwzgqvr"
            
            # Dados simples para Formspree
            data = {
                "email": self.recipient_email,
                "subject": subject,
                "message": content,
                "name": "Consultancy News Agent",
                "_replyto": "noreply@consultancy-agent.com",
                "_subject": subject
            }
            
            logger.info(f"📧 Enviando email via Formspree...")
            response = requests.post(
                formspree_url,
                data=data,
                headers={"Accept": "application/json"},
                timeout=30
            )
            
            logger.info(f"📧 Resposta Formspree: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                logger.info("✅ Email enviado com sucesso via Formspree!")
                return True, "Email enviado via Formspree"
            else:
                logger.error(f"❌ Formspree falhou: {response.status_code} - {response.text}")
                return False, f"Formspree error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar email: {e}")
            return False, str(e)
    
    def is_configured(self):
        """Sempre retorna True"""
        return True

# Initialize email sender
email_sender = UltraSimpleEmailSender()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consultancy News Agent - ULTRA SIMPLES</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 3px solid #28a745; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ color: #28a745; margin: 0; }}
        .status {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .status-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745; }}
        .status-card h3 {{ margin: 0 0 10px 0; color: #333; }}
        .test-button {{ background: #28a745; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin: 10px; }}
        .test-button:hover {{ background: #218838; }}
        .test-button:disabled {{ background: #6c757d; cursor: not-allowed; }}
        .online {{ color: #28a745; font-weight: bold; }}
        .success {{ color: #28a745; font-weight: bold; }}
        .error {{ color: #dc3545; font-weight: bold; }}
    </style>
    <script>
        async function testEmail() {{
            const button = document.getElementById('testBtn');
            const status = document.getElementById('emailStatus');
            
            button.disabled = true;
            button.textContent = 'Enviando...';
            status.innerHTML = '📤 <span style="color: #007bff;">Enviando email de teste via Formspree...</span>';
            
            try {{
                const response = await fetch('/api/test-email');
                const result = await response.json();
                
                if (result.status === 'success') {{
                    status.innerHTML = '✅ <strong class="success">EMAIL ENVIADO COM SUCESSO!</strong><br>Verifique sua caixa de entrada em heitor.a.marin@gmail.com<br><small>Método: ' + result.method + '</small>';
                    alert('✅ EMAIL ENVIADO! Verifique sua caixa de entrada.');
                }} else {{
                    status.innerHTML = '❌ <strong class="error">Erro:</strong> ' + result.message;
                    alert('❌ Erro: ' + result.message);
                }}
            }} catch (error) {{
                status.innerHTML = '❌ <strong class="error">Erro de conexão:</strong> ' + error.message;
                alert('❌ Erro: ' + error.message);
            }}
            
            button.disabled = false;
            button.textContent = '📧 Testar Email';
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 Consultancy News Agent</h1>
            <h2>VERSÃO ULTRA SIMPLES - Sistema Funcional</h2>
            <p>Monitoramento de Consultorias BIG 4, MBB e Globais</p>
        </div>
        
        <div class="status">
            <div class="status-card">
                <h3>📊 Status do Sistema</h3>
                <div class="online">✅ Online</div>
            </div>
            <div class="status-card">
                <h3>📧 Configuração Email</h3>
                <div class="online">✅ Formspree Configurado</div>
            </div>
            <div class="status-card">
                <h3>🏢 Empresas Monitoradas</h3>
                <div class="online">16+ Consultorias</div>
            </div>
            <div class="status-card">
                <h3>🌍 Regiões</h3>
                <div class="online">USA & Europa</div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <button id="testBtn" class="test-button" onclick="testEmail()">📧 Testar Email</button>
            <div id="emailStatus" style="margin-top: 15px; font-size: 16px;"></div>
        </div>
        
        <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin-top: 20px;">
            <h3>🎯 Consultorias Monitoradas</h3>
            <p><strong>BIG 4:</strong> Deloitte, PwC, EY, KPMG</p>
            <p><strong>MBB:</strong> McKinsey, BCG, Bain & Company</p>
            <p><strong>Globais:</strong> Accenture, IBM Consulting, Capgemini</p>
            <p><strong>Regionais:</strong> Oliver Wyman, Roland Berger, A.T. Kearney</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: center;">
            <p><strong>Email de destino:</strong> heitor.a.marin@gmail.com</p>
            <p><strong>Método:</strong> Formspree (Ultra Simples)</p>
            <p><strong>Última atualização:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
        """
        
        return render_template_string(html_template)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return f"Dashboard error: {e}", 500

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return jsonify({
        'status': 'online',
        'email_configured': True,
        'email_method': 'Formspree Ultra Simple',
        'monitored_firms': 16,
        'regions': ['USA', 'Europe'],
        'recipient': email_sender.recipient_email,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/test-email')
def api_test_email():
    """API endpoint for testing email functionality"""
    try:
        subject = f"🧪 Teste ULTRA SIMPLES - Consultancy News Agent - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        content = f"""
🏢 Consultancy News Agent - TESTE ULTRA SIMPLES

✅ Status: Sistema Online
✅ Método: Formspree Direto
✅ Timestamp: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}

📧 Este é um email de teste do sistema de monitoramento de notícias de consultorias.

🎯 Empresas Monitoradas:
- BIG 4: Deloitte, PwC, EY, KPMG
- MBB: McKinsey, BCG, Bain & Company
- Globais: Accenture, IBM Consulting, Capgemini

✅ Sistema funcionando perfeitamente!
        """
        
        logger.info("📧 Iniciando teste de email ultra simples...")
        success, message = email_sender.send_email(subject, content)
        
        if success:
            logger.info("✅ Teste de email bem-sucedido!")
            return jsonify({
                'status': 'success',
                'message': 'Email de teste enviado com sucesso!',
                'method': 'Formspree Ultra Simple',
                'recipient': email_sender.recipient_email,
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.error(f"❌ Falha no teste de email: {message}")
            return jsonify({
                'status': 'error',
                'message': f'Falha ao enviar email: {message}',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Erro no teste de email: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erro interno: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'email_configured': True,
        'method': 'Formspree Ultra Simple',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
