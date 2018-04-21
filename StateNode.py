# -*- coding:utf-8 -*-
class StateNode(object):
	def __init__(self, name, keepHistory = False, isDefault = False):
		self._name = name
		self._isActive = False
		self._machine = None
		self._parentNode = None
		self._activeNodeList = []
		self._childNodeList = []
		self._defaultChildNodeList = [] #进入该状态时候的默认节点
		self._keepHistory = keepHistory #进入该状态的时候,子状态是保持默认还是最后一次离开该状态时候的状态
		self._isDefault = isDefault
		self._transition = {}
		self._cachedNodesForLCS = None #用来计算最近父节点的一个cache

	def CheckIsDefault(self):
		return self._isDefault

	def HasParent(self):
		return self._parentNode

	def OnAddToStateMachine(self, machine):
		if self._machine:
			raise Exception("node %s already in machine" % self._name)
		self._machine = machine

	def OnAddToParentNode(self, parent):
		if self._parentNode:
			raise Exception("node %s already have parent" % self._name)
		self._parentNode = parent

	def AddChildNode(self, node):
		self._childNodeList.append(node)
		if node._isDefault:
			self._defaultChildNodeList.append(node)
		node.OnAddToParentNode(self)

	def AddTransition(self, eventName, targetNode):
		self._transition[eventName] = targetNode

	def GetCurrentActiveNodesName(self):
		ret = [self._name]
		for node in self._activeNodeList:
			ret.append(node.GetCurrentActiveNodesName())
		return ret

	def OnActiveStateMachine(self):
		self.On_Entry()
		for node in self._activeNodeList:
			node.OnActiveStateMachine()

	#isFirst表示是否首次激活
	def On_Entry(self):
		self._isActive = True
		self._machine.TriggerEvent(self._name, "Entry")

	def On_Exit(self):
		self._isActive = False
		self._machine.TriggerEvent(self._name, "Exit")

	def TriggerAllExit(self):
		for node in self._activeNodeList:
			node.TriggerAllExit()
		self.On_Exit()

	def TriggerAllEntry(self):
		self.On_Entry()
		if self._keepHistory:
			for node in self._activeNodeList:
				node.TriggerAllEntry()
		else:
			self._activeNodeList.clear()
			for node in self._defaultChildNodeList:
				self._activeNodeList.append(node)
				node.TriggerAllEntry()

	def ReceiveTransitionEvent(self, eventName):
		nextNode = self._transition.get(eventName)
		if nextNode:
			#先找到一条到nextNode的路径
			nowNode = self
			while nowNode:
				nowNode._cachedNodesForLCS = self
				nowNode = nowNode._parentNode
			#需要转换的状态是当前状态的父节点,这个一定是状态机写错了
			if nextNode._cachedNodesForLCS == self:
				raise Exception("cannot transition to parent state %s %s" % (self._name, nextNode._name))
			nowNode = nextNode
			pathList = []
			while nowNode and nowNode._cachedNodesForLCS != self:
				pathList.append(nowNode)
				nowNode = nowNode._parentNode
			#需要转换的状态是当前状态的父节点,这个一定是状态机写错了
			if nowNode == self:
				raise Exception("cannot transition to parent state %s %s" % (self._name, nextNode._name))
			#先退出自己的子节点
			self.TriggerAllExit()
			#两个状态之间没有公共节点,说明是最外面一层的状态机
			if nowNode is None:
				#节点不允许并行
				if len(self._machine._activeNodeList) == 1:
					self._machine._activeNodeList[0] = pathList[-1]
					pathList[-1].On_Entry()
					nowNode = pathList[-1]
					for i in range(len(pathList) - 2, -1, -1):
						if len(nowNode._activeNodeList) == 1:
							nowNode._activeNodeList[1] = pathList[i]
							nowNode = pathList[i]
							if i != 0:
								nowNode.On_Entry()
						elif len(nowNode._activeNodeList) > 1:
							#节点允许并行,并行的节点是不可能跨节点转移的..
							raise Exception("cannot transist")
						else:
							raise Exception("no active nodes")
						pathList[0].TriggerAllEntry()
				elif len(self._machine._activeNodeList) > 1:
					#节点允许并行,并行的节点是不可能跨节点转移的..
					raise Exception("cannot transist")
				else:
					raise Exception("no active nodes")
			else:
				#往上退出到nowNode位置
				travsalNode = self._parentNode
				lastTravaslNode = self
				while travsalNode and travsalNode != nowNode:
					travsalNode.On_Exit()
					lastTravaslNode = travsalNode
					travsalNode = travsalNode._parentNode
				#沿着pathList依次进入
				for i in range(len(pathList) - 1, -1, -1):
					#节点不允许并行
					if len(nowNode._activeNodeList) == 1:
						nowNode._activeNodeList[0] = pathList[i]
						nowNode = pathList[i]
						if i != 0:
							nowNode.On_Entry()
					elif len(nowNode._activeNodeList) > 1:
						#节点允许并行,并行的节点是不可能跨节点转移的..
						raise Exception("cannot transist %s" % nowNode._name)
					else:
						raise Exception("no active nodes %s" % nowNode._name)
				pathList[0].TriggerAllEntry()
		else:
			for node in self._activeNodeList:
				if self._isActive:
					node.ReceiveTransitionEvent(eventName)