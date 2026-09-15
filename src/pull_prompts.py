"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

# Configura encoding UTF-8 no terminal Windows para evitar UnicodeEncodeError
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Assegura compatibilidade de variáveis de API key entre LangSmith e LangChain Hub
if os.getenv("LANGSMITH_API_KEY") and not os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")


def pull_prompts_from_langsmith(repo_name: str = "leonanluppi/bug_to_user_story_v1", output_path: str = "prompts/bug_to_user_story_v1.yml") -> bool:
    """
    Puxa o prompt inicial de baixa qualidade do LangSmith Prompt Hub e salva em arquivo YAML.

    Args:
        repo_name: Nome do repositório no LangSmith Hub
        output_path: Caminho de destino para salvar o arquivo YAML

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        print(f"📥 Puxando prompt do LangSmith Hub: {repo_name}...")
        prompt_template = hub.pull(repo_name)

        system_prompt = ""
        user_prompt = "{bug_report}"

        # Extrair mensagens do ChatPromptTemplate
        for message in getattr(prompt_template, "messages", []):
            msg_type = message.__class__.__name__
            content = ""
            if hasattr(message, "prompt") and hasattr(message.prompt, "template"):
                content = message.prompt.template
            elif hasattr(message, "content"):
                content = str(message.content)

            if "System" in msg_type:
                system_prompt = content
            elif "Human" in msg_type or "User" in msg_type:
                user_prompt = content

        prompt_dict = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"]
            }
        }

        success = save_yaml(prompt_dict, output_path)
        if success:
            print(f"✓ Prompt salvo com sucesso em: {output_path}")
            return True
        else:
            print(f"❌ Falha ao salvar arquivo YAML em: {output_path}")
            return False

    except Exception as e:
        print(f"❌ Erro ao puxar prompt do LangSmith Hub: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    success = pull_prompts_from_langsmith()
    if success:
        print("\n✅ Etapa de Pull concluída com sucesso!")
        return 0
    else:
        print("\n❌ Falha na etapa de Pull.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
