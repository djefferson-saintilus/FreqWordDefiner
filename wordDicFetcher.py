import os
import json
import random
import requests
import textwrap
import re
from bs4 import BeautifulSoup
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize color output
init(autoreset=True)

# Constants
CACHE_FILE = 'definitions_cache.json'
WORDS_FILE = '2000words.py'
MAX_DEF_LENGTH = 180
WRAP_WIDTH = 70

# Load cached definitions from file
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save definitions cache to file
def save_cache(cache):
    with open(CACHE_FILE, 'w') as file:
        json.dump(cache, file, indent=2)

# Clean and format the raw definition
def format_definition(text):
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)        # fix stuck words
    text = re.sub(r'\s+', ' ', text).strip()                # normalize whitespace
    if len(text) > MAX_DEF_LENGTH:
        text = text[:MAX_DEF_LENGTH].rsplit(' ', 1)[0] + "..."
    return "\n".join(textwrap.wrap(text, width=WRAP_WIDTH))

# Scrape definition from Merriam-Webster
def fetch_definitions(word, cache):
    if word in cache:
        return cache[word]

    try:
        url = f"https://www.merriam-webster.com/dictionary/{word}"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        definition_tags = soup.find_all('span', class_='dtText')
        definitions = [tag.get_text(strip=True).lstrip(":") for tag in definition_tags[:3]]
        raw_definition = "; ".join(definitions) if definitions else "Definition not found."

        cleaned_definition = format_definition(raw_definition)
        cache[word] = cleaned_definition
        return cleaned_definition

    except requests.RequestException as e:
        return f"Request error: {e}"
    except Exception as e:
        return f"Parsing error: {e}"

# Read words from file and build table
def read_and_categorize_file(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

            words_data = []
            for line in lines:
                columns = line.strip().split()
                if len(columns) >= 3:
                    word_number = columns[0]
                    usage_frequency = int(columns[1])
                    word = ' '.join(columns[2:])
                    words_data.append((word_number, usage_frequency, word))

            # Sort by frequency
            words_data.sort(key=lambda x: x[1], reverse=True)

            # Randomly select 10
            selected_words = random.sample(words_data, min(10, len(words_data)))

            print(Fore.CYAN + "\n=== Word Definition Fetcher ===")
            print(Fore.YELLOW + f"Processing file: {filename}\n")

            cache = load_cache()
            table_data = []

            for i, (word_number, usage_frequency, word) in enumerate(selected_words, start=1):
                print(Fore.GREEN + f"{i}. Fetching: {word}...", end=' ')
                definition = fetch_definitions(word, cache)
                print("Done.")
                table_data.append([
                    word_number,
                    usage_frequency,
                    word,
                    definition
                ])

            save_cache(cache)

            # Print final table
            print("\n" + tabulate(
                table_data,
                headers=["Word Number", "Usage Frequency", "Word", "Definition"],
                tablefmt="grid"
            ))

    except FileNotFoundError:
        print(Fore.RED + "Error: File not found.")
    except ValueError as ve:
        print(Fore.RED + f"Value error: {ve}")
    except Exception as e:
        print(Fore.RED + f"Unexpected error: {e}")

# Entry point
if __name__ == '__main__':
    read_and_categorize_file(WORDS_FILE)
