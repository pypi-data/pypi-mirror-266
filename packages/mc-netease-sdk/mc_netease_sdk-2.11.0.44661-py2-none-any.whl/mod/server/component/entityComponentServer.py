# -*- coding: utf-8 -*-

from typing import List
from mod.common.component.baseComponent import BaseComponent

class EntityComponentServer(BaseComponent):
    def HasComponent(self, attrType):
        # type: (int) -> bool
        """
        判断实体是否有原版组件
        """
        pass

    def GetAllComponentsName(self):
        # type: () -> List[str]
        """
        获取实体所拥有的原版组件list
        """
        pass

