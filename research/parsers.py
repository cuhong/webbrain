import os
import shlex

from django.conf import settings


class Parser():
    def __init__(self, path):
        self.path_string = path  # 반드시 absolute path
        dirname = os.path.dirname(path).replace('media/', '')
        self.path = os.path.join(settings.MEDIA_URL, dirname)
        self.exp_string_list = None
        self.sectioned_string = {
            "description": None,
            "preseq": None,
            "mainseq": None,
            "postseq": None
        }
        self.parsed_dict = {
            "description": None,
            "preseq": None,
            "mainseq": None,
            "postseq": None
        }
        self.parse_result = True
        try:
            self.read_file()  # 파일 읽기
            self.split_section()  # 파일 섹션별로 분리
            self.errors = None
            self.parse_stimulus()
            self.parse_sequence()
        except:
            self.parse_result = False

    def read_file(self):
        try:
            with open(self.path_string, 'r', encoding='utf-8') as f:
                exp_string = f.read()
        except:
            raise IOError('exp 파일을 읽기 실패')
        else:
            self.exp_string_list = [temp.strip() for temp in  exp_string.split('\n')]

    def split_section(self):
        """
        주어진 text 파일을 description, preseq, mainseq, postseq, end 영역으로 구분하여
        self.sectioned_string에 닥셔너리 형태로 저장
        """
        def split(keyword, exp_string_list=self.exp_string_list):
            first = next((idx for idx, string in enumerate(exp_string_list) if string == '[{}]'.format(keyword)))
            end = next((idx for idx, string in enumerate(exp_string_list) if string == '[End{}]'.format(keyword)))
            return exp_string_list[first+1:end]
        # section_dict = {'description': 'Descriptions', 'preseq': 'PreSeq', 'mainseq': 'MainSeq', 'postseq': 'PostSeq'}
        # for k, v in section_dict.items():
        #     self.sectioned_string[k] = split(k)
        self.sectioned_string['description'] = split('Descriptions')
        self.sectioned_string['preseq'] = split('PreSeq')
        self.sectioned_string['mainseq'] = split('MainSeq')
        self.sectioned_string['postseq'] = split('PostSeq')

    def parse_stimulus(self):
        description_list = {}
        for idx, _stimulus in enumerate(self.sectioned_string['description']):
            stimulus = {'type': None, 'indicator': None, 'body': None, 'font_size': None, 'font_color': None}
            splitted_stimulus = shlex.split(_stimulus, ' ')
            stimulus['type'] = splitted_stimulus[0]
            stimulus['indicator'] = splitted_stimulus[1]
            if stimulus['type'] in ['text', 'text_file']:
                stimulus['font_size'] = None if splitted_stimulus[3] == 'n' else splitted_stimulus[3]
                stimulus['font_color'] = None if splitted_stimulus[4] == 'n' else splitted_stimulus[4]
                stimulus['body'] = splitted_stimulus[2]
            else:
                stimulus['body'] = self.path + '/' + splitted_stimulus[2]
            description_list[splitted_stimulus[1]] = stimulus
        self.parsed_dict['description'] = description_list

    def parse_sequence(self):
        sequence_type = ['preseq', 'mainseq', 'postseq']
        for _type in sequence_type:
            _temp_list = self.sectioned_string.get(_type, None)
            if _temp_list is not None:
                sequence_list = []
                for idx, _sequence in enumerate(_temp_list):
                    sequence = {'onSetTime': None, 'identifier': None, 'stim': None, 'stimDur': None, 'choices': None, 'choiceDur': None,
                                'answer': None, 'choiceOnsetRelativeToSim': None, 'reactionTime': None, 'feed_back_type': None,
                                'feed_back_duration': None  , 'feed_back_1': None, 'feed_back_2': None, 'test': None}
                    splitted_sequence = shlex.split(_sequence, ' ')

                    sequence['onSetTime'] = splitted_sequence[0]
                    sequence['identifier'] = splitted_sequence[1]
                    sequence['stim'] = self.parsed_dict['description'][splitted_sequence[1]]
                    sequence['stimDur'] = None if splitted_sequence[2] == 'inf' else splitted_sequence[2]
                    sequence['choices'] = None if splitted_sequence[3] == 'n' else [self.parsed_dict['description'][key] for key in splitted_sequence[3].split(',')]
                    sequence['choiceDur'] = None if splitted_sequence[4] == 'inf' else splitted_sequence[4]
                    sequence['answer'] = None if splitted_sequence[5] == 'n' else self.parsed_dict['description'][splitted_sequence[5]]
                    sequence['answer_identifier'] = None if splitted_sequence[5] == 'n' else splitted_sequence[5]
                    sequence['choiceOnsetRelativeToSim'] = None if splitted_sequence[6] == 'n' else splitted_sequence[6]
                    sequence['reactionTime'] = None if splitted_sequence[7] == 'inf' else splitted_sequence[7]
                    sequence['feed_back_type'] = splitted_sequence[8]
                    sequence['feed_back_duration'] = None if splitted_sequence[9] == 'inf' else splitted_sequence[9]
                    sequence['feed_back_1'] = None if splitted_sequence[10] == 'n' else self.parsed_dict['description'][splitted_sequence[10]]
                    sequence['feed_back_2'] = None if splitted_sequence[11] == 'n' else self.parsed_dict['description'][splitted_sequence[11]]
                    sequence['test'] = True if splitted_sequence[12] == 'y' else False
                    sequence_list.append(sequence)
                self.parsed_dict[_type] = sequence_list

# p = Parser('/Users/cuhong/Desktop/dev/monet/legacy/Webrain_sample/dictator2_exp/exp.txt')
# p.parse_stimulus()
# p.parse_sequence()
