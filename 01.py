def count_words(text):
    # Step 1: Clean the data. 
    # We use .lower() so "How" and "how" are counted as the same word.
    # Then we .split() it into a list of words.
    words = text.lower().split()

    # Step 2: Create the empty dictionary (Your row of empty bins)
    word_counts = {}

    # Step 3: Loop through every single word in the list
    for word in words:
        # Check if the bin already exists
        if word in word_counts:
            # If yes, add 1 to the current count
            word_counts[word] += 1
        else:
            # If no, create the bin and set the count to 1
            word_counts[word] = 1

    # Step 4: Give the final dictionary back
    return word_counts


# --- Testing the Code ---
user_input = input("Paste : ")
final_result = count_words(user_input)

# We print OUTSIDE the loop, so it only prints the final answer once.
print(final_result)

