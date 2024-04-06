from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render, reverse, resolve_url
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from accrete.utils import save_form
from accrete.contrib import ui
from .forms import UserForm, ChangePasswordForm, ChangeEmailForm


class LoginView(views.LoginView):

    form_class = AuthenticationForm
    template_name = 'user/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        user = form.get_user()
        if user is not None and not user.is_active:
            ctx = {'to_confirm': True}
            if self.extra_context:
                self.extra_context.update(ctx)
            else:
                self.extra_context = ctx
        return super().form_invalid(form)


class LogoutView(views.LogoutView):

    def get_success_url(self):
        return resolve_url(settings.LOGIN_URL)


@login_required()
def user_detail(request):
    ctx = ui.DetailContext(
        title=_('Preferences'),
        object=request.user,
        breadcrumbs=[],
        actions=[
            ui.ClientAction(_('Edit'), url=reverse('user:edit')),
            ui.ClientAction(_('Change E-Mail'), url=reverse('user:edit_email')),
            ui.ClientAction(_('Change Password'), url=reverse('user:edit_password'))
        ]
    ).dict()
    return render(request, 'user/user_detail.html', ctx)


@login_required()
def user_edit(request):
    form = UserForm(
        initial={'language_code': request.user.language_code},
        instance=request.user
    )
    if request.method == 'POST':
        form = save_form(UserForm(request.POST, instance=request.user))
        if form.is_saved:
            return redirect('user:detail')
    ctx = ui.FormContext(
        title=_('Preferences'),
        form=form,
        form_id='form',
        actions=ui.form_actions(reverse('user:detail'))
    ).dict()
    return render(request, 'user/user_form.html', ctx)


@login_required()
def user_change_password(request):
    form = ChangePasswordForm(instance=request.user)
    if request.method == 'POST':
        form = save_form(ChangePasswordForm(request.POST, instance=request.user))
        if form.is_saved:
            update_session_auth_hash(request, form.instance)
            messages.add_message(
                request, messages.SUCCESS,
                str(_('Your password has been changed.')),
                fail_silently=True
            )
            return redirect('user:detail')
    ctx = ui.FormContext(
        title=_('Change Password'),
        form=form,
        form_id='form',
        actions=ui.form_actions(reverse('user:detail'))
    ).dict()
    return render(request, 'user/change_password.html', ctx)


@login_required()
def user_change_email(request):
    form = ChangeEmailForm(instance=request.user)
    if request.method == 'POST':
        form = save_form(ChangeEmailForm(request.POST, instance=request.user))
        if form.is_saved:
            messages.add_message(
                request, messages.SUCCESS,
                str(_('Your email address has been changed.')),
                fail_silently=True
            )
            return redirect('user:detail')

    ctx = ui.FormContext(
        title=_('Change Email'),
        form=form,
        form_id='form',
        actions=ui.form_actions(reverse('user:detail'))
    ).dict()
    return render(request, 'user/change_email.html', ctx)
