
import ollama
import hashlib
import scipy.stats as stats
import numpy as np
import nltk

nltk.download('punkt')

def hash_string(s):
    """
    Hash a string using SHA-256 and return the hexadecimal digest.
    """
    return hashlib.sha256(s.encode()).hexdigest()
def hash_to_randint(hash_str):
    """
    Convert a hash string to a random integer between 0 and 1.
    """
    return 1 * (int(hash_str, 16) % 100 / 100.0 >= 0.5)  # Convert hash to a float between 0 and 1


def sample_from_probas(probas, num_samples=1):
    """
    Sample tokens from the given probabilities.
    """
    tokens = list(probas)
    indices = np.arange(len(tokens))
    probabilities = list(probas.values())  # Get the probabilities
    probabilities = [p / sum(probabilities) for p in probabilities]  # Normalize probabilities
    sampled_indices = np.random.choice(indices, size=num_samples, p=probabilities)
    sampled_tokens = [tokens[i] for i in sampled_indices]
    return sampled_tokens
def dueling(sampled_tokens, last_four_tokens):

    """
    Function to perform dueling on sampled tokens.
    """
    N_SAMPLES = len(sampled_tokens)
    sampled_tokens = [(token, '') for token in sampled_tokens]  # Add a placeholder for the second token

    for steps in range(int(np.log(N_SAMPLES) / np.log(2))):
        new_sampled_tokens = []
        for i in range(0, len(sampled_tokens), 2):
            if i + 1 < len(sampled_tokens):
                token1, token2 = sampled_tokens[i][0], sampled_tokens[i + 1][0]
               
                hash1 = hash_string(f'seed:{steps} '+''.join(last_four_tokens) + str(token1).strip())
                hash2 = hash_string(f'seed:{steps} '+''.join(last_four_tokens) + str(token2).strip())
                hash_values = [hash_to_randint(h) for h in [hash1, hash2]]
                winner = token1 if hash_values[0] > hash_values[1] else token2
                new_sampled_tokens.append((winner, sampled_tokens[i + 1][1] + str(hash_values[1]) if winner == token2 else sampled_tokens[i][1] + str(hash_values[0])))
            else:
                hash1 = hash_string(f'seed:{steps} '+''.join(last_four_tokens) + str(sampled_tokens[i]).strip())
                hash_value = hash_to_randint(hash1)
                new_sampled_tokens.append((sampled_tokens[i][0], str(hash_value) + sampled_tokens[i][1]))
        sampled_tokens = new_sampled_tokens
    # print("Dueling results:", sampled_tokens, "Last four tokens:", last_four_tokens)
    return sampled_tokens[0]
def token_hscore(token, last_four_tokens, n_duels=3):
    """
    Function to compute the h-score of a token based on dueling.
    """
    value = 0
    values = []
    for i in range(n_duels):
       
        hash_value = hash_string(f'seed:{i} '+''.join(last_four_tokens) + str(token.strip()))
        if hash_to_randint(hash_value) > 0.5:
            value += 1 / n_duels
            values.append(1)
        else:
            values.append(0)
    # print(f"Token: {token}, Last Four Tokens: {last_four_tokens}, H-Score: {value}, Values: {values}")
    return value



def part_emoji_token_check(token):
    """
    Check if the token contains any emoji characters.
    """
    emoji_ranges = [
        (0x1F600, 0x1F64F),  # Emoticons
        (0x1F300, 0x1F5FF),  # Miscellaneous Symbols and Pictographs
        (0x1F680, 0x1F6FF),  # Transport and Map Symbols
        (0x2600, 0x26FF),    # Miscellaneous Symbols
        (0x2700, 0x27BF),    # Dingbats
        (0xFE00, 0xFE0F),    # Variation Selectors
        (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
        (0x1FA70, 0x1FAFF),  # Symbols and Pictographs Extended-A
    ]
    
    for char in token:
        if any(start <= ord(char) <= end for start, end in emoji_ranges):
            return True
    return False
def wattermarking_text(probas, last_four_tokens, n_duels=8):
    """
    Function to perform watermarking.
    """
    # Implement your watermarking logic here
    
    sampled_tokens = sample_from_probas(probas, num_samples=2**n_duels)
    # print("Sampled Tokens:", probas)
    final_sampled_tokens, scores = dueling(sampled_tokens, last_four_tokens)
    return final_sampled_tokens

def logprob_token(entry):
    return entry.token if hasattr(entry, "token") else entry[0]

def logprob_value(entry):
    return entry.logprob if hasattr(entry, "logprob") else entry[1]

def word_probas(logprobs):
    return {
        logprob_token(entry): np.exp(logprob_value(entry))
        for entry in logprobs if np.exp(logprob_value(entry)) > 0.01
    }

def split_word_boundaries(text):
   
    return text[0].isspace(), text
    # part = ""
    # for character in text:
    #     if character.isspace():
    #         if part:
    #             yield False, part
    #             part = ""
    #         yield True, " "
    #     else:
    #         part += character
    # if part:
    #     yield False, part

def ttest_hscore(scores):
    """
    Perform a t-test on the h-scores to determine if they are significantly different from 0.5.
    """
    t_statistic, p_value = stats.ttest_1samp(scores, 0.5)
    return t_statistic, p_value
def is_special_character(char):
    """
    Check if a character is a special character like #, @, $, %, &, *, backlashes, etc.
    """
    special_characters = set("#@$%&*\\()[]{}<>/|^~`_+-=;:'’\\\".,?!<>")
    result = any(
        character in special_characters or part_emoji_token_check(character)
        for character in char
    )
   
    return result


def remove_goto_line(text):
    word_with_newline = text
    word = text.replace("\n", "")
    word = " " + word if word_with_newline != word and word != "" else word
    return word if word  != "" else word


def new_generate_text(model, messages, watermarking=False, n_duels=8, placeholder=None, seed=42):
    """
    Stream generated text and print one buffered word at a time.
    """
    conversation = list(messages)
    words_and_others = []
    average_1_bias_score = []
    last_four_tokens = ["", "", "", ""]
    response_text = ""
    water_buffer = ""
    content = None
    prev_logprobs = None
    while True:
        restart_stream = False
        stream = ollama.chat(
            model=model,
            messages=conversation,
            stream=True,
            think=False,
            options={"temperature": 0.0},
            logprobs=True,
            top_logprobs=5
        )
        started = False
        ongoing = False
        ended = False
        token = ""
        for chunk in stream:
            content = chunk.message.content if content is None else chunk.message.content
            print(f"Chunk received: {content}")
            if not content:
                continue
            if content[0].isspace() and not any(is_special_character(c) for c in content) and not "\n" in content:
                if started:
                    ended = True
                if ended and prev_logprobs and not ongoing and max(prev_logprobs.values(), default=1.0) < (0.9 * watermarking):
                    token = wattermarking_text(prev_logprobs, last_four_tokens, n_duels=8)
                    ## if previous token has \n\n put it back in the token
                    if "\n\n" in prev_token:
                        token = "\n\n" + token
                    print(f"Watermarking applied. Token: '{token}'")
                    restart_stream = True
                elif not ongoing and not started:
                    token = content
                    started = True
                    print(f"Starting new token: '{token}'")
            else:
                started = True
                ongoing = True
                token += content
                ongoing = True
                print(f"Buffering token: '{token}'")
            if content[0].isspace() and token and ended:
                # buffer_to_use = "".join(buffer)
                print(f"Buffer to use for watermarking check: '{token}'")
                duel_score = token_hscore(remove_goto_line(token), last_four_tokens, n_duels=n_duels)
                average_1_bias_score.append(duel_score)
                last_four_tokens.append(remove_goto_line(token))
                last_four_tokens = last_four_tokens[-4:]
                response_text += token
                ended = False
                ongoing = False
                if placeholder:
                    placeholder.markdown(response_text + "▌")
                else:
                    print(token, end="", flush=True)
                words_and_others.append((remove_goto_line(token), duel_score))
                if restart_stream:
                    started = False
                    break
                token = content
                started = True
            logprobs = word_probas(chunk.logprobs[0]["top_logprobs"]) if chunk.logprobs else {}
            prev_logprobs = logprobs if chunk.logprobs else None
            prev_token = token
        if restart_stream:

            conversation = [*messages, {"role": "assistant", "content": response_text}]
            stream.close()
            # print(conversation)
            # print("Restarting stream due to watermarking...")
            continue
        # print(f"Final buffer: {buffer}, Last four tokens: {last_four_tokens}, Water buffer: '{water_buffer}'")
        # if buffer != [""]:
        #     buffer = "".join(buffer)
        #     duel_score = token_hscore(remove_goto_line(buffer), last_four_tokens, n_duels=n_duels)
        #     average_1_bias_score.append(duel_score)
        #     words_and_others.append((buffer, duel_score))
        #     response_text += buffer
            # if placeholder:
            #     placeholder.markdown(buffer)
            # else:
            #     print(buffer, end="", flush=True)
        break
    # print("Tokens:", words_and_others)
   
    t_statistic, p_value = ttest_hscore(average_1_bias_score)
    if placeholder:
        placeholder.markdown(response_text)
    else:
        print('length of average_1_bias_score:', len(average_1_bias_score))
        print("Average 1 Bias Score:", sum(average_1_bias_score) / len(average_1_bias_score) if average_1_bias_score else 0)
        print(f"T-statistic: {t_statistic}, P-value: {p_value}")

    return response_text, average_1_bias_score, t_statistic, p_value
def apply_token(token, list_special_characters):
    ## add space before if token is not a special character
    if not is_special_character(token):
        token = " " + token
    return token
def split_tokens(text, model=None):
    """
    Split the text into tokens using the Qwen tokenizer.
    """
    if model is None:
        list_special_characters = set("#@$%&*\\()[]{}<>/|^~`_+-=;:'’\".,?!<>")
        
        tokens = nltk.word_tokenize(text)
        
        tokens = [apply_token(token, list_special_characters) for token in tokens]
        tokens[0] = tokens[0].lstrip()  # Remove leading space from the first token
        return tokens
        return tokens_to_word
def check_watermarking(model, text):
    """
    Test the watermarking by generating text and checking the h-scores.
    """
   
    tokens =  split_tokens(text, model=None)
    token_values = []
    total_h_score = 0
    average_1_bias_score = []
    last_four_tokens = ["", "", "", ""]
    for token in tokens:
        
        if len(last_four_tokens) > 4:
            last_four_tokens.pop(0)

        h_score = token_hscore(token, last_four_tokens , n_duels=8)
        last_four_tokens.append(token)
        token_values.append((token, h_score))
        total_h_score += h_score
        average_1_bias_score.append(h_score)
    print(f"Average H-Score: {total_h_score/len(tokens)},average_1_bias_score: {len(average_1_bias_score)}")
    t_statistic, p_value = ttest_hscore(average_1_bias_score)
    print(f"T-statistic: {t_statistic}, P-value: {p_value}")

    ## nice prints to tell whether the text is watermarked or not
    score = total_h_score/len(tokens)
    is_significant = p_value < 0.05
    
    print("\n" + "="*60)
    if score > 0.5 and is_significant:
        print("✓ WATERMARK DETECTED")
        print(f"  H-Score: {score*100:.1f}%")
        print(f"  Statistical Significance: p={p_value} (p < 0.05 ✓)")
        print(f"  T-Statistic: {t_statistic:.4f}")
    elif score > 0.5:
        print("⚠ POSSIBLE WATERMARK")
        print(f"  H-Score: {score*100:.1f}%")
        print(f"  Statistical Significance: p={p_value:.4f} (not significant)")
        print(f"  T-Statistic: {t_statistic:.4f}")
    else:
        print("✗ NO WATERMARK DETECTED")
        print(f"  H-Score: {score*100:.1f}%")
        print(f"  Statistical Significance: p={p_value:.4f}")
        print(f"  T-Statistic: {t_statistic:.4f}")
    print("="*60)
