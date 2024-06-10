from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from django.contrib import messages
import random

import markdown2

from . import util

class new_entry_form(forms.Form):
    title = forms.CharField(label="Title", max_length=100,
                            widget=forms.TextInput(
                            attrs={'class': "form-control"}))

    content = forms.CharField(label="Content",
                            widget=forms.Textarea(
                            attrs={'class': "form-control"}))

class new_content_form(forms.Form):
    content = forms.CharField(label="Content",
                            widget=forms.Textarea(
                            attrs={'class': "form-control"}))

def filter_list(string_list, target):
    filtered_list = []
    for string in string_list:
        if target.lower() in string.lower():
            filtered_list.append(string)
    return filtered_list

def index(request):
    if request.method == "POST":
        form = forms.Form(request.POST)
        return render(request, "encyclopedia/index.html", {
            "title": "Pages Including \"" + form.data["q"]+"\"",
            "entries": filter_list(util.list_entries(), form.data["q"])
        })
    else:
        return render(request, "encyclopedia/index.html", {
            "title": "All Pages",
            "entries": util.list_entries()
        })


def new(request):
    if request.method == "POST":
        form = new_entry_form(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            if util.get_entry(title):
                messages.info(request, 'This page already exists!')
                return render(request, "encyclopedia/new.html", {
                    "form": form
                })
            else:
                util.save_entry(title, form.cleaned_data["content"])
                return HttpResponseRedirect(reverse("wiki:index") + title)
        else:
            return render(request, "encyclopedia/new.html", {
                "form": form
            })
    else:
        return render(request, "encyclopedia/new.html", {
            "form": new_entry_form()
        })

def edit(request):
    if request.method == "POST":
        form = new_content_form(request.POST)
        if form.data["first"] == "True":
            return render(request, "encyclopedia/edit.html", {
                "title": form.data["title"],
                "form": form
            })
        else:
            if form.is_valid():
                title = form.data["title"]
                util.save_entry(title, form.cleaned_data["content"])
                return HttpResponseRedirect(reverse("wiki:index") + title)
            else:
                return render(request, "encyclopedia/edit.html", {
                    "title": form.data["title"],
                    "form": form
                })
    else:
        return render(request, "encyclopedia/new.html", {
            "form": new_content_form()
        })

def entry(request, name):
    page_content = util.get_entry(name)
    if page_content == None:
            return render(request, "encyclopedia/error.html", {
            "title": name
        })

    return render(request, "encyclopedia/entry.html", {
        "title" : name,
        "content" : markdown2.markdown(page_content),
        "raw_content": page_content
    })

def random_entry(request):
    return entry(request, random.choice(util.list_entries()))