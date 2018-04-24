# -*- coding:utf-8 -*-
import StateNode

class StateMachine(object):
	def __init__(self):
		self._eventObjectList = []
		self._allNodes = {}
		self._activeNodeList = []
		self._isTransition = False

	def AddEventObject(self, eventObject):
		self._eventObjectList.append(eventObject)

	def GetCurrentActiveNodesName(self):
		ret = []
		for node in self._activeNodeList:
			ret.append(node.GetCurrentActiveNodesName())
		return ret

	def CreateStateNode(self, name, keepHistory = False, isDefault = False):
		if name in self._allNodes:
			raise Exception("%s has exits" % name)
		node = StateNode.StateNode(name, keepHistory, isDefault)
		node.OnAddToStateMachine(self)
		self._allNodes[name] = node
		return node

	def TriggerEventInner(self, stateName, eventName, globalExtraData, localExtraData, eventData):
		fullName = stateName + "_" + eventName
		for ob in self._eventObjectList:
			func = getattr(ob, fullName, None)
			#在globalExtraData中设置PreventEvent为True,该事件将不再传递
			#在localExtraData中设置PreventEventToChild为True,该事件将不再传递给当前子节点
			func and func(globalExtraData, localExtraData, eventData)

	def TriggerEvent(self, eventName, eventData, skipChild = False):
		if self._isTransition:
			raise Exception("cannot trigger event when transition")
		
		globalExtraData = {}
		for node in self._activeNodeList:
			if not globalExtraData.get("PreventEvent"):
				localExtraData = {}
				node.TriggerEvent(eventName, skipChild, globalExtraData, localExtraData, eventData)

	def ActiveStateMachine(self):
		for name, node in self._allNodes.items():
			#一开始就初始化activenodes为defaultnodes
			if node._defaultChildNodeList:
				for cnode in node._defaultChildNodeList:
					node._activeNodeList.append(cnode)
			if not node.HasParent() and node.CheckIsDefault():
				self._activeNodeList.append(node)
				node.OnActiveStateMachine()

	def ReceiveTransitionEvent(self, eventName):
		self._isTransition = True
		for node in self._activeNodeList:
			node.ReceiveTransitionEvent(eventName)
		self._isTransition = False

	def InitFromConfig(self, config):
		for nodeParam in config["nodes"]:
			self.CreateStateNode(nodeParam["name"], nodeParam.get("keepHistory", False), nodeParam.get("isDefault", False))
		for parentName, childrenNames in config.get("relations", {}).items():
			parentNode = self._allNodes[parentName]
			for nodename in childrenNames:
				node = self._allNodes[nodename]
				parentNode.AddChildNode(node)
		for sourceNodeName, eventName, targetNodeName in config.get("transitions", []):
			sourceNode = self._allNodes[sourceNodeName]
			targetNode = self._allNodes[targetNodeName]
			sourceNode.AddTransition(eventName, targetNode)
		machine.ActiveStateMachine()

'''
	locomotion  default keephistory
		normal   default
			idle  default keephistory
				idle_special concurrence default
					idle_special_1 default
					idle_special_2 default
				idle_normal
			move  keephistory
				move_normal   default
				move_fast
		nonemove
	behavior   default
		skill
		forcetrans
			blow   default
			knockdown
		behavioridle default
'''
if __name__ == "__main__":
	machine = StateMachine()
	config = {\
				"nodes" : [\
							{"name" : "locomotion", "isDefault" : True, "keepHistory" : True},
							{"name" : "normal", "isDefault" : True, },
							{"name" : "idle", "isDefault" : True, "keepHistory" : True},
							{"name" : "idle_special", "isDefault" : True, },
							{"name" : "idle_special_1", "isDefault" : True, },
							{"name" : "idle_special_2", "isDefault" : True, },
							{"name" : "idle_normal", },
							{"name" : "move", "keepHistory" : True},
							{"name" : "move_normal", "isDefault" : True},
							{"name" : "move_fast", },
							{"name" : "nonemove", },
							{"name" : "behavior", "isDefault" : True},
							{"name" : "skill", },
							{"name" : "forcetrans", },
							{"name" : "blow", "isDefault" : True},
							{"name" : "knockdown", },
							{"name" : "behavioridle", "isDefault" : True},
						],
				"relations" : {\
							"locomotion" : ("normal", "nonemove"),
							"normal" : ("idle", "move"),
							"idle" : ("idle_special", "idle_normal"),
							"idle_special" : ("idle_special_1", "idle_special_2"),
							"move" : ("move_normal", "move_fast"),
							"behavior" : ("skill", "forcetrans", "behavioridle"),
							"forcetrans" : ("blow", "knockdown"),
						},
				"transitions" : [\
						("normal", "EventNoneNormal", "nonemove"),
						("behavioridle", "EventNoneNormal", "knockdown"),
						("nonemove", "EventNoneNormal", "normal"),
						("nonemove", "EventIdleNormal", "idle_normal"),
				],
		}
	machine.InitFromConfig(config)
	print(machine.GetCurrentActiveNodesName())
	print("----------------------------------")
	machine.ReceiveTransitionEvent("EventNoneNormal")
	print(machine.GetCurrentActiveNodesName())
	print("----------------------------------")
	machine.ReceiveTransitionEvent("EventIdleNormal")
	print(machine.GetCurrentActiveNodesName())
	print("----------------------------------")
	machine.ReceiveTransitionEvent("EventNoneNormal")
	print(machine.GetCurrentActiveNodesName())
	print("----------------------------------")
	machine.ReceiveTransitionEvent("EventNoneNormal")
	print(machine.GetCurrentActiveNodesName())
	print("----------------------------------")

	class A(object):
		def behavior_event1(self, globalExtraData, localExtraData, eventData):
			print("behavior_event1")
			localExtraData["PreventEventToChild"] = True
		
		def forcetrans_event1(self, globalExtraData, localExtraData, eventData):
			print("forcetrans_event1")

		def behavior_event2(self, globalExtraData, localExtraData, eventData):
			print("behavior_event2")

		def forcetrans_event2(self, globalExtraData, localExtraData, eventData):
			print("forcetrans_event2")

	machine.AddEventObject(A())
	machine.TriggerEvent("event1", {})
	machine.TriggerEvent("event2", {})
