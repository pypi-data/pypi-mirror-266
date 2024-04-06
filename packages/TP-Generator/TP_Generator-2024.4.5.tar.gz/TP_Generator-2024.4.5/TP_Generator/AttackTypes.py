def Sniper(InsertionPoints, Payloads, testcases=list(), separator="||"):
	if type(separator) != str: separator = "||"

	'''
	- The data type of "InsertionPoints" must be a "list"
	- The data type of "Payloads" must be a "list"
	- The "Payloads" has length "1"
	- The data type of the first element of Payloads must be a "dict", containing only one key and the value of this key must be a "list"
	'''
	if type(InsertionPoints) != list \
			or type(Payloads) != list \
			or len(Payloads) != 1 \
			or type(Payloads[0]) != dict \
			or len(Payloads[0].keys()) != 1 \
			or type(list(Payloads[0].values())[0]) != list:
		exit("[-] Invalid InsertionPoints or Payloads")

	try:
		testcases = list()
		for i in range(len(InsertionPoints)):
			if type(InsertionPoints[i]) != str:
				exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

			if InsertionPoints[i].split(separator,1)[0] not in ["RequestMethod", "PathParams", "QueryParams", "URIFragment", "HTTPVersion", "HTTPHeaders", "HTTPCookies", "RequestBody"]:
				exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

			if InsertionPoints[i].split(separator,1)[0] in ["RequestMethod", "URIFragment", "HTTPVersion"] and len(InsertionPoints[i].split(separator,1)) == 2:
				exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

			if InsertionPoints[i].split(separator,1)[0] in ["PathParams", "QueryParams", "HTTPHeaders", "HTTPCookies", "RequestBody"] and (len(InsertionPoints[i].split(separator,1)) == 1 or len(InsertionPoints[i].split(separator,1)[1]) == 0):
				exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

			for alias_payload in Payloads[0]:
				for j in range(len(Payloads[0][alias_payload])):
					if InsertionPoints[i].split(separator,1)[0] in ["PathParams", "QueryParams", "HTTPHeaders", "HTTPCookies", "RequestBody"]:
						testcases.append({
							"[\x1b[1;31mSniper Attack\x1b[1;0m]\n - \x1b[1;33m" + alias_payload+"_"+str(j+1) + "\x1b[1;0m => \x1b[1;34m" + InsertionPoints[i] + "\x1b[1;0m": {
								InsertionPoints[i].split(separator,1)[0]: {
									InsertionPoints[i].split(separator,1)[1]: Payloads[0][alias_payload][j]
								}
							}
						})
					else:
						testcases.append({
							"[\x1b[1;31mSniper Attack\x1b[1;0m]\n - \x1b[1;33m" + alias_payload+"_"+str(j+1) + "\x1b[1;0m => \x1b[1;34m" + InsertionPoints[i] + "\x1b[1;0m": {
								InsertionPoints[i].split(separator,1)[0]: str(Payloads[0][alias_payload][j])
							}
						})
		return testcases
	except Exception as e:
		exit("[-] ExceptionError:", e)



def Batteringram(InsertionPoints, Payloads, testcases=list(), separator="||"):
	if type(separator) != str: separator = "||"

	'''
	- The data type of "InsertionPoints" must be a "list"
	- The data type of "Payloads" must be a "list"
	- The "Payloads" has length "1"
	- The data type of the first element of Payloads must be a "dict", containing only one key and the value of this key must be a "list"
	'''
	if type(InsertionPoints) != list \
			or type(Payloads) != list \
			or len(Payloads) != 1 \
			or type(Payloads[0]) != dict \
			or len(Payloads[0].keys()) != 1 \
			or type(list(Payloads[0].values())[0]) != list:
		exit("[-] Invalid InsertionPoints or Payloads")

	try:
		testcases = list()
		for alias_payload in Payloads[0]:
			for j in range(len(Payloads[0][alias_payload])):
				tmp = dict()
				tmp_alias = list()
				for i in range(len(InsertionPoints)):
					if type(InsertionPoints[i]) != str:
						exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

					if InsertionPoints[i].split(separator,1)[0] not in ["RequestMethod", "PathParams", "QueryParams", "URIFragment", "HTTPVersion", "HTTPHeaders", "HTTPCookies", "RequestBody"]:
						exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

					if InsertionPoints[i].split(separator,1)[0] in ["RequestMethod", "URIFragment", "HTTPVersion"] and len(InsertionPoints[i].split(separator,1)) == 2:
						exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

					if InsertionPoints[i].split(separator,1)[0] in ["PathParams", "QueryParams", "HTTPHeaders", "HTTPCookies", "RequestBody"] and (len(InsertionPoints[i].split(separator,1)) == 1 or len(InsertionPoints[i].split(separator,1)[1]) == 0):
						exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

					if InsertionPoints[i].split(separator,1)[0] not in tmp:
						if InsertionPoints[i].split(separator,1)[0] in ["PathParams", "QueryParams", "HTTPHeaders", "HTTPCookies", "RequestBody"]:
							tmp[InsertionPoints[i].split(separator,1)[0]] = dict()
						else:
							tmp[InsertionPoints[i].split(separator,1)[0]] = str()

					if InsertionPoints[i].split(separator,1)[0] in ["PathParams", "QueryParams", "HTTPHeaders", "HTTPCookies", "RequestBody"]:
						tmp[InsertionPoints[i].split(separator,1)[0]][InsertionPoints[i].split(separator,1)[1]] = Payloads[0][alias_payload][j]
					else:
						tmp[InsertionPoints[i].split(separator,1)[0]] = str(Payloads[0][alias_payload][j])
					tmp_alias.append("\x1b[1;33m"+alias_payload+"_"+str(j+1) + "\x1b[1;0m => \x1b[1;34m" + InsertionPoints[i]+"\x1b[1;0m")
				testcases.append({"[\x1b[1;31mBatteringram Attack\x1b[1;0m]\n - " + "\n - ".join(tmp_alias): tmp})
		return testcases
	except Exception as e:
		exit("[-] ExceptionError:", e)



def Pitchfork(InsertionPoints, Payloads, testcases=list(), separator="||"):
	if type(separator) != str: separator = "||"

	'''
	- The data type of "InsertionPoints" must be a "list"
	- The data type of "Payloads" must be a "list"
	- The length of "Payloads" is equal to the length of "InsertionPoints"
	- The data type of each Payloads element must be "dict", containing only one key, and the value of this key must be a "list" of equal length
	'''
	if type(InsertionPoints) != list \
			or type(Payloads) != list \
			or len(InsertionPoints) != len(Payloads) \
			or len([1 for i in Payloads if type(i)==dict]) != len(Payloads) \
			or len([1 for i in Payloads if len(i.keys())==1]) != len(Payloads) \
			or len([1 for i in Payloads if type(list(i.values())[0])==list]) != len(Payloads) \
			or len(set([len(list(i.values())[0]) for i in Payloads])) != 1:
		exit("[-] Invalid InsertionPoints or Payloads")

	try:
		testcases = list()
		for j in range(len(list(Payloads[0].values())[0])):
			tmp = dict()
			tmp_alias = list()
			for i in range(len(InsertionPoints)):
				alias_payload = list(Payloads[i].keys())[0]

				if type(InsertionPoints[i]) != str:
					exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

				if InsertionPoints[i].split(separator,1)[0] not in ["RequestMethod", "PathParams", "QueryParams", "URIFragment", "HTTPVersion", "HTTPHeaders", "HTTPCookies", "RequestBody"]:
					exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

				if InsertionPoints[i].split(separator,1)[0] in ["RequestMethod", "URIFragment", "HTTPVersion"] and len(InsertionPoints[i].split(separator,1)) == 2:
					exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

				if InsertionPoints[i].split(separator,1)[0] in ["PathParams", "QueryParams", "HTTPHeaders", "HTTPCookies", "RequestBody"] and (len(InsertionPoints[i].split(separator,1)) == 1 or len(InsertionPoints[i].split(separator,1)[1]) == 0):
					exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

				if InsertionPoints[i].split(separator,1)[0] not in tmp:
					if InsertionPoints[i].split(separator,1)[0] in ["PathParams", "QueryParams", "HTTPHeaders", "HTTPCookies", "RequestBody"]:
						tmp[InsertionPoints[i].split(separator,1)[0]] = dict()
					else:
						tmp[InsertionPoints[i].split(separator,1)[0]] = str()

				if InsertionPoints[i].split(separator,1)[0] in ["PathParams", "QueryParams", "HTTPHeaders", "HTTPCookies", "RequestBody"]:
					tmp[InsertionPoints[i].split(separator,1)[0]][InsertionPoints[i].split(separator,1)[1]] = Payloads[i][alias_payload][j]
				else:
					tmp[InsertionPoints[i].split(separator,1)[0]] = str(Payloads[i][alias_payload][j])
				tmp_alias.append("\x1b[1;33m"+alias_payload+"_"+str(j+1) + "\x1b[1;0m => \x1b[1;34m" + InsertionPoints[i]+"\x1b[1;0m")
			testcases.append({"[\x1b[1;31mPitchfork Attack\x1b[1;0m]\n - " + "\n - ".join(tmp_alias): tmp})
		return testcases
	except Exception as e:
		exit("[-] ExceptionError:", e)



def Clusterbomb(InsertionPoints, Payloads, testcases=list(), separator="||"):
	def generate_combinations(Payloads):
		if len(Payloads) == 1:
			return [[{list(Payloads[0].keys())[0]+"_"+str(j+1):list(Payloads[0].values())[0][j]}] for j in range(len(list(Payloads[0].values())[0]))]
		else:
			sub_combinations = generate_combinations(Payloads[1:])
			combinations = []
			for j in range(len(list(Payloads[0].values())[0])):
				for sub_combination in sub_combinations:
					combinations.append([{list(Payloads[0].keys())[0]+"_"+str(j+1):list(Payloads[0].values())[0][j]}] + sub_combination)
			return combinations

	if type(separator) != str: separator = "||"

	'''
	- The data type of "InsertionPoints" must be a "list"
	- The data type of "Payloads" must be a "list"
	- The length of "Payloads" is equal to the length of "InsertionPoints"
	- The data type of each Payloads element must be "dict", containing only one key, and the value of this key must be a "list"
	'''
	if type(InsertionPoints) != list \
			or type(Payloads) != list \
			or len(InsertionPoints) != len(Payloads) \
			or len([1 for i in Payloads if type(i)==dict]) != len(Payloads) \
			or len([1 for i in Payloads if len(i.keys())==1]) != len(Payloads) \
			or len([1 for i in Payloads if type(list(i.values())[0])==list]) != len(Payloads):
		exit("[-] Invalid InsertionPoints or Payloads")

	try:
		testcases = list()
		for tc in generate_combinations(Payloads):
			tmp = dict()
			tmp_alias = list()
			for i in range(len(InsertionPoints)):
				alias_payload = list(tc[i].keys())[0]

				if type(InsertionPoints[i]) != str:
					exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

				if InsertionPoints[i].split(separator,1)[0] not in ["RequestMethod", "PathParams", "QueryParams", "URIFragment", "HTTPVersion", "HTTPHeaders", "HTTPCookies", "RequestBody"]:
					exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

				if InsertionPoints[i].split(separator,1)[0] in ["RequestMethod", "URIFragment", "HTTPVersion"] and len(InsertionPoints[i].split(separator,1)) == 2:
					exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

				if InsertionPoints[i].split(separator,1)[0] in ["PathParams", "QueryParams", "HTTPHeaders", "HTTPCookies", "RequestBody"] and (len(InsertionPoints[i].split(separator,1)) == 1 or len(InsertionPoints[i].split(separator,1)[1]) == 0):
					exit("[-] Invalid InsertionPoints: {}".format(InsertionPoints[i]))

				if InsertionPoints[i].split(separator,1)[0] not in tmp:
					if InsertionPoints[i].split(separator,1)[0] in ["PathParams", "QueryParams", "HTTPHeaders", "HTTPCookies", "RequestBody"]:
						tmp[InsertionPoints[i].split(separator,1)[0]] = dict()
					else:
						tmp[InsertionPoints[i].split(separator,1)[0]] = str()

				if InsertionPoints[i].split(separator,1)[0] in ["PathParams", "QueryParams", "HTTPHeaders", "HTTPCookies", "RequestBody"]:
					tmp[InsertionPoints[i].split(separator,1)[0]][InsertionPoints[i].split(separator,1)[1]] = tc[i][alias_payload]
				else:
					tmp[InsertionPoints[i].split(separator,1)[0]] = str(tc[i][alias_payload])
				tmp_alias.append("\x1b[1;33m"+alias_payload + "\x1b[1;0m => \x1b[1;34m" + InsertionPoints[i]+"\x1b[1;0m")
			testcases.append({"[\x1b[1;31mClusterbomb Attack\x1b[1;0m]\n - " + "\n - ".join(tmp_alias): tmp})
		return testcases
	except Exception as e:
		exit("[-] ExceptionError:", e)