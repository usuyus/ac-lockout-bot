import requests
from bs4 import BeautifulSoup
from time import strptime, mktime

def get_submissions(contest, user):
	url = f"https://atcoder.jp/contests/{contest}/submissions?f.User={user}"
	r = requests.get(url)
	html = r.text
	
	soup = BeautifulSoup(html, features = "lxml")
	table_div = soup.find(class_ = "table-responsive")
	
	if not table_div:
		return []
	
	res = []
	
	rows = table_div.table.tbody.children
	for row in rows:
		if row.string == '\n': continue # it inserts these for no reason...

		submit_time = row.contents[1].time.text
		submit_time = strptime(submit_time, "%Y-%m-%d %H:%M:%S%z")
		submit_time = int(mktime(submit_time) - 6 * 3600) # TR <-[6hrs]-> JP

		problem = row.contents[3].a.text.split(" ")[0]
		verdict = row.contents[13].span.text

		# print(f"{problem} -> {verdict}")
		res.append({
			"problem": problem,
			"verdict": verdict,
			"submit_time": submit_time
		})

	return res


async def get_reactions(msg):
	msg = await msg.channel.fetch_message(msg.id)
	st = set()

	for reaction in msg.reactions:
		async for user in reaction.users():
			st.add(user)
	
	return list(st)