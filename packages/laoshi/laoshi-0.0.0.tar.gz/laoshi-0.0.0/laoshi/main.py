"""Main file from laoshi"""
import click
from laoshi.converter import Converter
from laoshi.translator import Translator
from laoshi.flashcardgenerator import FlashCardGenerator
from laoshi.deckmanager import DeckManager

SIMPLIFIED = "simplified"
TRADITIONAL = "traditional"
CHINESE_OPTIONS = [TRADITIONAL, SIMPLIFIED, "pinyin"]


@click.group()
def cli_group():
    """cli group function for click"""


@cli_group.command(help="Convert characters")
@click.option(
    "-t",
    "--to",
    default="pinyin",
    type=click.Choice(CHINESE_OPTIONS),
)
@click.argument("word")
def cc(to: str, word: str):
    """Change character function"""
    match to:
        case "traditional":
            click.echo(Converter.to_traditional(word))
        case "simplified":
            click.echo(Converter.to_simplified(word))
        case "pinyin":
            click.echo(Converter.to_pinyin(word))


@cli_group.command(help="Translate a phrase")
@click.option(
    "-t",
    "--to",
    default="en",
)
@click.argument("phrase")
def translate(to: str, phrase: str):
    """Translate a phrase"""
    click.echo(Translator().translate(phrase, dest=to))


@cli_group.group()
def manage_deck():
    """Manage deck group"""


@manage_deck.command()
@click.option(
    "-c",
    "--character",
    default="simplified",
    type=click.Choice([SIMPLIFIED, TRADITIONAL]),
)
@click.argument("deck_name")
@click.argument("seed")
def create_deck(character: str, deck_name: str, seed: str):
    """Create a deck function for click"""
    with FlashCardGenerator() as generator:
        flashcard = generator.create_flashcard(character, seed)
        DeckManager(deck_name).create_deck(flashcard)


@manage_deck.command()
@click.option(
    "-c",
    "--character",
    default="simplified",
    type=click.Choice([SIMPLIFIED, TRADITIONAL]),
)
@click.argument("deck_name")
@click.argument("word")
def add_note(character: str, deck_name: str, word: str):
    """add note function for click"""
    with FlashCardGenerator() as generator:
        flashcard = generator.create_flashcard(character, word)
        DeckManager(deck_name).add_note(flashcard)


if __name__ == "__main__":
    cli_group()
