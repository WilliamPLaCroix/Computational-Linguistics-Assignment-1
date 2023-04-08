README
## Directory Structure
.
├── assignment_1.py
├── README.txt
└── Report.pdf


## Versions
Python: 3.8.8
NLTK: 3.6.5
Matplotlib: v3.3.4


## Runtime
Problem 1 - Zipf's Law:
	Longest observed runtime was 5.7s for the Bulgarian translation of SETIMES

Problem 2 - Dissociated Press:
	Jungle Book:
		Corpus loaded in 0.0s
		4-gram genereated in 0.3s
	Bible:
		Corpus loaded in 0.3s
		4-gram genereated in 2.6s
	Bulgarian SETIMES:
		Corpus loaded in 2.7s
		4-gram genereated in 16.8s
	Turkish SETIMES:
		Corpus loaded in 2.5s
		4-gram genereated in 15.9s

	100-word text samples generated in 0.0s in all cases,
		but feel free to generate much longer samples. I tried one output of 100k words, and realised I need to work on paragraph styling!

Problem 3 - Statistical Dependence:
	# This section runs significantly slower. Problem 2 may have been ~O(n) time, Problem 3 looks like O(n^2) at least...

	### Probably don't run problem 3 over the Bulgarian or Turkish corpora, unless you know something I don't... ###

	jungle_book:
		Corpus loaded in 12.9s
		PMIs calculated in 0.0s
	Bible:
		Corpus loaded in 354.6s
		PMIs calculated in 0.5s
	Bulgarian:
		Runtime > 15min, I gave up.
	Turkish:
		Runtime > 15min, I gave up.
		

## Additional Features
I did all 3 problems, and provided a terminal-based UI for navigating the problem generation.
I hope this is an intuitive and not all-together unpleasant way to test my program!
The only extensions of the individual problems I did was variations ignoring punctuation (problem 1 and 3),
	some mediocre conditional formatting for text output ( format_word() ), and options for text length (problem 2)

Thanks for taking the time to look through my code and documentation!
	~ William