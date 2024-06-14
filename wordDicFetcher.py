import random
import requests
from bs4 import BeautifulSoup

# Function to fetch definitions using web scraping
def fetch_definitions(word):
    try:
        url = f"https://www.merriam-webster.com/dictionary/{word}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the definition
        definition_tag = soup.find('span', class_='dtText')
        if definition_tag:
            definition = definition_tag.text.strip()
            return definition
        else:
            return "Definition not found."

    except requests.RequestException as e:
        print(f"Error fetching definition for '{word}': {e}")
        return None
    except Exception as e:
        print(f"An error occurred while fetching definition for '{word}': {e}")
        return None

# Function to read the file and categorize the words
def read_and_categorize_file(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            
            # Extracting columns from each line
            words_data = []
            for line in lines:
                columns = line.strip().split()
                if len(columns) >= 3:
                    word_number = columns[0]
                    usage_frequency = int(columns[1])
                    word = ' '.join(columns[2:])
                    words_data.append((word_number, usage_frequency, word))
            
            # Sort the words by usage frequency in descending order
            words_data.sort(key=lambda x: x[1], reverse=True)
            
            # Prompt the user to fetch definitions interactively
            print("Welcome to the Word Definition Fetcher!")
            print("You can fetch definitions for 10 randomly selected words from the file.")
            input("Press Enter to continue...")

            # Select 10 words randomly from the sorted list
            selected_words = random.sample(words_data, min(len(words_data), 10))
            
            # Print table header
            print("\nFetching definitions for selected words:")
            print(f"{'Word Number':<12} {'Usage Frequency':<15} {'Word':<15} {'Definition':<60}")
            print("-" * 90)
            
            # Fetch and print definitions for each selected word
            for word_data in selected_words:
                word_number, usage_frequency, word = word_data
                definition = fetch_definitions(word)
                print(f"{word_number:<12} {usage_frequency:<15} {word:<15} {definition:<60}")
                
    except FileNotFoundError:
        print("Error: File not found. Please check the filename and try again.")
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# File name
filename = '2000words.py'

# Reading and categorizing the file
read_and_categorize_file(filename)