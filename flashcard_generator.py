from google import genai
from google.genai import types
from pydantic import BaseModel
import pathlib
import json
import genanki

def generate_flashcards_from_pdf(arquivo_pdf: str):
    client = genai.Client()
    filepath = pathlib.Path(arquivo_pdf)

    class Flashcard(BaseModel):
        question: str
        answer: str

    prompt = """Based on the following text content, please generate a comprehensive set of flashcards that cover the entire document.
    The output must be a valid JSON array of objects. Each object should represent a single flashcard with two keys: "question" and "answer".
    The questions should be clear and concise, and the answers should accurately reflect the information in the text.
    If the content involves mathematical expressions, please format them using LaTeX notation inside [$] and [/$] tags.
    The cards should be made in the same language as the document.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=filepath.read_bytes(),
                mime_type='application/pdf',
            ),
            prompt
        ],
        config = {
            "response_mime_type": "application/json",
            "response_schema": list[Flashcard],
        }
    )

    print(response.candidates[0].content.parts[0].text)

    json_str = response.candidates[0].content.parts[0].text
    flashcards = json.loads(json_str)

    with open('flashcards.json', 'w', encoding='utf-8') as f:
        json.dump(flashcards, f, ensure_ascii=False, indent=2)

    return flashcards

def create_flashcard_deck(nome_deck:str, flashcards: list):
    model = genanki.Model(
        1607392319,
        'Modelo Padrão',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ]
    )

    deck = genanki.Deck(
        2059400110,
        nome_deck
    )

    for card in flashcards:
        note = genanki.Note(
            model=model,
            fields=[card['question'], card['answer']]
        )
        deck.add_note(note)

    genanki.Package(deck).write_to_file('flashcards.apkg')

def main(arquivo_pdf: str):
    filepath = pathlib.Path(arquivo_pdf)
    nome_deck = filepath.name.replace('.pdf', '')

    flashcards = generate_flashcards_from_pdf(arquivo_pdf)

    with open('flashcards.json', 'r', encoding='utf-8') as f:
        flashcards = json.load(f)

    create_flashcard_deck(nome_deck, flashcards)

arquivo_pdf = "arquivo"

main(arquivo_pdf)