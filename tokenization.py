import json

with open("vocab.json", "r", encoding="utf-8") as f:
    vocab = json.load(f)

with open("merges.txt", "r", encoding="utf-8") as f:
    merges = [tuple(line.strip().split()) for line in f.readlines()[1:]]

# Build ranks: a dict to lookup pair merge priority
merge_ranks = {pair: i for i, pair in enumerate(merges)}

# Reverse vocab to decode
id_to_token = {v: k for k, v in vocab.items()}


def get_pairs(word):
    """Get all symbol pairs from a list of symbols (word pieces)."""
    return {(word[i], word[i + 1]) for i in range(len(word) - 1)}


def bpe(token):
    """Apply BPE to a single token (word)."""
    word = list(token)
    pairs = get_pairs(word)

    while True:
        # Get valid pairs that exist in merge rules
        if not pairs: 
            print("No pairs found")
            break
        candidate_pairs = {pair: merge_ranks[pair] for pair in pairs if pair in merge_ranks}
        if not candidate_pairs:
            break

        # Find best (lowest rank)
        best_pair = min(candidate_pairs, key=candidate_pairs.get)

        # Merge best pair
        new_word = []
        i = 0
        while i < len(word):
            if i < len(word) - 1 and (word[i], word[i + 1]) == best_pair:
                new_word.append(word[i] + word[i + 1])
                i += 2
            else:
                new_word.append(word[i])
                i += 1

        word = new_word
        pairs = get_pairs(word)

    return word


def encode(text):
    """
    Tokenize and BPE-encode the input string manually using vocab and merges.
    """
    tokens = text.strip().split(" ")
    wordpieces = []

    for i, token in enumerate(tokens):
        # Add space prefix to all words except the first
        if i != 0:
            token = "Ġ" + token

        bpe_tokens = bpe(token)
        wordpieces.extend(bpe_tokens)

    # Convert to vocab IDs
    token_ids = [vocab.get(piece, vocab.get("unk")) for piece in wordpieces]
    return token_ids


def decode(token_ids):
    """
    Decode token IDs back into text using vocab.
    """
    pieces = [id_to_token.get(token_id) for token_id in token_ids]
    text = "".join(pieces)
    # Replace GPT-2 space token with real space
    return text.replace("Ġ", " ")





text = "the cat sat on the mat 🧪"
encoded = encode(text)
decoded = decode(encoded)


print("Original :", text)
print("Encoded  :", encoded)
print("Decoded  :", decoded)
