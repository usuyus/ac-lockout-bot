import discord
import asyncio

from tracker import LockoutTracker

class LockoutBot(discord.Client):
	prefix = "ac!"
	lockouts = {}
	
	async def on_ready(self):
		print(f"username: {str(self.user)}")
		print(self.user.name)

	async def on_message(self, msg):
		# to avoid infinite loops
		if msg.author == self.user:return

		# print(f"[{msg.author}] {msg.content}")

		cmd = msg.content.split(" ")
		if len(cmd) < 2 or cmd[0] != self.prefix: return

		if cmd[1] == "help":
			await msg.channel.send("usage: ac! [contest_id] [handles]")
			return
		
		print(f"detected command -- contest id: {cmd[1]}")

		try: self.lockouts[msg.channel.id]
		except KeyError: pass
		else:
			await msg.channel.send("that channel already has an ongoing lockout!")
			return
		
		contest = cmd[1]
		users = cmd[2:]

		lockout_msg = await msg.channel.send("lockout round starting in a couple of seconds...")

		self.lockouts[msg.channel.id] = LockoutTracker(contest, users, lockout_msg)
		await self.lockouts[msg.channel.id].run(10 * 60)
		del self.lockouts[msg.channel.id]
		await msg.channel.send("round is over, see leaderboard above for the results")


def run_bot():
	token = open("private/token.txt", "r").read()
	client = LockoutBot()
	client.run(token)
	# print("wtf")