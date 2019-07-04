from django.shortcuts import render

# Create your views here.
from django.views import View

from research.parsers import Parser


class GameView(View):
    def get(self, request, research_id, game_id):
        path = 'media/game_extracted/{research_id}/{game_id}/exp.txt'.format(research_id=str(research_id), game_id=str(game_id))
        data = Parser(path)
        context = {'data': data.parsed_dict}
        return render(request, template_name='game/game.html', context=context)
