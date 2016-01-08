'''
trying out different methods
full of debug text
variable names may not always be descriptive
'''
import language_check
import re

nl_tool = language_check.LanguageTool('en-US')
PUNCTUATION_LIST = [';', '(', ')', '=', '{', '}', '/', '[', ']']
ERROR_RATIO_THRESHOLD = 0.4
PUNCTUATION_RATIO_THRESHOLD = 0.5

def is_source_code(text):
	print "analyzing: "
	print text + "\n"
	word_count = get_word_count(text)
	error_ratio = get_error_ratio(text, word_count)
	punctuation_ratio = get_punctuation_ratio(text, word_count)
	if error_ratio >= ERROR_RATIO_THRESHOLD:
		print "SOURCE CODE!"
	elif punctuation_ratio >= PUNCTUATION_RATIO_THRESHOLD:
		print "SOURCE CODE!"

def get_word_count (text):
	words = text.split()
	word_count = len(words)
	for word in words:
		if re.search('[a-zA-Z]', word) < 0:
			word_count -= 1
	return word_count

def get_error_ratio (text, word_count):
	if word_count <= 0:
		return 0.0
	errors = nl_tool.check(text)
	error_count = len(errors)
	error_ratio = float(error_count) / float(word_count)
	print "error count: " + str(error_count) + " error ratio: " + str(error_ratio)
	return error_ratio

def get_punctuation_ratio (text, word_count):
	if word_count <= 0:
		return 0.0
	punctuation_count = 0
	for punctuation in PUNCTUATION_LIST:
		punctuation_count += text.count(punctuation)
	punctuation_ratio = float(punctuation_count) / float(word_count)
	print "punctuation count: " + str(punctuation_count) + " punctuation ratio: " + str(punctuation_ratio)
	return punctuation_ratio

text_to_test = open('C:\\Users\\V-ann\\Desktop\\testing.txt', 'r')
is_source_code(text_to_test.read())
text_to_test.close

'''
RULES and WEIGHTS
Punctuation = 50
Grammar = 50

Instances of !x = 90
Instances of () = 100
Instances of //x where x is NL = 90
Instances of {, }, =, ;, (, ) = 70
Instances of x.x = 70
Instances of import ... ; = 80
TOTAL: 500
'''