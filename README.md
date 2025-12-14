# instagram-message-data
When you request your data from Instagram, your DMs are exported as a set of HTML files. This tool converts those HTML files into a single, plain text transcript.

I built this because working with the raw HTML export is inconvenient. I wanted a way to easily read conversations, copy and paste large sections, search for specific timestamps or words, and run text-based statistics without media getting in the way. Reel descriptions and metadata include a lot of extra text, which can interfere with word counts and phrase analysis, so removing or isolating that content was important.

The result is one compact .txt file that’s much easier to work with than the original export. It’s more readable, easier to search, and far better suited for analysis or use with other tools (including AI systems, which generally don’t handle HTML well).

In addition to the converter, there’s a separate analysis script that takes the generated text file and produces messaging statistics such as message counts, word usage, and activity patterns by day, week, and month. Spotify wrapped except for your DMs. 

Overall, this just turns Instagram’s DM export into a format that’s actually usable.
