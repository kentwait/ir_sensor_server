from api.models import control
import re


class IRDevice:
    def __init__(self, device_id, power_control, **kwargs):
        # Use object.__setattr__ to bypass __setattr__ method
        object.__setattr__(self, 'device_id', device_id)
        self.power = power_control
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)
    
    def add_control(self, control):
        if control.name in self.__dict__.keys():
            raise ValueError('controller name "{}" already belongs to an existing control'.format(control.name))
        object.__setattr__(self, control.name, control)
        

class Light(IRDevice):
    def __init__(self, device_id, power_control, brightness_control, tone_control, **kwargs):
        super().__init__(device_id, power_control,
                         brightness=brightness_control,
                         tone=tone_control,
                         **kwargs)
    
    @classmethod
    def interactive_setup(cls):
        print('--------------------')
        print(' Initial setting    ')
        print('--------------------')
        device_id = input('Unique device name')
        # Initialize
        # Create controls
        print('# Power')
        power_control = control.BinaryControl.interactive_new()
        print('# Brightness')
        brightness_control = control.LevelControl.interactive_new()
        print('# Tone')
        tone_control = control.LevelControl.interactive_new()

        print('--------------------')
        print(' Additional setting ')
        print('--------------------')
        kwargs = additional_commands()

        print('Set-up completed for Light "{}".'.format(device_id))  # TODO: Print summary of controllers
        return cls(device_id, power_control, brightness_control, tone_control, **kwargs)

class TV(IRDevice):
    def __init__(self, device_id, power_control, volume_control, channel_control, input_source_control,
                 video_play_control, mute_control, **kwargs):
        super().__init__(device_id, power_control,
                         volume=volume_control,
                         channel=channel_control,
                         input_source=input_source_control, 
                         video_play=video_play_control,
                         mute=mute_control,
                         **kwargs)
    
    @classmethod
    def interactive_setup(cls):
        print('-----------------')
        print(' Initial setting ')
        print('-----------------')
        device_id = input('Unique device name')
        # Initialize
        # Create controls
        print('# Power')
        power_control = control.BinaryControl.interactive_new()
        print('# Volume')
        volume_control = control.LevelControl.interactive_new()
        print('# Channel')
        channel_control = control.PrevNextSeletableControl.interactive_new()
        print('# Input source')
        input_source_control = control.NextSelectableControl.interactive_setup()
        print('# Play/pause')
        video_play_control = control.BinaryControl.interactive_setup()
        print('# Mute')
        mute_control = control.ToggleableControl.interactive_setup()

        print('--------------------')
        print(' Additional setting ')
        print('--------------------')
        kwargs = additional_commands()

        print('Set-up completed for TV "{}".'.format(device_id))  # TODO: Print summary of controllers
        return cls(device_id, power_control, volume_control, channel_control, input_source_control,
                   video_play_control, mute_control, **kwargs)

class Aircon(IRDevice):
    def __init__(self, device_id, power_control, temp_control, fan_speed_control, mode_control, swing_control,
                 **kwargs):
        super().__init__(device_id, power_control,
                         temp=temp_control,
                         fan_speed=fan_speed_control,
                         mode=mode_control,
                         swing=swing_control,
                         **kwargs)

    @classmethod
    def interactive_setup(cls):
        print('--------------------')
        print(' Initial setting    ')
        print('--------------------')
        device_id = input('Unique device name')
        # Initialize
        # Create controls
        print('# Power')
        power_control = control.BinaryControl.interactive_new()
        print('# Temperature')
        temp_control = control.LevelControl.interactive_new()
        print('# Fan speed')
        fan_speed_control = control.NextSelectableControl.interactive_new()
        print('# Mode')
        mode_control = control.NextSelectableControl.interactive_new()
        print('# Swing')
        swing_control = control.NextSelectableControl.interactive_new()

        print('--------------------')
        print(' Additional setting ')
        print('--------------------')
        kwargs = additional_commands()

        print('Set-up completed for Light "{}".'.format(device_id))  # TODO: Print summary of controllers
        return cls(device_id, power_control, temp_control, fan_speed_control, mode_control, swing_control,
                   **kwargs)


def additional_commands():
    kwargs = {}
    print('If your device has other initial settings, add them in this section')
    print('Press Ctrl+C when finished.\n')
    control_choices = {
        0: control.StatelessControl,  # stateless
        1: control.SetterControl,  # setter control.
        2: control.ToggleableControl,  # switch, same key, toggle
        3: control.BinaryControl,  # switch, separate keys
        4: control.LevelControl,  # has levels with min and max
        5: control.NextSelectableControl,  # list of choices, goes to next choice when pressed
        6: control.PrevNextSeletableControl,  # list of choices, has prev and next buttons, cycles
    }
    control_choice_desc = {
        0: 'Stateless. Just register a button/key and do not track it underlying state.',
        1: 'Setter control. Pressing the button will set it to a particular state. '
            'Presses while in the state will not do anything.',
        2: 'Switch control. Uses one button/key to toggle between states',
        3: 'Switch control variant. Uses two buttons to toggle between states. '
            'Acts like 2 setter controls tracking the same state',
        4: 'Level control. Underlying state is a series of level and 2 buttons increase or decrease the value, '
            'ie. volume',
        5: 'Simple list control. Pressing the button/key will select the next item in the list. '
            'If at the end of the list, cycles back to the start.',
        6: 'Two-way list control. Underlying state is also a list but two buttons provide forward and '
            'backward navigation, ie. channel up and down.',
    }
    while True:
        try:
            name = input('Name of setting/control: ').strip()
            print('Type of setting/control. Select a number from the choices below.')
            for k, v in control_choice_desc.items():
                print('  {} : {}'.format(k, v))
            kind = int(input('Choice: ').strip())
            print('Now setting up the setting/control...')
            controller = control_choices[kind].interactive_setup()
            kwargs[name] = controller
            print('Control "{}" saved.\n'.format(name))
        except KeyboardInterrupt:
            break
    return kwargs
