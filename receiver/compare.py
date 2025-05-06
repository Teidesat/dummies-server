def highlight_differences(seq1, seq2, width=64, marker='^'):
    lines = []
    for i in range(0, len(seq1), width):
        chunk1 = seq1[i:i+width]
        chunk2 = seq2[i:i+width]
        marker_line = ''.join(marker if a != b else ' ' for a, b in zip(chunk1, chunk2))
        lines.append(f"{i:04d}: {chunk1}\n      {chunk2}\n      {marker_line}")
    return '\n'.join(lines)

def main():
    # Replace these with your actual sequences
    with open("seq1.txt", "r") as f:
        seq1 = f.read().strip()
    with open("seq2.txt", "r") as f:
        seq2 = f.read().strip()

    if len(seq1) != len(seq2):
        print("Warning: Sequences are different lengths.")

    diffs = [i for i, (a, b) in enumerate(zip(seq1, seq2)) if a != b]
    print(f"Total differences: {len(diffs)}")

    diff_text = highlight_differences(seq1, seq2)

    with open("bit_sequence_diff.txt", "w") as out:
        out.write(diff_text)

    print("Diff written to 'bit_sequence_diff.txt'.")

if __name__ == "__main__":
    main()
