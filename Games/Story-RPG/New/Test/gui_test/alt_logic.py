#!/usr/bin/python3
import json

class Dialogue:
	"""
		Keys: names, text, nodes, links, coords, tags
	"""
	def __init__(self, dialoguedict):
		self.names = []
		self.nodes = self.assemble_nodes(dialoguedict)
		self.starts = self.gather_nodes("greeting")
		self.comment_starts = self.gather_nodes("start")
		self.cards = self.find_cards()

##### Init Methods.

	def assemble_nodes(self, _dict):
		node_dict = {}
		for name in _dict["names"]:
			self.names.append(name)
			for node in _dict["nodes"][name]:
				tags = self.fix_tags(_dict["tags"][node])
				n = Node(node, name.lower(), _dict["text"][node], _dict["links"][node], tags, _dict["coords"][node], self.set_type(tags))
				node_dict[node] = n
		return node_dict

	def set_type(self, tags):
		if tags[0] in ("comment", "comment_reply", "start"):
			return "comment"
		elif tags[0] in ("greeting", "question", "answer"):
			return "dialogue"
		elif "card" in tags[0]:
			return "card"
		else:
			return "unknown"

	def fix_tags(self, tags):
		taglist = []
		for tag in tags:
			tag = tag.lower()
			tag = tag.strip()
			taglist.append(tag)
		return taglist

	def gather_nodes(self, pat):
		nodelist = []
		for node in self.nodes.keys():
			if pat in self.nodes[node].tags:
				nodelist.append(self.nodes[node])
		return nodelist

	def find_cards(self):
		cards = []
		for node in self.nodes.keys():
			if self.nodes[node].type == "card":
				cards.append(node)
		return cards

#### Public Methods.

	def find_node(self, node_id=None, text=None):
		if node_id:
			return self.nodes[node_id]
		elif text:
			for node in self.nodes.keys():
				if text == self.nodes[node].text:
					return self.nodes[node]
		else:
			return None

class Node():
	def __init__(self, node, npc, text, links, tags, coords, type_):
		self.node = node
		self.npc = npc
		self.text = text
		self.links = links
		self.tags = tags
		self.coords = coords
		self.type = type_
		if self.type == "card":
			title = self.tags[0].replace("card", "")
			title = title.replace("_", " ")
			title = title.strip()
			title = title.capitalize()
			names = [t[:4] for t in tags if "name" in t]
			self.dict = {"title":title, "maintext":self.text, "tags":names}

	def __repr__(self):
		return self.text
		
class Events:
	def __init__(self, dialogue):
		self.data = dialogue
		self.flags = self.get_flags()
		self.blocks = []
		self.playerwait_30 = False
		self.set_start_flags()

	def get_flags(self):
		flags = {}
		for node in self.data.nodes.keys():
			for tag in self.data.nodes[node].tags:
				if "flag" in tag:
					flags[tag] = False
				elif tag[:4] == "card":
					flags["flag_"+tag] = False
		return flags

	def set_start_flags(self):
		self.flags["flag_tutorial_part1"] = True
		for npc in self.data.names:
			self.flags["flag_start_"+npc.lower()] = True

	def update(self, dt):
		pass

class DialogueSystem:
	def __init__(self, parent, events, dialoguedata):
		self.parent = parent
		self.dialogue = dialoguedata
		self.events = events
		self.deck = []
		self.retired_deck = []
		self.card_changed = None
		self.callback_dict = {}
		self.once_list = []
		self.current_answer = None
		self.current_questions = []
		self.current_comment = None
		self.in_conversation = False

### Starting Conversations.
	def start_conversation(self, npc):
		node = None
		for meth in (self.find_conversation, self.find_comment, self.find_busy):
			node = meth(npc)
			if node != None:
				break
		self.setup_conversation(node)

	def end_conversation(self):
		self.in_conversation = False
		self.parent.gui.conv_panels_toggle()

	def find_conversation(self, npc):
		for start in self.dialogue.starts:
			if start.npc.lower() == npc:
				for tag in start.tags:
					if "block" in tag:
						if not self.blocked(start):
							return start
		else:
			return None

	def find_busy(self, npc):
		for comment in self.dialogue.comment_starts:
			if npc == comment.npc and "busy" in comment.tags:
				return comment

	def find_comment(self, npc):
		for comment in self.dialogue.comment_starts:
			if npc == comment.npc:
				for tag in comment.tags:
					if "block" in tag:
						if not self.blocked(comment):
							return comment
		return None

### Setting up a conversation.
	def setup_conversation(self, node):
		if node.type == "dialogue":
			if not self.in_conversation:
				self.in_conversation = True
				self.parent.gui.conv_panels_toggle()
			node, back = self.check_answer_tags(node)
			self.current_questions = self.get_questions(node)
			if not back:
				self.current_answer = node
			text_dict = {"top_text":str(self.current_answer),
			"question_list":[str(n) for n in self.current_questions]}
			self.parent.gui.add_text_to_conv_panels(text_dict)
		elif node.type == "comment":
			nodelist = []
			while True:
				self.check_answer_tags(node)
				name = "player"*("comment_reply" in node.tags) or node.npc.lower() 
				pos = self.parent.get_npc_pos(name)
				nodelist.append({"pos":pos, "text":str(node)})
				next_list = self.next_nodes(node)
				if next_list == []:
					break
				else:
					node = next_list[0]
			self.parent.gui.add_comments(nodelist)

	def question_picked(self, text):
		text = text[3:]
		if text != "Continue...":
			for node in self.current_questions:
				if text == node.text:
					self.check_question_tags(node) 
					break
			else:
				raise Exception("Selected text not found among Questions. That is not supposed to happen. \n{}\n{}".format(text, self.current_questions))
		else:
			node = self.current_answer
		next_list = self.next_nodes(node)
		if next_list != []:
			self.setup_conversation(next_list[0])
		else:
			self.end_conversation()

	def next_nodes(self, node):
		next_nodes = []
		for n in node.links:
			if node.coords[0] < self.dialogue.nodes[n].coords[0]:
				next_nodes.append(self.dialogue.nodes[n])
		return next_nodes

	def get_questions(self, node):
		nodelist = self.next_nodes(node)
		nodelist = self.check_for_blocks(nodelist)
		nodelist = [q for q in nodelist if q not in self.once_list]
		if len(nodelist) == 1:
			if "question" in nodelist[0].tags:
				return nodelist
		elif len(nodelist) > 1:
			return nodelist
		return ["Continue..."]

	def check_for_blocks(self, nodelist):
		return [i for i in nodelist if not self.blocked(i)]

	def blocked(self, node):
		blocked = False
		for tag in node.tags:
			if "block" in tag:
				blocked = True
				if "flag" not in tag:
					flag = tag.replace("block", "flag")
				else:
					flag = tag.replace("block_", "")
				if self.events.flags[flag]:
					self.events.flags[flag] = False
					blocked = False
					if tag not in self.events.blocks:
						self.events.blocks.append(tag)
		return blocked

	def check_answer_tags(self, node):
		back = False
		for tag in node.tags:
			if "flag" in tag:
				self.events.flags[tag] = True
			elif "card" == tag[:4]:
				self.events.flags["flag_"+tag] = True
				self.add_card_to_inventory(tag)
			elif "back" in tag:
				saved = tag.replace("back", "save")
				if saved in self.callback_dict.keys():
					node = self.callback_dict[saved]
					del(self.callback_dict[saved])
					back = True
		return node, back

	def check_question_tags(self, question):
		for tag in question.tags:
			if "save" in tag:
				self.once_list.append(question)
				self.callback_dict[tag] = self.current_answer

	def add_card_to_inventory(self, tag):
		node = self.find_card(tag)      ## <--- THIS IS COMING BACK NONE!! WHY??   
		self.deck.append(node)
		self.parent.gui.add_card(node.dict)

	def find_card(self, tag):
		for k, node in self.dialogue.nodes.items():
			if node.type == "card":
				print("Found Card, ", tag)
				if tag == node.tags[0]:
					return node
		else:
			assert Exception("Card not found. This should not happen. {}".format(tag))
