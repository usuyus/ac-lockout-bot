from utils import get_submissions, get_reactions
import asyncio
from time import time

class LockoutTracker:
	
	num_problems = 6
	base_scores = [100, 300, 500, 700, 900, 1100]
	
	def __init__(self, contest, handles, msg):
		self.handles = handles
		self.contest = contest
		self.msg = msg

		self.num_solved = [0] * self.num_problems
		self.scores = {handle: 0 for handle in self.handles}
		self.solved = {handle: [False] * 6 for handle in self.handles}
	
	def check_no_submits(self):
		for handle in self.handles:
			submits = get_submissions(self.contest, handle)
			if len(submits) > 0: return False
		return True
	
	async def run(self, duration):
		self.running = True
		self.start_time = int(time())
		self.duration = duration

		# await asyncio.sleep(5)

		if not self.check_no_submits():
			await self.msg.channel.send("warning: there's a user who has already submitted something to this contest", delete_after = 10)
		
		print("starting round...")
		await self.msg.edit(content = "round started, good luck!")
		await asyncio.gather(
			self.timer_coro(duration),
			self.update_coro(),
		)
	
	async def timer_coro(self, duration):
		await asyncio.sleep(duration)
		self.running = False
		print("done")
	
	async def update_coro(self, delay = 0):
		while self.running:
			await self.update()
			await self.update_msg()
			await asyncio.sleep(delay)
		await self.update()
		await self.update_msg()
	
	async def update(self):
		# print("enter update")
		for handle in self.handles:
			submits = get_submissions(self.contest, handle)
			if len(submits) == 0 or submits[0]["submit_time"] < self.start_time: continue
	
			last = submits[0]
			letter = ord(last["problem"]) - ord('A')

			if last["verdict"] == "AC" and not self.solved[handle][letter]:
				cur_pts = self.base_scores[letter] // (self.num_solved[letter] + 1)
				self.solved[handle][letter] = True
				self.scores[handle] += cur_pts
				self.num_solved[letter] += 1

				upd_users = await get_reactions(self.msg)
				upd_msg = f"{handle} solved problem {chr(letter + ord('A'))} for {cur_pts}! "
				for user in upd_users: upd_msg += user.mention
				await self.msg.channel.send(upd_msg)
		# print("exit update")
	
	async def update_msg(self):
		# print("enter msg")
		res = ""

		res += "[L E A D E R B O A R D]\n"
		res += "                       \n"
		res += "   Handle      Score   \n"
		res += "   -----------------   \n"

		self.handles = sorted(
			self.handles,
			key = lambda handle: self.scores[handle],
			reverse = True
		)
	
		for handle, i in zip(self.handles, range(len(self.handles))):
			res += f"{i+1}) {handle:<13}{self.scores[handle]:>4}   \n"
		
		res += "                       \n"
		res += "///////////////////////\n"
		res += "                       \n"
		res += "   [P R O B L E M S]   \n"
		res += "                       \n"
		res += "   Points   # Solved   \n"
		res += "   -----------------   \n"

		for i in range(self.num_problems):
			res += f"{chr(ord('A') + i)}) {self.base_scores[i] // (self.num_solved[i] + 1):<13}{self.num_solved[i]:>4}   \n"
		
		res += "                       \n"
	
		cur_time = int(time())
		diff = max(0, self.duration - (cur_time - self.start_time))
		res += f"Time left: {diff//60:02}:{diff%60:02}"

		res = "```\n" + res + "```"
		await self.msg.edit(content = res)
		# print("exit msg")


		