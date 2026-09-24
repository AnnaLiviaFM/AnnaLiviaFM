"""Gera cards de estatísticas em tons pastel (rosa) para o README do perfil."""
import json, os, urllib.request
from collections import Counter

USER = os.environ.get("GH_USER", "AnnaLiviaFM")
TOKEN = os.environ.get("GITHUB_TOKEN")
OUT = os.environ.get("OUT_DIR", "cards")

# paleta fofa
BG, BORDA, TITULO, TEXTO, SUAVE = "#FFF5F9", "#F8C8DC", "#C77DAA", "#5E4B56", "#9C8792"
CORES = ["#F4A6C6", "#CDB4DB", "#B5EAD7", "#FFD6A5", "#A2D2FF", "#FFC8DD"]
FONTE = "'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif"


def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "readme-cards")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def moldura(largura, altura, titulo, corpo):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}">
  <rect x="1" y="1" rx="16" width="{largura-2}" height="{altura-2}" fill="{BG}" stroke="{BORDA}" stroke-width="2"/>
  <text x="25" y="38" font-family="{FONTE}" font-size="18" font-weight="700" fill="{TITULO}">{titulo}</text>
{corpo}
</svg>'''


def card_stats(user, repos):
    estrelas = sum(r["stargazers_count"] for r in repos)
    itens = [
        (CORES[0], "Repositórios", user["public_repos"]),
        (CORES[3], "Estrelas", estrelas),
        (CORES[2], "Seguidores", user["followers"]),
        (CORES[1], "Forks recebidos", sum(r["forks_count"] for r in repos)),
    ]
    linhas = []
    for i, (cor, nome, valor) in enumerate(itens):
        y = 75 + i * 28
        linhas.append(
            f'  <circle cx="31" cy="{y-5}" r="6" fill="{cor}"/>\n'
            f'  <text x="45" y="{y}" font-family="{FONTE}" font-size="14" fill="{TEXTO}">{nome}</text>\n'
            f'  <text x="335" y="{y}" font-family="{FONTE}" font-size="14" font-weight="700" fill="{TITULO}" text-anchor="end">{valor}</text>'
        )
    return moldura(360, 185, "✿ meus números", "\n".join(linhas))


def card_linguagens(repos):
    total = Counter()
    for r in repos:
        for lang, b in api(f"/repos/{r['full_name']}/languages").items():
            total[lang] += b
    top = total.most_common(6)
    soma = sum(b for _, b in top) or 1
    largura_barra = 310
    # barra empilhada
    x, barra = 25, []
    for i, (lang, b) in enumerate(top):
        w = largura_barra * b / soma
        barra.append(f'    <rect x="{x:.1f}" y="55" width="{w:.1f}" height="10" fill="{CORES[i % len(CORES)]}"/>')
        x += w
    corpo = [f'  <clipPath id="c"><rect x="25" y="55" width="{largura_barra}" height="10" rx="5"/></clipPath>',
             '  <g clip-path="url(#c)">', *barra, '  </g>']
    # legenda em 2 colunas
    for i, (lang, b) in enumerate(top):
        cx = 25 + (i % 2) * 150
        cy = 92 + (i // 2) * 26
        corpo.append(
            f'  <circle cx="{cx+5}" cy="{cy-4}" r="5" fill="{CORES[i % len(CORES)]}"/>\n'
            f'  <text x="{cx+16}" y="{cy}" font-family="{FONTE}" font-size="13" fill="{TEXTO}">{esc(lang.replace(" Notebook", ""))} '
            f'<tspan fill="{SUAVE}">{100*b/soma:.1f}%</tspan></text>'
        )
    return moldura(360, 185, "✿ linguagens favoritas", "\n".join(corpo))


def main():
    user = api(f"/users/{USER}")
    repos = [r for r in api(f"/users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/stats.svg", "w", encoding="utf-8") as f:
        f.write(card_stats(user, repos))
    with open(f"{OUT}/linguagens.svg", "w", encoding="utf-8") as f:
        f.write(card_linguagens(repos))
    print("cards gerados em", OUT)


if __name__ == "__main__":
    main()
