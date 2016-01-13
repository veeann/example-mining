'''
This program reads a file, checks the contents per line, and outputs them if they are source code.

WARNING:
This is an experimental version where different methods are being tried.
The current method it is implementing is noted above.
It is full of debug text; variable names may not always be descriptive
'''
import language_check
import re

nl_tool = language_check.LanguageTool('en-US')
PUNCTUATION_LIST = [';', '(', ')', '=', '{', '}', '[', ']']

ERROR_WEIGHT = 0.4
CODE_WEIGHT = 1.0
SCORE_TOTAL = ERROR_WEIGHT + CODE_WEIGHT

PUNCTUATION_WEIGHT = 0.7
PARENTHESIS_WEIGHT = 1.0
NEGATION_WEIGHT = 0.8
COMMENT_WEIGHT = 0.7
METHOD_WEIGHT = 0.5
IMPORT_WEIGHT = 0.8
CODE_TOTAL = PUNCTUATION_WEIGHT + PARENTHESIS_WEIGHT + NEGATION_WEIGHT + COMMENT_WEIGHT + METHOD_WEIGHT + IMPORT_WEIGHT

SCORE_THRESHOLD = 0.1

def find_source_code(text):
	lines = text.replace('\r', '\n').split("\n")
	for line in lines:
		if is_source_code(line):
			encoding = UnicodeDammit(line).original_encoding
			if not encoding == None:
				print line.encode(encoding)
			else:
				print line
		else:
			print ""

def is_source_code(text):
	text = clean(text)
	word_count = get_word_count(text)
	error_ratio = get_error_ratio(text, word_count) * ERROR_WEIGHT
	code_ratio = get_code_ratio(text, word_count) * CODE_WEIGHT
	score = error_ratio + code_ratio
	score = score / SCORE_TOTAL
	#print "DEBUG: score: " + str(score)
	if score >= SCORE_THRESHOLD:
		return True
	return False

def clean (text):
	lines = text.replace('\r','\n').split("\n")
	new_text = ""
	for line in lines:
		if not line.strip()=="":
			new_text += line + "\n"
	return new_text

def get_word_count (text):
	words = text.split()
	word_count = len(words)
	'''
	for word in words:
		if re.search('[a-zA-Z]', word) < 0:
			word_count -= 1
	'''
	return word_count

def get_error_ratio (text, word_count):
	if word_count <= 0:
		return 0.0
	errors = nl_tool.check(text)
	error_count = len(errors)
	#print "DEBUG: error count: " + str(error_count)
	error_ratio = float(error_count) / float(word_count)
	#print "DEBUG: error ratio: " + str(error_ratio)
	return error_ratio

def get_code_ratio (text, word_count):
	if word_count <= 0:
		return 0.0
	punctuation_ratio = get_punctuation_occurrences(text)  / float(word_count) * PUNCTUATION_WEIGHT
	parenthesis_ratio = get_parentheses_occurrences(text)  / float(word_count) * PARENTHESIS_WEIGHT
	negation_ratio = get_negation_occurrences(text)  / float(word_count) * NEGATION_WEIGHT
	comment_ratio = get_comment_occurrences(text)  / float(word_count) * COMMENT_WEIGHT
	method_ratio = get_method_occurrences(text)  / float(word_count) * METHOD_WEIGHT
	import_ratio = get_import_occurrences(text)  / float(word_count) * IMPORT_WEIGHT
	code_ratio = punctuation_ratio + parenthesis_ratio + negation_ratio + comment_ratio + method_ratio + import_ratio
	code_ratio = code_ratio / CODE_TOTAL
	#print "DEBUG: code ratio: " + str(code_ratio)
	return code_ratio

def get_punctuation_occurrences (text):
	punctuation_count = 0
	for punctuation in PUNCTUATION_LIST:
		punctuation_count += text.count(punctuation)
	#print "DEBUG: punctuation: " + str(punctuation_count)
	return punctuation_count

def get_parentheses_occurrences (text):
	parenthesis_count = text.count("()")
	#print "DEBUG: parenthesis: " + str(parenthesis_count)
	return parenthesis_count

def get_negation_occurrences (text):
	negation_count = len(re.findall("![a-zA-Z=]+", text))
	#print "DEBUG: negation: " + str(negation_count)
	return negation_count

def get_comment_occurrences (text):
	possible_comments = re.findall("//[ \t\r\f\v\S]+\n", text)
	comment_count = 0
	for result in possible_comments:
		if not is_source_code(result[2:].strip()):
			comment_count += 1
	#print "DEBUG: comments: " + str(comment_count)
	return comment_count

def get_method_occurrences (text):
	method_count = len(re.findall("[a-zA-Z]+[a-zA-Z0-9_()\"]+\.[a-zA-Z]+", text))
	#print "DEBUG: methods: " + str(method_count)
	return method_count

def get_import_occurrences (text):
	import_count = len(re.findall("import [a-zA-Z0-9. ]+;", text))
	#print "DEBUG: imports: " + str(import_count)
	return import_count

text_to_test = open('C:\\Users\\V-ann\\Desktop\\testing.txt', 'r')
find_source_code(text_to_test.read())
text_to_test.close