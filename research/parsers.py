import os
import shlex


class Parser():
    def __init__(self, path):
        self.path = path  # exp 파일의 absolute path
        self.dirname = os.path.dirname(path)  # exp 파일의 경로
        self.exp_string_list = None  # 읽어들인 파일을 line별로 임시 저장하는 list
        self.sectioned_string = {
            # 읽어들인 파일을 임시로 저장하는 dictionary
            "stimulus": [],
            "sequences": {
                "pre_sequence": None,
                "main_sequence": None,
                "post_sequence": None
            }
        }
        self.parsed_dict = {
            # 최정 파싱된 정보를 저장하는 dictionary
            "version": 1,
            "stimulus": [],
            "sequences": {
                "pre_sequence": None,
                "main_sequence": None,
                "post_sequence": None
            }
        }
        self.errors = None
        try:
            self.read_file()  # 파일 읽기 및 line별 분리
            self.split_section()  # 파일 섹션별로 분리
            self.parse_stimulus()
            self.parse_sequence()
        except:
            self.parse_result = False
            self.errors = True
        else:
            self.parse_result = True

    def read_file(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                exp_string = f.read()
        except:
            raise IOError('파일 로딩 실패')
        else:
            self.exp_string_list = [line.strip() for line in exp_string.split('\n')]

    def parse_stimulus(self):
        stimulus_list = {}
        for idx, _stimulus in enumerate(self.sectioned_string['stimulus']):
            stimulus = {'type': None, 'body': None, 'font_size': None, 'font_color': None}
            splitted_stimulus = shlex.split(_stimulus, ' ')
            stimulus['type'] = splitted_stimulus[0]
            if stimulus['type'] in ['text', 'text_file']:
                try:
                    stimulus['font_size'] = None if splitted_stimulus[3] == 'n' else splitted_stimulus[3]
                except:
                    stimulus['font_size'] = None
                try:
                    stimulus['font_color'] = None if splitted_stimulus[4] == 'n' else splitted_stimulus[4]
                except:
                    stimulus['font_color'] = None
                if stimulus['type'] == 'text_file':
                    stimulus['type'] = 'text'
                    with open(os.path.join(self.dirname, splitted_stimulus[2]), 'r') as text_file:
                        stimulus['body'] = ''.join(line.replace('\n', ' ') for line in text_file.readlines())
                else:
                    stimulus['body'] = splitted_stimulus[2]
            else:
                stimulus['body'] = splitted_stimulus[2]
            stimulus_list.update({splitted_stimulus[1]: stimulus})
        self.parsed_dict['stimulus'] = stimulus_list

    def json(self):
        import json
        if self.parse_result:
            return json.dumps(self.parsed_dict, ensure_ascii=False)
        else:
            raise Exception('올바르게 파싱되지 않았습니다.')

    def split_section(self):
        """
        주어진 text 파일을 description, preseq, mainseq, postseq, end 영역으로 구분하여
        self.sectioned_string에 딕셔너리 형태로 저장
        """
        def split(keyword, exp_string_list):
            first = next((idx for idx, string in enumerate(exp_string_list) if string == '[{}]'.format(keyword)))
            end = next((idx for idx, string in enumerate(exp_string_list) if string == '[End{}]'.format(keyword)))
            return exp_string_list[first+1:end]

        self.sectioned_string['stimulus'] = split('Descriptions', self.exp_string_list)
        self.sectioned_string['sequences']['pre_sequence'] = split('PreSeq', self.exp_string_list)
        self.sectioned_string['sequences']['main_sequence'] = split('MainSeq', self.exp_string_list)
        self.sectioned_string['sequences']['post_sequence'] = split('PostSeq', self.exp_string_list)

    def parse_sequence(self):
        sequence_type_list = ['pre_sequence', 'main_sequence', 'post_sequence']
        # sequence_type_dict = {'preseq': 'pre_sequence', 'mainseq': 'main_sequence', 'postseq': 'post_sequence'}
        for type_str in sequence_type_list:
            _temp_sequence_list = self.sectioned_string['sequences'].get(type_str)
            sequence_list = []
            if _temp_sequence_list is not None:
                for _temp_sequence in _temp_sequence_list:
                    sequence = {'onSetTime': None, 'identifier': None, 'stimulus': None, 'stimulus_duration': None, 'choices': None, 'choice_duration': None,
                                'answer': None, 'choiceOnsetRelativeToSim': None, 'reaction_time': None, 'feedback_type': None,
                                'feedback_duration': None, 'feedback_1': None, 'feedback_2': None, 'test': None}
                    splitted_sequence = shlex.split(_temp_sequence, ' ')
                    temp_choice_list = splitted_sequence[3].split(',')
                    sequence['onSetTime'] = splitted_sequence[0]
                    sequence['stimulus'] = self.parsed_dict['stimulus'][splitted_sequence[1]]
                    sequence['stimulus_duration'] = None if splitted_sequence[2] == 'inf' else int(splitted_sequence[2])
                    sequence['choices'] = None if splitted_sequence[3] == 'n' else [self.parsed_dict['stimulus'][key] for key in temp_choice_list]
                    sequence['choice_duration'] = None if splitted_sequence[4] == 'inf' else int(splitted_sequence[4])

                    sequence['answer'] = None if splitted_sequence[5] == 'n' else self.parsed_dict['stimulus'][temp_choice_list[int(splitted_sequence[5])]]
                    sequence['answer_identifier'] = None if splitted_sequence[5] == 'n' else int(splitted_sequence[5])

                    sequence['choiceOnsetRelativeToSim'] = None if splitted_sequence[6] == 'n' else splitted_sequence[6]
                    sequence['reaction_time'] = None if splitted_sequence[7] == 'inf' else int(splitted_sequence[7])
                    sequence['feedback_type'] = splitted_sequence[8]
                    sequence['feedback_duration'] = None if splitted_sequence[9] == 'n' else int(splitted_sequence[9])
                    sequence['feedback_1'] = None if splitted_sequence[10] == 'n' else self.parsed_dict['stimulus'].get(splitted_sequence[10])
                    sequence['feedback_2'] = None if splitted_sequence[11] == 'n' else self.parsed_dict['stimulus'].get(splitted_sequence[11])
                    sequence['test'] = False if splitted_sequence[12] == 'n' else False
                    sequence_list.append(sequence)
                self.parsed_dict['sequences'].update({type_str: sequence_list})

