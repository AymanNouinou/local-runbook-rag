import json
import re

import httpx

from app.retrieval import Match


SYSTEM_PROMPT = """Tu es un assistant SRE prudent. Réponds uniquement à partir des extraits fournis.
N'invente jamais une commande. Ne prétends jamais avoir exécuté une action. Retourne uniquement un objet JSON avec les clés summary, checks, commands, warnings et confidence. Les listes contiennent des chaînes et confidence est un nombre entre 0 et 1."""


def extract_commands(matches: list[Match]) -> list[str]:
    commands: list[str] = []
    for match in matches:
        for block in re.findall(r"```(?:bash|sh)?\n(.*?)```", match.chunk.content, flags=re.DOTALL):
            for line in block.splitlines():
                command = line.strip()
                if command and not command.startswith("#") and command not in commands:
                    commands.append(command)
    return commands[:6]


def extractive_answer(matches: list[Match]) -> dict:
    if not matches:
        return {
            "summary": "La documentation locale ne contient pas assez d’éléments pour répondre.",
            "checks": [],
            "commands": [],
            "warnings": ["Compléter les runbooks ou reformuler la question avant toute intervention."],
            "confidence": 0.0,
        }
    sections = [f"{match.chunk.title} — {match.chunk.section}" for match in matches]
    checks = []
    for match in matches:
        for line in match.chunk.content.splitlines():
            cleaned = line.strip().lstrip("-0123456789. ")
            if line.strip().startswith(("-", "1.", "2.", "3.", "4.", "5.")) and cleaned:
                checks.append(cleaned)
    return {
        "summary": "Consulter en priorité : " + "; ".join(sections) + ".",
        "checks": checks[:6],
        "commands": extract_commands(matches),
        "warnings": ["Les commandes sont proposées en lecture seule et doivent être validées avant exécution."],
        "confidence": min(0.9, 0.35 + matches[0].score / 4),
    }


async def ollama_answer(matches: list[Match], question: str, base_url: str, model: str) -> dict:
    context = "\n\n".join(
        f"SOURCE: {m.chunk.source} | SECTION: {m.chunk.section}\n{m.chunk.content}" for m in matches
    )
    prompt = f"QUESTION:\n{question}\n\nDOCUMENTATION:\n{context}"
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{base_url.rstrip('/')}/api/chat",
            json={
                "model": model,
                "stream": False,
                "format": "json",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "options": {"temperature": 0.1},
            },
        )
        response.raise_for_status()
        return json.loads(response.json()["message"]["content"])
