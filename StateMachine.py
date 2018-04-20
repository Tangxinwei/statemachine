# -*- coding:utf-8 -*-
import StateNode

class StateMachine(object):
	def __init__(self):
		self._activeNode = None
		self._eventObjectList = []
		self._AllNodes = {}
		self._ActiveNodeList = []
		self._isTransition = False

	def AddEventObject(self, eventObject):
		self._eventObjectList.append(eventObject)

	def GetCurrentActiveNodesName(self):
		ret = []
		for node in self._ActiveNodeList:
			ret.append(node.GetCurrentActiveNodesName())
		return ret

	def CreateStateNode(self, name, keepHistory = False, isDefault = False):
		if name in self._AllNodes:
			raise Exception("%s has exits" % name)
		node = StateNode.StateNode(name, keepHistory, isDefault)
		node.OnAddToStateMachine(self)
		self._AllNodes[name] = node
		return node

	def TriggerEvent(self, stateName, eventName):
		print(stateName, eventName)

	def ActiveStateMachine(self):
		for name, node in self._AllNodes.items():
			if not node.HasParent() and node.CheckIsDefault():
				self._ActiveNodeList.append(node)
				node.On_Entry(True)

	def ReceiveTransitionEvent(self, eventName):
		self._isTransition = True
		for node in self._ActiveNodeList:
			node.ReceiveTransitionEvent(eventName)
		self._isTransition = False

'''
	locomotion
		normal
			idle
			move
		nonemove
	behavior
		skill
		forcetrans
			blow
			knockdown
		behavioridle
'''
if __name__ == "__main__":
	machine = StateMachine()
	locomotion = machine.CreateStateNode("locomotion", isDefault = True)
	normal = machine.CreateStateNode("normal", isDefault = True)
	idle = machine.CreateStateNode("idle", isDefault = True)
	move = machine.CreateStateNode("move", isDefault = True)
	nonemove = machine.CreateStateNode("nonemove")
	behavior = machine.CreateStateNode("behavior", isDefault = True)
	skill = machine.CreateStateNode("skill")
	forcetrans = machine.CreateStateNode("forcetrans", keepHistory = True, isDefault = True)
	blow = machine.CreateStateNode("blow", isDefault = True)
	knockdown = machine.CreateStateNode("knockdown")
	behavioridle = machine.CreateStateNode("behavioridle")

	locomotion.AddChildNode(normal)
	locomotion.AddChildNode(nonemove)

	normal.AddChildNode(idle)
	normal.AddChildNode(move)

	behavior.AddChildNode(skill)
	behavior.AddChildNode(forcetrans)
	behavior.AddChildNode(behavioridle)

	forcetrans.AddChildNode(blow)
	forcetrans.AddChildNode(knockdown)

	idle.AddTransition("NoneMove", nonemove)
	nonemove.AddTransition("ToMove", move)
	nonemove.AddTransition("ToNormal", normal)

	machine.ActiveStateMachine()
	print("-------")
	machine.ReceiveTransitionEvent("NoneMove")
	print(machine.GetCurrentActiveNodesName())
	print("-------")
	machine.ReceiveTransitionEvent("ToNormal")
	print(machine.GetCurrentActiveNodesName())
	
