from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View

from actions.utils import create_action
from comments.models import Comment
from comments.forms import CommentForm

from .models import Event


# Create your views here.


class EventList(generic.ListView):
    model = Event
    template_name = 'events/list_of_events.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        return Event.objects.all()


class EventDisplay(generic.DetailView):
    model = Event
    template_name = 'events/detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.get_object().comments.all()
        return context


class CommentCreate(SuccessMessageMixin, generic.CreateView):
    model = Comment
    template_name = 'events/detail.html'
    fields = ('comment',)
    success_message = 'Comment was added successfully'

    def form_valid(self, form):
        form.instance = form.save(commit=False)
        form.instance.event = self.get_object(queryset=Event.objects.all())
        form.instance.created_by = self.request.user
        create_action(self.request.user, 'added a comment', form.instance)
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('events:event-detail', kwargs={'pk': self.get_object(Event.objects.all()).pk})


class EventDetail(AccessMixin, View):

    def get(self, request, *args, **kwargs):
        view = EventDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        view = CommentCreate.as_view()
        return view(request, *args, **kwargs)


class EventFormMixin(object):
    def form_valid(self, form):
        form.instance.creator = self.request.user
        create_action(self.request.user, 'created a new event', form.instance)
        return super().form_valid(form)


class EventCreate(LoginRequiredMixin, SuccessMessageMixin, EventFormMixin, generic.CreateView):
    model = Event
    template_name = 'events/create_form.html'
    fields = ('category', 'name', 'details', 'venue', 'time', 'date')
    context_object_name = 'event'
    success_message = "%(name)s was created successfully"


class EventUpdate(LoginRequiredMixin, SuccessMessageMixin, EventFormMixin, generic.UpdateView):
    model = Event
    template_name = 'events/update_form.html'
    template_name_suffix = '_update_form'
    fields = ('category', 'name', 'details', 'venue', 'time', 'date',)
    success_message = "%(name)s was updated successfully"


class EventDelete(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    model = Event
    template_name = 'events/delete.html'
    success_url = reverse_lazy('events:event-list')
    context_object_name = 'event'
    success_message = "%(name)s was deleted successfully"


