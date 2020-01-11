import argparse
import re
import sys
import pickle

from random import uniform
from collections import defaultdict



def createParser ():  # parse of args command line
    parser = argparse.ArgumentParser()
    parser.add_argument ('name_file', nargs='?')
    return parser


class Generator:
    # Словарь trigram_model для каждой пары слов содержит список пар (слово, вероятность)   
    trigram_model = dict()

    available_character_ru = re.compile('[а-яА-Я]+|[.,:?!]')
    #available_character_en = re.compile('[a-zA-z]+|[.,:?!]')  # для англоязычных текстов

    def generating_lines_text(self, file_path):
        text = open(file_path)
        # text = re.sub(r'\s+', ' ', text)  # удаляем лишние пробелы
        for line in text:
            yield line.lower()


    def generating_words(self, lines):
        for line in lines:
            for word in self.available_character_ru.findall(line):
                yield word


    def generating_trigramgrams(self, words):
        first, second = '#', '#'
        for third in words:
            yield first, second, third
            if third in '.!?':
                yield second, third, '#'
                yield third, '#', '#'
                first, second = '#', '#'
            else:
                first, second = second, third

    
    def fit(self, file_path):
        # задаем генераторы
        lines = self.generating_lines_text(file_path)
        words = self.generating_words(lines)
        trigrams = self.generating_trigramgrams(words)

        # рассчитываем биграммы и триграммы (считаем количество одинаковых пар и троек слов в тексте)
        bigram, trigram = defaultdict(lambda: 0.0), defaultdict(lambda: 0.0)

        # first, second, third = word 1, word 2, word3
        for first, second, third in trigrams:
            bigram[first, second] += 1
            trigram[first, second, third] += 1

        # вычисляем вероятность слова в зависимости от двух предыдущих
        for (first, second, third), frequency in trigram.items():
            if (first, second) in self.trigram_model:
                self.trigram_model[first, second].append((third, frequency / bigram[first, second]))
            else:
                self.trigram_model[first, second] = [(third, frequency / bigram[first, second])]


        
    def generate(self):
        # выбираем наиболее вероятные слова или знаки препинания до тех пор,
        # пока не встречаем признак начала следующей фразы (#) 
        # первое слово выбирается как наиболее вероятное для начала предложения из набора trigram_model['#', '#']

        generated_text = ''
        first, second = '#', '#'
        while True:
            first, second = second, self.next_word(self.trigram_model[first, second])
            if second == '#': 
                break
            if second in ('.!?,:') or first == '#':
                generated_text += second
            else:
                generated_text += ' ' + second

        print(generated_text.capitalize())



    def next_word(self, possible_words):
        # possible_words - последовательность возможных слов
        sum_, frequency_ = 0, 0
        for item, frequency in possible_words:
            sum_ += frequency
        rnd = uniform(0, sum_)
        for token, frequency in possible_words:
            frequency_ += frequency
            if rnd < frequency_:
                return token


    def __init__(self, text):
        self.fit(text)
        self.generate()



if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args()
    
    # if namespace.name_file:
    #     s = input('Put "t" to train model or "g" to generate text (default "t"): ')
    #     if s[0] == 'g':
    #         model = input('Enter name(file_path) of the model: ')
    #         input_file = open(model, "rb")
    #         input_model = pickle.load(input_file)
    #         print('result:')
    #         input_model.generate()

    #     else:   
    #         print ("name of file: {}".format(namespace.name_file))
    #         start_text = Generator(namespace.name_file)
    #         oup = open('generator.pkl', "wb")
    #         pickle.dump(start_text, oup, 2)
    #         print("Done!")    
    # else:
    #     print ("you didn't specify a file name")

    if namespace.name_file:
        print ("name of file: {}".format(namespace.name_file))
        start_text = Generator(namespace.name_file)
        
    else:
        print ("no file")
