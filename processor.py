import re
import random

from dealer_templates import deal_templates
from fighter_templates import fight_templates
from bibler_templates import *


class Arthur:
    """ A class to represent all Arthurs around the world, but we all know there
        is only one true Arthur...
        Its methods 'deal' and 'fight' represent different modes of conversation,
        receive only the text as an argument and produce an answer.
        The answer is returned in the form of a dictionary with the following fields:
            -'text' - the text of the answer itself
            -'next_mode' - the mode that has to be turned on next. Modes can be
            viewed in the main.py module
            -'normal' - used only once in BIBLE mode as described in 'bible' method's docs
    """

    def __init__(self):
        self.anger = 0
        self.anger_threshold = 8
        self.deal_temps = deal_templates
        self.fight_temps = fight_templates

    def deal(self, text: str) -> dict:
        """ A method to make responses in the DEFAULT mode, which is
            an initial and main one. It goes through all the templates in
            'dealer_templates' using 'template_searcher' method to check if any template corresponds.
            Returns a dictionary as described in the class's documentation.
        """
        answer = self.template_searcher(text, self.deal_temps)
        if answer == None:
            return {'text': "Че бля?"}

        if self.anger >= self.anger_threshold:
            answer['next_mode'] = 1  # i.e. FIGHT

        return answer

    def template_searcher(self, text, templates):
        """ Goes through all the given templates, and in case it finds one, whose
            regular expression matches the text, it marks that template as
            asked. It also adds the template's field 'anger' to that of the class,
            and finally returns a dictionary with the text. In case the template
            wasn't found, returns None.
        """
        for template in templates:
            compiler = re.compile(template['pattern'], flags=re.I)
            if compiler.search(text):
                answer = {'text': self.group_helper(
                    template, compiler.search(text))}
                template['asked'] = True
                if 'anger' in template:
                    self.anger += template['anger']

                if 'next_mode' in template:
                    answer['next_mode'] = template['next_mode']

                return answer
        return None

    def group_helper(self, template, match_object):
        """ Return a string produced by fitting corresponding groups into
            the response of the template from the given match object.
            Also before filling in the gaps it calls the 'check_asked'
            function to check whether this template has already been used.
        """
        if 'groups' not in template:
            return self.check_asked(template)
        else:

            retrieved_groups = match_object.group(*template['groups'])
            return self.check_asked(template).format(*retrieved_groups)

    def check_asked(self, template):
        """ Returns a corresponding response depending on whether this
            pattern has already been asked or not
        """
        if 'asked' not in template:
            return template['response']
        else:
            return template['alternative']

    def fight(self, text: str):
        """ A method to respond to user's messages in FIGHT mode. The types of
            messages in this mode are strictly confined, since the input is
            performed via an answering keyboard. It can also turn back to the default
            mode if the instance's anger is at least half the threshold.
            Returns a dictionary with fields as described in class's docs.
        """
        answer = self.template_searcher(text, fight_templates)

        # 'template_searcher' might return None if no template was matched
        if answer == None:
            return {'text': 'На кнопки нажимай блять!!!'}

        if self.anger <= self.anger_threshold/2:
            answer['next_mode'] = 0  # i.e. going back to DEFAULT

        return answer

    def bible(self, text: str):
        """ A method to interact with user's messages in BIBLE mode.
            The 'normal' field means that we actually pass a prediction.
            Used to distinguish it prediction messages from other
            typed from the keyboard.
        """
        if text == bibler_keyboard[0][0]:
            return {'text': self.bible_helper(), 'normal': True}
        if text == bibler_keyboard[1][0]:
            return {'text': "Я тебе ща нагадаю коронавирус блять!"}
        if text == bibler_keyboard[2][0]:
            return {'text': 'Вот бы спеть сейчас...', 'next_mode': 0}
        return None

    def bible_helper(self):
        """ Returns a random string of prediction
        """
        person = random.randint(0, 7)
        prediction = (subjects[person] +
                      random.choice(general + individual[person]))
        return prediction


if __name__ == '__main__':
    arthur = Arthur()
    print(arthur.bible('Еще'))
