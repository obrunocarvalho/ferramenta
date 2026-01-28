"""Funções centrais reutilizáveis para conversão de dados brutos em mensagens.
Executa quatro passos:
 1. Carrega especificações de cada jogo a partir de `formatos.yaml`.
 2. Converte uma linha crua (string) em dicionário de campos.
 3. Lê o template Jinja2 correspondente.
 4. Renderiza a mensagem pronta.
"""
from __future__ import annotations
import pathlib
from typing import Dict, List
import unicodedata
import re

import yaml
from jinja2 import Template

def slug(text: str) -> str:
    """Converte uma string em slug snake_case ASCII (minúsculas, sem acentos)."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s-]+", "_", text)

# ---------------------------------------------------------------------------
# Carregamento de configurações
# ---------------------------------------------------------------------------

def carregar_formatos(cfg_path: str | pathlib.Path = "formatos.yaml") -> Dict[str, dict]:
    """Lê o arquivo YAML que descreve separador e campos de cada jogo."""
    cfg_path = pathlib.Path(cfg_path)
    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ---------------------------------------------------------------------------
# Conversão linha → dicionário
# ---------------------------------------------------------------------------

def linha_para_dict(linha: str, campos: List[str], sep: str) -> Dict[str, str]:
    partes = linha.strip().split(sep)
    if len(partes) < len(campos):
        raise ValueError(
            f"Linha possui {len(partes)} campos, mas são necessários {len(campos)}: {linha!r}"
        )
    return dict(zip(campos, partes))

# ---------------------------------------------------------------------------
# Renderização final
# ---------------------------------------------------------------------------

def renderizar_linha(
    linha: str,
    jogo: str,
    formatos: Dict[str, dict] | None = None,
    template_path: str | pathlib.Path | None = None,
) -> str:
    """Converte *uma* linha crua na mensagem pronta para envio.

    Parâmetros
    ----------
    linha : str
        Linha de dados brutos.
    jogo : str
        Nome do jogo conforme aparece em `formatos.yaml`.
    formatos : dict, opcional
        Se já carregado externamente, para evitar I/O repetido.
    template_path : path-like, opcional
        Caminho do template Jinja2 a utilizar. Se None, assume `templates/{jogo}.txt`.
    """
    formatos = formatos or carregar_formatos()
    if jogo not in formatos:
        raise KeyError(f"Jogo '{jogo}' não encontrado em formatos.yaml")

    spec = formatos[jogo]
    dados = linha_para_dict(linha, spec["campos"], spec["separador"])

    tpl_path = pathlib.Path(template_path) if template_path else pathlib.Path("templates") / f"{slug(jogo)}.txt"
    template_str = tpl_path.read_text(encoding="utf-8")
    return Template(template_str).render(**dados)

# ---------------------------------------------------------------------------
# Utilitário em lote
# ---------------------------------------------------------------------------

def converter_arquivo(
    base_path: str | pathlib.Path,
    jogo: str,
    template_path: str | pathlib.Path | None = None,
    saida_path: str | pathlib.Path = "mensagens_prontas.txt",
) -> int:
    """Converte todas as linhas de *base_path* e grava em *saida_path*.
    Retorna o número de mensagens geradas.
    """
    formatos = carregar_formatos()
    mensagens: List[str] = []
    with pathlib.Path(base_path).open(encoding="utf-8") as f:
        for linha in f:
            if not linha.strip():
                continue  # ignora linhas vazias
            try:
                mensagens.append(
                    renderizar_linha(linha, jogo=jogo, formatos=formatos, template_path=template_path)
                )
            except Exception as exc:
                print(f"[WARN] Linha ignorada: {linha.strip()} → {exc}")
    # Junta todas as mensagens, separadas por “;” e quebra-linha, e garante
    # um “;” também no fim do último bloco.
    saida_texto = ";\n".join(mensagens) + ";"
    pathlib.Path(saida_path).write_text(saida_texto, encoding="utf-8")
    return len(mensagens)
