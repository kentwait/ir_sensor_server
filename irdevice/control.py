from api.config import IR_EMITTER_GPIO, IR_RECEIVER_GPIO
from ircodec.command import CommandSet, Command
import re


class Control:
    def __init__(self, var_id, current_state, possible_states, commands={},
                 local_db=None, cloud_db=None):
        self.name = var_id
        self.state = current_state
        self.commands = commands
        self.possible_states = possible_states
        self.local_db = local_db
        self.cloud_db = cloud_db
    
    def set_state(self, state):
        # Set local object state
        self.state = state
        # TODO: Set local database state
        # TODO: Set DynamoDB remote state

    def set_command(self, command_id, command_obj):
        self.commands[command_id] = command_obj


class StatelessControl(Control):
    def set(self):
        self.commands['set'].emit(emitter_gpio=IR_EMITTER_GPIO)
        self.set_state(None)

    @classmethod
    def interactive_setup(cls, name=None):
        if name is None:
            name = input('Unique control name: ').strip()
        description = input('Description: ').strip()
        possible_states = [None]
        print('Press the key after the queue.')
        command_obj = Command.receive(name, IR_RECEIVER_GPIO, description)
        command_obj.normalize()
        print('Stateless control set-up completed.')
        return cls(name, None, possible_states, {'set': command_obj})


class SetterControl(Control):
    def set(self):
        self.commands['set'].emit(emitter_gpio=IR_EMITTER_GPIO)
        self.set_state(True)

    @classmethod
    def interactive_setup(cls, name=None):
        if name is None:
            name = input('Unique control name: ').strip()
        state = input('Current state (True/False): ').strip()
        possible_states = [True, False]
        print('Press the key after the queue.')
        command_obj = Command.receive(name, IR_RECEIVER_GPIO)
        command_obj.normalize()
        print('Setter control set-up completed.')
        return cls(name, state, possible_states, {'set': command_obj})


class BinaryControl(Control):
    def on(self):
        self.commands['on'].emit(emitter_gpio=IR_EMITTER_GPIO)
        self.set_state(True)

    def off(self):
        self.commands['off'].emit(emitter_gpio=IR_EMITTER_GPIO)
        self.set_state(False)

    @classmethod
    def interactive_setup(cls, name=None):
        if name is None:
            name = input('Unique control name: ').strip()
        state = input('Current state (True/False): ').strip()
        possible_states = [True, False]
        print('Press the "on" key after the queue.')
        on_obj = Command.receive(name, IR_RECEIVER_GPIO)
        on_obj.normalize()
        print('Press the "off" key after the queue.')
        off_obj = Command.receive(name, IR_RECEIVER_GPIO)
        off_obj.normalize()
        print('Binary switch set-up completed.')
        return cls(name, state, possible_states, 
                   {'on': on_obj, 'off': off_obj})


class ToggleableControl(BinaryControl):
    def toggle_state(self):
        if self.state:
            self.off()
        else:
            self.on()

    @classmethod
    def interactive_setup(cls, name=None):
        if name is None:
            name = input('Unique control name: ').strip()
        state = input('Current state (True/False): ').strip()
        possible_states = [True, False]
        print('Press the key after the queue.')
        toggle_obj = Command.receive(name, IR_RECEIVER_GPIO)
        toggle_obj.normalize()
        print('Binary toggle switch set-up completed.')
        return cls(name, state, possible_states, 
                   {'on': toggle_obj, 'off': toggle_obj})

class LevelControl(Control):
    def __init__(self, var_id, current_state, min_state, max_state, commands={},
                 local_db=None, cloud_db=None):
        super().__init__(var_id, current_state, range(min_state, max_state+1), commands=commands,
                         local_db=local_db, cloud_db=cloud_db)

    def up(self):
        if self.state == self.possible_states.stop - 1:
            raise ValueError('{} already at maximum'.format(self.name))  # TODO: create a new error for this
        self.commands['up'].emit(emitter_gpio=IR_EMITTER_GPIO)
        self.set_state(self.state + 1)

    def down(self):
        if self.state == self.possible_states.start:
            raise ValueError('{} already at minimum'.format(self.name))  # TODO: create a new error for this
        self.commands['down'].emit(emitter_gpio=IR_EMITTER_GPIO)
        self.set_state(self.state - 1)


    @classmethod
    def interactive_setup(cls, name=None):
        if name is None:
            name = input('Unique control name: ').strip()
        min_state = int(input('Minimum value: ').strip())
        max_state = int(input('Maximum value: ').strip())
        possible_states = range(min_state, max_state+1)
        state = int(input('Current state: ').strip())
        while state not in possible_states:
            state = int(input('Invalid state ({}), current '
                              'state must be one of possible states: '.format(state)).strip())
        print('Press the "up" key after the queue.')
        up_obj = Command.receive(name, IR_RECEIVER_GPIO)
        up_obj.normalize()
        print('Press the "down" key after the queue.')
        down_obj = Command.receive(name, IR_RECEIVER_GPIO)
        down_obj.normalize()
        print('Level control set-up completed.')
        return cls(name, state, min_state, max_state, 
                   {'up': up_obj, 'down': down_obj})


class NextSelectableControl(LevelControl):
    def next(self):
        if self.state == self.possible_states[-1]:
            self.set_state(self.possible_states[0])
        else:
            i = self.possible_states.index(self.channel)
            self.set_state(self.possible_states[i+1])
        self.commands['next'].emit(emitter_gpio=IR_EMITTER_GPIO)

    @classmethod
    def interactive_setup(cls, name=None):
        if name is None:
            name = input('Unique control name: ').strip()
        possible_states = input('Possible states (seperate with commas ","): ').strip()
        possible_states = re.split(r'\s*\,\s*', possible_states)
        state = input('Current state: ').strip()
        while state not in possible_states:
            state = input('Invalid state ({}), current '
                          'state must be one of possible states: '.format(state)).strip()
        print('Press the key after the queue.')
        command_obj = Command.receive(name, IR_RECEIVER_GPIO)
        command_obj.normalize()
        print('Simple list control set-up completed.')
        return cls(name, state, possible_states, {'next': command_obj})


class PrevNextSeletableControl(LevelControl):
    def next(self):
        if self.state == self.possible_states[-1]:
            self.set_state(self.possible_states[0])
        else:
            i = self.possible_states.index(self.channel)
            self.set_state(self.possible_states[i+1])
        self.commands['next'].emit(emitter_gpio=IR_EMITTER_GPIO)

    def previous(self):
        if self.state == self.possible_states[0]:
            self.set_state(self.possible_states[-1])
        else:
            i = self.possible_states.index(self.channel)
            self.set_state(self.possible_states[i-1])
        self.commands['previous'].emit(emitter_gpio=IR_EMITTER_GPIO)

    @classmethod
    def interactive_setup(cls, name=None):
        if name is None:
            name = input('Unique control name: ').strip()
        possible_states = input('Possible states (seperate with commas ","): ').strip()
        possible_states = re.split(r'\s*\,\s*', possible_states)
        state = input('Current state: ').strip()
        while state not in possible_states:
            state = input('Invalid state ({}), current '
                          'state must be one of possible states: '.format(state)).strip()
        print('Press the "next" key after the queue.')
        up_obj = Command.receive(name, IR_RECEIVER_GPIO)
        up_obj.normalize()
        print('Press the "previous" key after the queue.')
        down_obj = Command.receive(name, IR_RECEIVER_GPIO)
        down_obj.normalize()
        print('Two-way list control set-up completed.')
        return cls(name, state, possible_states, 
                   {'next': up_obj, 'previous': down_obj})
