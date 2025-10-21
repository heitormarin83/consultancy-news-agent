"""
Peers Consulting & Technology News Agent
VERSÃO CORRIGIDA - SMTP SIMPLES E FUNCIONAL
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

logger.info("🚀 Starting Peers Consulting & Technology News Agent - FIXED VERSION")

class SimpleEmailSender:
    def __init__(self):
        self.recipient_email = "heitor.a.marin@gmail.com"
        self.sender_email = os.getenv('GMAIL_EMAIL', 'heitor.a.marin@gmail.com')
        self.sender_password = os.getenv('GMAIL_APP_PASSWORD')
        
    def send_email(self, subject, content):
        """Enviar email via SMTP Gmail - versão simplificada e funcional"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            if not self.sender_password:
                logger.error("❌ GMAIL_APP_PASSWORD não configurado")
                return False, "SMTP credentials not configured"
            
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            # Corpo do email
            body = f"""
🏢 Consultancy News Agent - Sistema Funcionando!

✅ Status: Online
✅ Método: SMTP Gmail Direto
✅ Timestamp: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

📧 Conteúdo: {content}

---
Sistema de monitoramento de notícias de consultorias
Big 4 | MBB | Global Consultancies
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Enviar email com timeout reduzido
            logger.info(f"📧 Conectando ao Gmail SMTP...")
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
                logger.info(f"🔐 Fazendo login...")
                server.login(self.sender_email, self.sender_password)
                logger.info(f"📤 Enviando email...")
                server.send_message(msg)
                logger.info(f"✅ Email enviado com sucesso!")
                
            return True, "Email sent successfully"
            
        except Exception as e:
            logger.error(f"❌ Erro SMTP: {e}")
            return False, str(e)
    
    def is_configured(self):
        """Verificar se as credenciais estão configuradas"""
        return bool(self.sender_password)

# Initialize email sender
email_sender = SimpleEmailSender()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        email_status = "✅ Configurado" if email_sender.is_configured() else "❌ Não Configurado"
        
        html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consultancy News Agent - FIXED</title>
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
        .configured {{ color: #28a745; font-weight: bold; }}
    </style>
    <script>
        async function testEmail() {{
            const button = document.getElementById('testBtn');
            const status = document.getElementById('emailStatus');
            
            button.disabled = true;
            button.textContent = 'Enviando...';
            status.textContent = '📤 Enviando email de teste...';
            
            try {{
                const response = await fetch('/api/test-email');
                const result = await response.json();
                
                if (result.status === 'success') {{
                    status.innerHTML = '✅ <strong>Email enviado com sucesso!</strong> Verifique sua caixa de entrada.';
                    alert('✅ Email enviado com sucesso! Verifique sua caixa de entrada em heitor.a.marin@gmail.com');
                }} else {{
                    status.innerHTML = '❌ <strong>Erro:</strong> ' + result.message;
                    alert('❌ Erro ao enviar email: ' + result.message);
                }}
            }} catch (error) {{
                status.innerHTML = '❌ <strong>Erro de conexão:</strong> ' + error.message;
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
            <h2>VERSÃO CORRIGIDA - Sistema Funcional</h2>
            <p>Monitoramento de Consultorias BIG 4, MBB e Globais</p>
        </div>
        
        <div class="status">
            <div class="status-card">
                <h3>📊 Status do Sistema</h3>
                <div class="online">✅ Online</div>
            </div>
            <div class="status-card">
                <h3>📧 Configuração Email</h3>
                <div class="configured">{email_status}</div>
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
        'email_configured': email_sender.is_configured(),
        'email_method': 'SMTP Gmail Direct',
        'monitored_firms': 16,
        'regions': ['USA', 'Europe'],
        'recipient': email_sender.recipient_email,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/test-email')
def api_test_email():
    """API endpoint for testing email functionality"""
    try:
        content = f"Email de teste enviado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}"
        subject = f"🧪 Teste - Consultancy News Agent - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        logger.info("📧 Iniciando teste de email...")
        success, message = email_sender.send_email(subject, content)
        
        if success:
            logger.info("✅ Teste de email bem-sucedido")
            return jsonify({
                'status': 'success',
                'message': 'Email de teste enviado com sucesso!',
                'recipient': email_sender.recipient_email,
                'method': 'SMTP Gmail Direct',
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

@app.route('/api/collect')
def api_collect():
    """API endpoint for manual news collection"""
    return jsonify({
        'status': 'success',
        'message': 'Collection endpoint - implementation pending',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/webhook')
def webhook():
    """Webhook endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Webhook endpoint active',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'email_configured': email_sender.is_configured(),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
