from dragonfly.actions.action_base import *
from dragonfly.actions.action_function import Function

class AsyncState:
    def __init__(self):
        self.iteration = 0
        self.complete = False
        
class AsyncItem(ActionBase):

    def __init__(self):
        ActionBase.__init__(self)

    def __add__(self, other):
        return AsyncItemSeries(self, other)

    def __iadd__(self, other):
        return AsyncItemSeries(self, other)

    def __mul__(self, factor):
        return AsyncRepetition(self, factor)
        
    def __imul__(self, factor):
        return AsyncRepetition(self, factor)
                      
    
class AsyncFunction(AsyncItem, Function):
    def __init__(self, function, remap_data=None, **defaults):
        Function.__init__(self, function, remap_data, **defaults)
    
    def execute(self, data=None):
        async_state = data["async_state"]
        try:
            if Function.execute(self, data) == False:
                raise ActionError(str(self))
        except ActionError as e:
            async_state.complete = True
            return False
    
class AsyncItemSeries(AsyncItem, ActionSeries):

    def __init__(self, *actions):
        ActionSeries.__init__(self, *actions)
        self.next_action = 0
        self.sub_state = AsyncState()
        
    def execute(self, data=None):
        async_state = data["async_state"]
        if async_state.iteration == 0:
            self.next_action = 0
            self.sub_state = AsyncState()
            
        if self.next_action < len(self._actions):
            sub_data = data.copy()
            sub_data["async_state"] = self.sub_state

            action = self._actions[self.next_action]
            try:
                if action.execute(sub_data) == False:
                    raise ActionError(str(self))
            except ActionError as e:
                async_state.complete = True
                return False

            self.sub_state.iteration += 1
            if self.sub_state.complete:
                self.next_action += 1
                self.sub_state = AsyncState()
       
        if self.next_action >= len(self._actions):
            async_state.complete = True
           
    
class AsyncRepetition(AsyncItem, ActionRepetition):
    def __init__(self, action, factor):
        ActionRepetition.__init__(self, action, factor)
        self._series = None
        
    def factor(self, data=None):
        if isinstance(self._factor, integer_types):
            repeat = self._factor
        elif isinstance(self._factor, Repeat):
            repeat = self._factor.factor(data)
        else:
            raise ActionError("Invalid repeat factor: %r" % (self._factor,))
        return repeat
            
    def execute(self, data=None):
        async_state = data["async_state"]
        if async_state.iteration == 0:
            repeat_count = self.factor(data)
            actions = (self._action for i in range(repeat_count))
            self._series = AsyncItemSeries(*actions)
        
        return self._series.execute(data)
        
        
class AsyncRepeat(Repeat):
    pass
