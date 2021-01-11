from enum import Enum

class TM_data:
    def __init__(self):
        self.__objects = {0: TM_object("ROUND END", -1, 0)}
        self.__order_list = [0]
        self.__current = 0

        self.add_object("A", 10, 2)
        self.add_object("B", 40, 5)
        self.__objects[1].add_effect(
            TM_effect("Krwawienie", None, 2, "$0% do testów odpierania chorób", TM_remove_mode.ROUND_END_TEST_STACK, "-1 Żyw, jeśli 0 -> $0% szans na śmierć z wykrwienia, jeśli dublet, cel leczy 1 stan" )
        )
        self.__objects[1].add_effect(
            TM_effect("Bezduszny", None, None, "nie musi wykonywać testów psychologicznych", TM_remove_mode.NONE, None)
        )
        self.__objects[2].add_effect(
            TM_effect("AA", 2, None, "ABC", TM_remove_mode.ROUND_END_COUNT, None)
        )
        self.__objects[2].add_effect(
            TM_effect("AB", 2, None, "ABCD", TM_remove_mode.ROUND_END_COUNT_BUT_TEST, "TEST")
        )
        self.__objects[2].add_effect(
            TM_effect("AC", 2, None, "ABCD", TM_remove_mode.ROUND_END_MESSAGE_ON_EXPIRE, "MESSAGE")
        )
        self.__objects[1].add_effect(
            TM_effect("AC", None, 3, "ABCD", TM_remove_mode.TURN_CAN_TEST_STACK, "TEST")
        )
        

    # object CRUD
    def add_object(self, name, initiative, advantage_max):
        id = self.__next_id()
        self.__objects[id] = TM_object(name, initiative, advantage_max)
        self.__order_list.append(id)
        self.__order_list.sort(key=lambda a: self.__objects[a]._initiative, reverse=True)
        return(self.tm_list)

    def get_object(self, id):
        return self.__objects[id].data

    def edit_object(self, id, name, initiative, advantage_max):
        self.__objects[id].edit(name, initiative, advantage_max)
        return (self.tm_list(), self.get_object(id))

    def change_advantage(self, id, new_advantage):
        return self.__objects[id].set_advantage(new_advantage)

    def remove_object(self, id):
        del self.__objects[id]
        self.__order_list.remove(id)
        if self.__current == id:
            self.next()
        return self.tm_list

    # effects
    def add_effect(self, id, name, rounds_to_end, stacks, effect, remove_mode, remove_description):
        effect = TM_effect(name, rounds_to_end, stacks, effect, remove_mode, remove_description)
        self.__objects[id].add_effect(effect)

    def edit_effect(self, id, effect_index, name, rounds_to_end, stacks, effect, remove_mode, remove_description):
        self.__objects[id]._effects[effect_index].edit(name, rounds_to_end, stacks, effect, remove_mode, remove_description)

    def get_current_effects_to_execute(self):
        effects_to_execute = []
        if self.__current == 0:
            for id, effects in [(x[0], x[1]._effects) for x in self.__objects.items()]:
                for i, effect in enumerate(effects, start=0):
                    if effect._remove_mode == TM_remove_mode.ROUND_END_COUNT:
                        if effect.execute_effect_remove():
                            del self.__objects[id]._effects[i]
                    elif effect._remove_mode == TM_remove_mode.ROUND_END_COUNT_BUT_TEST:
                        text = effect.execute_effect_remove()
                        if text:
                            effects_to_execute.append((id, i, effect._remove_mode, text))
                    elif effect._remove_mode == TM_remove_mode.ROUND_END_TEST_STACK:
                        effects_to_execute.append((id, i, TM_remove_mode.ROUND_END_TEST_STACK, effect.execute_effect_remove()))
                    elif effect._remove_mode == TM_remove_mode.ROUND_END_MESSAGE_ON_EXPIRE:
                        text = effect.execute_effect_remove()
                        if text:
                            del self.__objects[id]._effects[i]
                            effects_to_execute.append((id, i, effect._remove_mode, text))
        else:
            for i, effect in enumerate(self.__objects[self.__current]._effects, start=0):
                if effect._remove_mode == TM_remove_mode.TURN_CAN_TEST_STACK:
                    effects_to_execute.append((self.__current, i, TM_remove_mode.TURN_CAN_TEST_STACK, effect.execute_effect_remove()))
        return effects_to_execute

    def remove_effect(self, id, effect_index):
        self.__objects[id].remove_effect(effect_index)
    
    def effect_update_reaction(self, id, i, effect_mode, returned_value):
        if effect_mode == TM_remove_mode.ROUND_END_COUNT_BUT_TEST:
            if not returned_value:
                del self.__objects[id]._effects[i]
        elif effect_mode == TM_remove_mode.ROUND_END_TEST_STACK or \
             effect_mode == TM_remove_mode.TURN_CAN_TEST_STACK:
            if returned_value != 0:
                if self.__objects[id]._effects[i].change_stacks(returned_value):
                    del self.__objects[id]._effects[i]

    #oder_list
    def next(self):
        next_pos = self.__order_list.index(self.__current) + 1
        if next_pos == len(self.__order_list):
            next_pos = 0
        self.__current = self.__order_list[next_pos]
    
    #private
    def __next_id(self):
        if len(self.__objects.keys()) == 0:
            return 1
        else:
            return max(self.__objects.keys()) + 1

    @property
    def tm_list(self):
        current_pos = self.__order_list.index(self.__current)
        next_list = self.__order_list[current_pos:] + self.__order_list[:current_pos]
        return [(x, self.__objects[x]._name) for x in next_list]
        
class TM_object:
    def __init__(self, name, initiative, advantage_max):
        self._name = name
        self._initiative = initiative
        self._advantage = 0
        self._advantage_max = advantage_max
        self._effects = []
    
    def edit(self, name, initiative, advantage_max):
        self._name = name
        self._initiative = initiative
        self._advantage_max = advantage_max
        
    def set_advantage(self, advantage):
        if advantage < 0 or advantage > self._advantage_max:
            return False
        else:
            self._advantage = advantage
            return True

    def add_effect(self, effect):
        self._effects.append(effect)
    
    def remove_effect(self, effect_index):
        del self._effects[effect_index]

    @property
    def data(self):
        return (self._name, self._initiative, self._advantage, self._advantage_max, [x.show_effect_info() for x in self._effects])

class TM_effect:
    DESCRIPTION_REPLACE_WITH_STACK_SIGN = '$'
    DESCRIPTION_REPLACE_WITH_ROUNDS_SIGN = '@'
    def __init__(self, name, rounds_to_end, stacks, effect, remove_mode, remove_description):
        self._name = name
        self._rounds_to_end = rounds_to_end
        self._stacks = stacks
        self._effect = effect
        self._remove_mode = remove_mode
        self._remove_description = remove_description
    
    def show_effect_info(self):
        return (
            self._name, self._rounds_to_end, self._stacks, 
            self.__insert_counters(self._effect), self._remove_mode
        )

    def execute_effect_remove(self):
        if self._remove_mode == TM_remove_mode.ROUND_END_COUNT:
            if self._rounds_to_end == 0:
                return True
            else:
                self._rounds_to_end -= 1
                return False
        if self._remove_mode == TM_remove_mode.ROUND_END_MESSAGE_ON_EXPIRE or \
           self._remove_mode == TM_remove_mode.ROUND_END_COUNT_BUT_TEST:
            if self._rounds_to_end == 0:
                return self.__insert_counters(self._remove_description)
            else:
                self._rounds_to_end -= 1
                return
        if self._remove_mode == TM_remove_mode.ROUND_END_TEST_STACK or \
           self._remove_mode == TM_remove_mode.TURN_CAN_TEST_STACK:
            return self.__insert_counters(self._remove_description)
            
    def change_stacks(self, stacks_delta):
        self._stacks += stacks_delta
        if self._stacks == 0:
            return True

    def edit(self, name, rounds_to_end, stacks, effect, remove_mode, remove_description):
        self._name = name
        self._rounds_to_end = rounds_to_end
        self._stacks = stacks
        self._effect = effect
        self._remove_mode = remove_mode
        self._remove_description = remove_description 
    
    def __insert_counters(self, text):
        return text.replace(self.DESCRIPTION_REPLACE_WITH_STACK_SIGN, str(self._stacks)) \
                   .replace(self.DESCRIPTION_REPLACE_WITH_ROUNDS_SIGN, str(self._rounds_to_end))
        
class TM_remove_mode(Enum):
    ROUND_END_TEST_STACK = "Make test at end of round to remove stacks"
    ROUND_END_COUNT = "Effect will expire after some rounds"
    TURN_CAN_TEST_STACK = "Can make test during turn to remove stacks"
    NONE = "Effect won't expire durring this fight"
    ROUND_END_COUNT_BUT_TEST = "Effect will expire after some rounds, but can be prolong with test"
    ROUND_END_MESSAGE_ON_EXPIRE = "Effect will happen at expired"