import discord
import asyncio

from tracker import LockoutTracker
from utils import contest_exists

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

		tokens = msg.content.split(" ")
		if len(tokens) < 2 or tokens[0] != self.prefix: return

		cmd = tokens[1]
		channel = msg.channel

		if cmd == "help": await self.cmd_help(channel)
		elif cmd == "start": await self.cmd_start(channel, tokens[2:])
		elif cmd == "stop": await self.cmd_stop(channel)
		else: await channel.send(f"unknown command {cmd}, see `{self.prefix} help` for more info")
	
	async def cmd_help(self, channel):
		res = ""
		res += f"usage: {self.prefix} [command] [arguments]\n"
		res += f"\t{self.prefix} help -- display this help text\n"
		res += f"\t{self.prefix} start [contest_id] [atcoder_handles] -- start a lockout round\n"
		res += f"\t{self.prefix} stop -- stop the lockout round running in a channel\n"
		res += f"\t{self.prefix} pull -- resend the leaderboard message"
		
		await channel.send("```" + res + "```")

	async def cmd_start(self, channel, args):
		try: self.lockouts[channel.id]
		except KeyError: pass
		else:
			await channel.send("that channel already has an ongoing lockout!")
			return
		
		contest = args[0]
		users = args[1:]

		if not contest_exists(contest):
			await channel.send("that contest doesn't exist!")
			return

		lockout_msg = await channel.send("lockout round starting in a couple of seconds...")

		tracker = LockoutTracker(contest, users, lockout_msg)
		self.lockouts[channel.id] = tracker
		await tracker.run(10)

		if tracker.stopped:
			return
		else:
			del self.lockouts[channel.id]
			await channel.send("round is over, see leaderboard above for the results.")
	
	async def cmd_stop(self, channel):
		try:
			self.lockouts[channel.id].running = False
			self.lockouts[channel.id].stopped = True
			await channel.send("round stopped manually.")
			del self.lockouts[channel.id]
		except KeyError:
			await channel.send("there is no lockout round currently running!")
			return

def run_bot():
	token = open("private/token.txt", "r").read()
	client = LockoutBot()
	client.run(token)
	# print("wtf")