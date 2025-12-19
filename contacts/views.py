from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from main.models import Contact
from main.forms import ContactForm


def is_dean(user):
    return user.is_authenticated and user.role == 'dean'


def contacts_view(request):
    """Просмотр контактов деканата"""
    contact = Contact.get_contact()
    return render(request, 'contacts/contacts.html', {'contact': contact})


@login_required
@user_passes_test(is_dean)
def contacts_edit(request):
    """Редактирование контактов (только декан)"""
    contact = Contact.get_contact()
    
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Контакты обновлены!')
            return redirect('contacts_view')
    else:
        form = ContactForm(instance=contact)
    
    return render(request, 'contacts/contacts_edit.html', {'form': form})