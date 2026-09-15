"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

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


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt utilizando a função utilitária do projeto.

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome completo do repositório no Hub ({username}/{prompt})
        prompt_data: Dicionário contendo dados, prompts e metadados

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        print(f"📤 Publicando prompt no LangSmith Hub: {prompt_name}...")

        system_prompt = prompt_data.get("system_prompt", "").strip()
        user_prompt = prompt_data.get("user_prompt", "{bug_report}").strip()

        # Criação do ChatPromptTemplate com input_variable {bug_report}
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        description = prompt_data.get("description", "Prompt otimizado para converter bugs em User Stories")
        tags = prompt_data.get("tags", ["bug-to-user-story", "v2-optimized"])

        # Push com visibilidade pública (new_repo_is_public=True)
        hub_url = hub.push(
            repo_full_name=prompt_name,
            object=chat_prompt,
            new_repo_is_public=True,
            new_repo_description=description,
            tags=tags
        )

        print(f"✓ Prompt publicado com sucesso no LangSmith Hub!")
        print(f"🔗 URL: https://smith.langchain.com/hub/{prompt_name}")
        return True

    except Exception as e:
        print(f"❌ Erro ao publicar prompt no LangSmith Hub: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPT OTIMIZADO PARA O LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    prompt_path = "prompts/bug_to_user_story_v2.yml"
    print(f"📖 Carregando prompt otimizado de: {prompt_path}...")
    yaml_content = load_yaml(prompt_path)
    if not yaml_content:
        print(f"❌ Não foi possível ler o arquivo: {prompt_path}")
        return 1

    prompt_data = yaml_content.get("bug_to_user_story_v2", yaml_content)

    print("🔍 Validando conformidade do prompt...")
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Validação do prompt falhou com os seguintes erros:")
        for err in errors:
            print(f"   - {err}")
        return 1
    print("✓ Validação estrutural do prompt aprovada!")

    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    prompt_name = f"{username}/bug_to_user_story_v2"

    success = push_prompt_to_langsmith(prompt_name, prompt_data)
    if success:
        print("\n✅ Etapa de Push concluída com sucesso!")
        return 0
    else:
        print("\n❌ Falha na etapa de Push.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
