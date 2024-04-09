from typing import List

from pydantic import BaseModel

# https://github.com/citation-file-format/citation-file-format/issues/373
DUTCH_NAME_PARTICLES: List[str] = ['den', 'van', 'van den', 'van het',
                                   'op het', "van 't", "op 't", "v/d"]
SPANISH_NAME_PARTICLES: List[str] = ['de', 'de la']

NAME_PARTICLES: List[str] = list(
    set(DUTCH_NAME_PARTICLES + SPANISH_NAME_PARTICLES))

SPLIT_NAME_PARTICLES: List[str] = [p2 for split_particle_list in [
    p1.split(' ') for p1 in NAME_PARTICLES] for p2 in split_particle_list]

NAME_SUFFIXES: List[str] = ['jr.', 'jr', 'sr.', 'sr', 'i',
                            'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x']


class HumanName(BaseModel):
    first_name: str = ''
    middle_name: str = ''
    particle: str = ''
    last_name: str = ''
    suffix: str = ''

    @property
    def full_name(self) -> str:
        return ' '.join([self.first_name, self.middle_name, self.particle, self.last_name, self.suffix]).strip()

    @full_name.setter
    def full_name(self, full_name: str) -> None:
        name: HumanName = HumanNameParser.parse(text=full_name)
        self.first_name = name.first_name
        self.last_name = name.last_name
        self.middle_name = name.middle_name
        self.particle = name.particle
        self.suffix = name.suffix


class Token(BaseModel):
    tag: str
    value: str


class HumanNameParser:

    FIRST_NAME_TAG: str = 'first_name'
    MIDDLE_NAME_TAG: str = 'middle_name'
    PARTICLE_TAG: str = 'particle'
    LAST_NAME_TAG: str = 'last_name'
    SUFFIX_TAG: str = 'suffix'

    @staticmethod
    def get_tokens(text: str) -> List[Token]:
        raw_tokens: List[Token] = [Token(tag="", value=v)
                                   for v in text.strip().split(sep=' ')]

        tokens: List[Token] = []
        if len(raw_tokens):
            # find suffix
            token = raw_tokens.pop()
            if token.value.casefold() in NAME_SUFFIXES and len(raw_tokens) >= 2:
                token.tag = HumanNameParser.SUFFIX_TAG
                tokens.append(token)
            else:
                raw_tokens.append(token)

            has_last_name: bool = False
            while (True):
                token = raw_tokens.pop()
                if len(raw_tokens) == 0:
                    token.tag = HumanNameParser.FIRST_NAME_TAG
                    tokens.append(token)
                    break
                elif len(raw_tokens) == 1:
                    if has_last_name and token.value.casefold() in NAME_PARTICLES:
                        token.tag = HumanNameParser.PARTICLE_TAG
                        tokens.append(token)
                    elif has_last_name:
                        token.tag = HumanNameParser.MIDDLE_NAME_TAG
                        tokens.append(token)
                    else:
                        token.tag = HumanNameParser.LAST_NAME_TAG
                        has_last_name = True
                        tokens.append(token)
                else:
                    if has_last_name and token.value.casefold() in NAME_PARTICLES:
                        token.tag = HumanNameParser.PARTICLE_TAG
                        tokens.append(token)
                    else:
                        # we have at least 2 extra raw tokens

                        # see if the token is the first part of a particle with 2 words
                        # currently this algorithm only handles particles with at most 2 words
                        next_token = raw_tokens.pop()
                        possible_two_word_particle = ' '.join(
                            [next_token.value, token.value]).casefold()
                        if has_last_name and possible_two_word_particle in NAME_PARTICLES:
                            token = Token(
                                tag=HumanNameParser.PARTICLE_TAG, value=possible_two_word_particle)
                            tokens.append(token)
                        elif has_last_name is False:
                            raw_tokens.append(next_token)
                            token.tag = HumanNameParser.LAST_NAME_TAG
                            has_last_name = True
                            tokens.append(token)
                        else:
                            raw_tokens.append(next_token)

                            # it is either a middle name token or a n-ary last name token
                            # but we will assume it is a middle name token for now
                            token.tag = HumanNameParser.MIDDLE_NAME_TAG

                            # merge middle name with previous token if necessary
                            previous_token = tokens.pop()
                            if previous_token.tag == HumanNameParser.MIDDLE_NAME_TAG:
                                token.value = token.value + previous_token.value
                            else:
                                tokens.append(previous_token)

                            # append middle name token
                            tokens.append(token)

            # reverse the tokens so the are in the correct order
            tokens.reverse()
            return tokens
        else:
            return []

    @staticmethod
    def parse(text: str) -> HumanName:

        human_name = HumanName()

        tokens: List[Token] = HumanNameParser.get_tokens(text=text)

        for token in tokens:
            if token.tag == HumanNameParser.FIRST_NAME_TAG:
                human_name.first_name += ' ' + token.value
            elif token.tag == HumanNameParser.MIDDLE_NAME_TAG:
                human_name.middle_name += ' ' + token.value
            elif token.tag == HumanNameParser.PARTICLE_TAG:
                human_name.particle += ' ' + token.value
            elif token.tag == HumanNameParser.LAST_NAME_TAG:
                human_name.last_name += ' ' + token.value
            elif token.tag == HumanNameParser.SUFFIX_TAG:
                human_name.suffix += ' ' + token.value

        human_name.first_name = human_name.first_name.strip()
        human_name.middle_name = human_name.middle_name.strip()
        human_name.particle = human_name.particle.strip()
        human_name.last_name = human_name.last_name.strip()
        human_name.suffix = human_name.suffix.strip()

        return human_name
