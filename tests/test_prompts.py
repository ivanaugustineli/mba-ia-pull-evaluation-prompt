"""
Testes automatizados para validação de prompts.
Utiliza preferencialmente as funções utilitárias de src/utils.py.
"""

import sys
from pathlib import Path
import pytest

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import load_yaml, validate_prompt_structure


class TestPrompts:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Carrega dados do prompt otimizado v2 utilizando utils.load_yaml."""
        yaml_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
        data = load_yaml(str(yaml_path))
        assert data is not None, f"Falha ao carregar arquivo YAML em: {yaml_path}"
        self.prompt_data = data.get("bug_to_user_story_v2", data)

    def test_prompt_structure_validation(self):
        """Valida a integridade estrutural básica usando utils.validate_prompt_structure."""
        is_valid, errors = validate_prompt_structure(self.prompt_data)
        assert is_valid, f"Falha na validação de estrutura do prompt: {errors}"

    def test_prompt_has_system_prompt(self):
        """Garante existência e preenchimento da mensagem de sistema."""
        # Validação estrutural via utils
        _, errors = validate_prompt_structure(self.prompt_data)
        system_prompt_errors = [e for e in errors if "system_prompt" in e]
        assert not system_prompt_errors, f"Erros no system_prompt: {system_prompt_errors}"

        system_prompt = self.prompt_data.get("system_prompt", "")
        assert isinstance(system_prompt, str), "O campo 'system_prompt' deve ser uma string"
        assert len(system_prompt.strip()) > 0, "O 'system_prompt' está vazio"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        system_prompt = self.prompt_data.get("system_prompt", "").lower()
        role_indicators = [
            "product manager",
            "você é um",
            "voce e um",
            "persona",
            "especialista em produto",
        ]
        assert any(indicator in system_prompt for indicator in role_indicators), (
            "O prompt não define uma persona ou papel explícito (ex: 'Você é um Product Manager')"
        )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown e BDD ('Dado... Quando... Então...')."""
        system_prompt = self.prompt_data.get("system_prompt", "").lower()
        assert "markdown" in system_prompt, "O prompt deve exigir explicitamente formatação em Markdown"
        assert "dado" in system_prompt, "O prompt deve exigir formato BDD contendo a cláusula 'Dado'"
        assert "quando" in system_prompt, "O prompt deve exigir formato BDD contendo a cláusula 'Quando'"
        assert "então" in system_prompt or "entao" in system_prompt, (
            "O prompt deve exigir formato BDD contendo a cláusula 'Então'"
        )

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = self.prompt_data.get("system_prompt", "")
        system_prompt_lower = system_prompt.lower()
        has_examples_keyword = (
            "exemplo" in system_prompt_lower
            or "example" in system_prompt_lower
            or "few-shot" in system_prompt_lower
        )
        assert has_examples_keyword, "O prompt deve conter seção de exemplos Few-Shot demonstrando entrada e saída"
        examples_count = system_prompt_lower.count("exemplo") + system_prompt_lower.count("example")
        assert examples_count >= 2, (
            f"O prompt deve conter múltiplos exemplos (mínimo 2), encontrados: {examples_count}"
        )

    def test_prompt_no_todos(self):
        """Garante que não existem TODOs residuais, validando também via utils.validate_prompt_structure."""
        # Validação de TODOs via utils
        _, errors = validate_prompt_structure(self.prompt_data)
        todo_errors = [e for e in errors if "TODO" in e]
        assert not todo_errors, f"TODO detectado por validate_prompt_structure: {todo_errors}"

        system_prompt = self.prompt_data.get("system_prompt", "")
        assert "[todo]" not in system_prompt.lower(), "O system_prompt contém a marcação [TODO]"
        assert "todo" not in system_prompt.lower(), "O system_prompt contém a palavra TODO residual"

    def test_minimum_techniques(self):
        """Verifica se no mínimo 2 técnicas foram listadas nos metadados do YAML."""
        # Validação de técnicas mínimas via utils
        _, errors = validate_prompt_structure(self.prompt_data)
        tech_errors = [e for e in errors if "técnicas" in e.lower() or "tecnicas" in e.lower()]
        assert not tech_errors, f"Erro de técnicas mínimas identificado por utils: {tech_errors}"

        techniques = self.prompt_data.get("techniques_applied", [])
        assert isinstance(techniques, list), "O campo 'techniques_applied' deve ser uma lista nos metadados do YAML"
        assert len(techniques) >= 2, (
            f"Metadados devem listar no mínimo 2 técnicas reconhecidas, encontradas: {len(techniques)}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])