# from openai import OpenAI
import requests
import re
import urllib.request
from bs4 import BeautifulSoup
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
import os
import pandas as pd
import numpy as np
import tiktoken
import matplotlib.pyplot as plt
from main import client
from ast import literal_eval
import unicodedata
import ast  # for converting embeddings saved as strings back to arrays
from scipy import spatial


from dotenv import load_dotenv

load_dotenv()

HTTP_URL_PATTERN = r'^http[s]*://.+'

# Create a class to parse the HTML and get the hyperlinks
class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        # Create a list to store the hyperlinks
        self.hyperlinks = []
    # Override the HTMLParser's handle_starttag method to get the hyperlinks
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # If the tag is an anchor tag and it has an href attribute, add the href attribute to the list of hyperlinks
        if tag == "a" and "href" in attrs:
            self.hyperlinks.append(attrs["href"])

# Function to get the hyperlinks from a URL
def get_hyperlinks(url):
    # Try to open the URL and read the HTML
    try:
        # Open the URL and read the HTML
        with urllib.request.urlopen(url) as response:
            # If the response is not HTML, return an empty list
            if not response.info().get('Content-Type').startswith("text/html"):
                return []
            # Decode the HTML
            html = response.read().decode('utf-8')
    except Exception as e:
        print("error here",e,url)
        return []
    # Create the HTML Parser and then Parse the HTML to get hyperlinks
    parser = HyperlinkParser()
    parser.feed(html)
    return parser.hyperlinks

# Function to get the hyperlinks from a URL that are within the same domain
def get_domain_hyperlinks(local_domain, url):
    clean_links = []
    for link in set(get_hyperlinks(url)):
        clean_link = None
        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain:
                clean_link = link
        # If the link is not a URL, check if it is a relative link
        else:
            if link.startswith("/"):
                link = link[1:]
            elif link.startswith("#") or link.startswith("mailto:"):
                continue
            clean_link = "https://" + local_domain + "/" + link
        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)
    # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))

def crawl(url):
    try:
        # Parse the URL and get the domain
        local_domain = urlparse(url).netloc
        # Create a queue to store the URLs to crawl
        queue = deque([url])
        # Create a set to store the URLs that have already been seen (no duplicates)
        seen = set([url])
        # Create a directory to store the text files
        if not os.path.exists("text/"):
            os.mkdir("text/")
        if not os.path.exists("text/"+local_domain+"/"):
            os.mkdir("text/" + local_domain + "/")
        # While the queue is not empty, continue crawling
        while queue:
            # Get the next URL from the queue
            url = queue.pop()
            print(url) # for debugging and to see the progress
            # Save text from the url to a <url>.txt file
            file_path = 'text/'+local_domain+'/'+url[8:].replace("/", "_") + ".txt"
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    # Get the text from the URL using BeautifulSoup
                    soup = BeautifulSoup(requests.get(url).text, "html.parser")
                    # Get the text but remove the tags
                    text = soup.get_text()
                    # If the crawler gets to a page that requires JavaScript, it will stop the crawl
                    if ("You need to enable JavaScript to run this app." in text):
                        print("Unable to parse page " + url + " due to JavaScript being required") 
                    # Otherwise, write the text to the file in the text directory
                    f.write(text)
            except UnicodeEncodeError as e:
                print(f"UnicodeEncodeError: {e} - Skipping file {file_path}")
                continue
            except Exception as e:
                print(f"Error: {e} - Failed to write file {file_path}")
            # Get the hyperlinks from the URL and add them to the queue
            for link in get_domain_hyperlinks(local_domain, url):
                if link not in seen:
                    queue.append(link)
                    seen.add(link)
    except Exception as e:
        print("error in crawl", e)

# crawl(full_url)
def remove_newlines(serie):
    serie = serie.str.replace('\n', ' ')
    serie = serie.str.replace('\\n', ' ')
    serie = serie.str.replace('  ', ' ')
    serie = serie.str.replace('   ', ' ')
    serie = serie.str.replace("'", " ")
    serie = serie.str.replace("’", " ")
    serie = serie.str.replace("©", " ")
    serie = serie.str.replace("“", '"')
    serie = serie.str.replace("”", '"')
    serie = serie.str.replace("‘", "'")
    serie = serie.str.replace("’", "'")
    serie = serie.apply(lambda x: unicodedata.normalize("NFKD", x).replace('\u00A0', ' ')) 
    return serie

def data_cleaning():    
    # Create a list to store the text files
    texts = []
    text_file_count = 0
    # print(os.listdir("text/"))
    # Get all the text files in the text directory
    for file in os.listdir("text/"):
        # print(file)
        for text_file in os.listdir(f"text/{file}/"):
        # Open the file and read the text
            # print(text_file)
            with open(f"text/{file}/{text_file}", "r",encoding="utf-8") as f:
                text = f.read()
                text_file_count +=1
                # Omit the first 11 lines and the last 4 lines, then replace -, _, and #update with spaces.
                texts.append((file.replace('-', ' ').replace('_', ' ').replace('#update', '').replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace('©', "@"), text))
    # print("total files read: ",text_file_count)
    # Create a dataframe from the list of texts
    df = pd.DataFrame(texts, columns = ['fname', 'text'])
    # Set the text column to be the raw text with the newlines removed
    df['text'] = df.fname + ". " + remove_newlines(df.text)
    # Check if the directory exists, if not, create it
    if not os.path.exists("processed"):
        os.makedirs("processed")
    # df.to_csv("processed/scraped.csv")
    print("done data cleaning")
    return df


def token_generation():
    try:
        # Load the cl100k_base tokenizer which is designed to work with the ada-002 model
        tokenizer = tiktoken.get_encoding("cl100k_base")
        df = pd.read_csv("processed/scraped3.csv", index_col=0)
        df.columns = ['title', 'text']
        # Tokenize the text and save the number of tokens to a new column
        df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))
        # Visualize the distribution of the number of tokens per row using a histogram
        df.n_tokens.hist()
        # plt.show()
        max_tokens = 500
        # Function to split the text into chunks of a maximum number of tokens
        def split_into_many(text, max_tokens = max_tokens):
            # Split the text into sentences
            sentences = text.split('. ')
            # Get the number of tokens for each sentence
            n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in sentences]
            chunks = []
            tokens_so_far = 0
            chunk = []
            # Loop through the sentences and tokens joined together in a tuple
            for sentence, token in zip(sentences, n_tokens):
                # If the number of tokens so far plus the number of tokens in the current sentence is greater 
                # than the max number of tokens, then add the chunk to the list of chunks and reset
                # the chunk and tokens so far
                if tokens_so_far + token > max_tokens:
                    chunks.append(". ".join(chunk) + ".")
                    chunk = []
                    tokens_so_far = 0
                # If the number of tokens in the current sentence is greater than the max number of 
                # tokens, go to the next sentence
                if token > max_tokens:
                    continue
                # Otherwise, add the sentence to the chunk and add the number of tokens to the total
                chunk.append(sentence)
                tokens_so_far += token + 1
            # Add the last chunk to the list of chunks
            if chunk:
                chunks.append(". ".join(chunk) + ".")
            return chunks
        shortened = []
        # Loop through the dataframe
        for row in df.iterrows():
            # If the text is None, go to the next row
            if row[1]['text'] is None:
                continue
            # If the number of tokens is greater than the max number of tokens, split the text into chunks
            if row[1]['n_tokens'] > max_tokens:
                shortened += split_into_many(row[1]['text'])
            # Otherwise, add the text to the list of shortened texts
            else:
                shortened.append( row[1]['text'] )
        df = pd.DataFrame(shortened, columns = ['text'])
        df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))
        df.n_tokens.hist()
        # plt.show()
        print("token generation done")
        return df
    except Exception as e:
        print("error in token generation:", e)

def get_embedding(text, model):
   try:
    text = text.replace("\n", " ").replace("'"," ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding
   except Exception as e:
       print("error in get embedding:",e)

def ada_embedding():
    try:
        df = token_generation()
        df['ada_embedding'] = df['text'].apply(lambda x: get_embedding(x, model=os.getenv("EMBEDDING_MODEL")))
        # df['embeddings'] = df['ada_embedding'].apply(literal_eval).apply(np.array)
        df.reset_index(inplace=True)
        if not os.path.exists("output"):
            os.makedirs("output")
        df.to_csv('output/embeddings2.csv', index=False)
        df.head()
        print("ada_embedding done")
    except Exception as e:
        print("error in ada embedding:",e)

# df = ada_embedding()
# search function
def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 100
) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding_response = client.embeddings.create(
        model=os.getenv("GPT_model"),
        input=query,
    )
    query_embedding = query_embedding_response.data[0].embedding
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embedding"]))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]

def query_message(self, query):
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    strings, relatednesses = strings_ranked_by_relatedness(query, df)  # Replace with your function or logic
    introduction = 'Use the below articles to answer the subsequent question. If the answer cannot be found, write "I could not find an answer."'
    question = f"\n\nQuestion: {query}"
    message = introduction
    for string in strings:
        next_article = f'\n\nSource text:\n"""\n{string}\n"""'
        if (
            self.num_tokens(message + next_article + question) > 4096
        ):
            break
        else:
            message += next_article
    return message + question

df = pd.read_csv(r"output\embeddings2.csv")
df.drop("index", axis=1, inplace= True)
df['embeddings'] = df['ada_embedding'].apply(literal_eval).apply(np.array)

