from django.views.generic import ListView
from datetime import datetime

from events.models import Event


class HomeView(ListView):
	model = Event
	template_name = "home.html"
	context_object_name = 'events'
	paginate_by = 10

	def get_queryset(self):
		return Event.objects.filter(date__gt=datetime.today()).order_by('time')

	def get_context_data(self, **kwargs):
		context = super(HomeView, self).get_context_data(**kwargs)
		return context
