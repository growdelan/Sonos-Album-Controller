# Profil OpenAI Codex i format narzędzi

Celem tego pliku jest utrzymanie jednego, spójnego profilu pracy dla OpenAI Codex. To repozytorium jest szablonem 100% pod Codex, dlatego nie definiuje profili dla innych dostawców.

## Aktywny profil

| Profil | Modele / rodziny | Preferowany format edycji | Styl instrukcji | Ryzyka | Reguła harnessu |
|---|---|---|---|---|---|
| `openai_patch` | OpenAI Codex / modele OpenAI używane w Codex | patch/diff, małe hunki, `apply_patch`, jawne ścieżki plików | precyzyjny, literalny, krokowy | zbyt szeroki diff, niepotrzebne refaktory, dopisywanie rzeczy spoza kontraktu | dawaj konkretne zakresy, małe zmiany i jawne walidacje |

## Polityka wyboru modelu

- Domyślny i jedyny profil harnessu to `openai_patch`.
- Wybierz konkretny wariant OpenAI/Codex przed startem milestone’u.
- Nie zmieniaj wariantu modelu w środku milestone’u, batcha ani review.
- Jeśli różne role w Codex mają działać w osobnych sesjach, każda rola powinna startować jako świeży subagent z własnym, krótkim handoffem, a nie przejmować pełną surową historię poprzedniej roli.
- Jeśli musisz użyć narzędzia innego niż patch/diff, potraktuj to jako wyjątek, opisz powód w `STATUS.md` i wróć do małych patchy przy kolejnej zmianie.

## Przełączenie wariantu modelu mid-chat

Przełączenie w środku rozmowy jest dopuszczalne tylko, gdy istnieje konkretny powód, np. limit, niedostępność albo wyraźna potrzeba innego wariantu OpenAI. Nie traktuj przełączenia jako darmowego skrótu.

Procedura:

1. Zatrzymaj pracę po walidacji albo w jasno opisanym punkcie.
2. Przygotuj handoff według `HANDOFF-TEMPLATE.md`.
3. W handoffie zapisz:
   - co zostało zrobione,
   - co jeszcze jest do zrobienia,
   - jakie pliki zmieniono,
   - jakie walidacje wykonano,
   - jakie błędy narzędzi wystąpiły,
   - jakich założeń z poprzedniej części rozmowy nie należy dziedziczyć bez sprawdzenia.
4. Nowy kontekst zaczyna od profilu `openai_patch` i sprawdza aktualny stan repo przed dalszą pracą.

## Instrukcja dla agentów

Na początku pracy wpisz w odpowiedzi lub w `STATUS.md`, jeśli praca jest dłuższa:

```text
Profil modelu: openai_patch
Format edycji: patch/diff, małe hunki, apply_patch
Model switch: nie
```

Nie trzeba tego robić przy każdej drobnej odpowiedzi. Wystarczy przy starcie milestone’u, batcha, dużej poprawki albo po handoffie.
