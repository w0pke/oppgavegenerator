from django.http import HttpResponse
from oppgavegen.models import Level, Template, Set, Chapter
from datetime import datetime


def new_chapter(chapter_name, user):
    chapter = Chapter(name=chapter_name, creator=user, creation_date=datetime.now())
    chapter.save()
    return chapter


def new_level(level_name, user):
    level = Level(name=level_name, user=user, creation_date=datetime.now())
    level.save()
    return level


def new_set(set_name, user):
    set = Set(name=set_name, user=user, creation_date=datetime.now())
    set.save()
    return set


def remove_chapter(chapter_id, user):
    chapter = Chapter.objects.get(pk=chapter_id)
    success_string = 'Failed to delete chapter ' + chapter.name + '.'
    if chapter.creator == user:
        success_string = 'Chapter sucessfully deleted' + chapter.name + '.'
        chapter.delete()
    return success_string


def remove_level(level_id, user):
    level = Level.objects.get(pk=level_id)
    success_string = 'Failed to delete chapter ' + level.name + '.'
    if level.creator == user:
        success_string = 'Chapter sucessfully deleted' + level.name + '.'
        level.delete()
    return success_string

def remove_from_set(set_id, chapter_id, user):
    set = Set.objects.get(pk=set_id)
    chapter = Chapter.objects.get(pk=chapter_id)
    success_message = 'Failed to remove ' + chapter.name + ' from set.'
    if user == set.creator:
        set.chapters.remove(chapter)
        order = set.order.split(',')
        order.remove(chapter_id)
        order = ','.join(order)
        set.order = order
        set.save()
        success_message = 'successfully removed ' + chapter.name + ' from set.'

    return success_message




def remove_set(set_id, user):
    set = Set.objects.get(pk=set_id)
    success_string = 'Failed to delete chapter ' + set.name + '.'
    if set.creator == user:
        success_string = 'Chapter sucessfully deleted' + set.name + '.'
        set.delete()
    return success_string

def add_template_to_level(template, level):
    level.levels.add(template)
    level.save()


def add_level_to_chapter(level, chapter):
    add_to_level_order = ''
    if chapter.order != '':
        add_to_level_order = ','
    chapter.order += add_to_level_order + str(level.pk)
    chapter.levels.add(level)
    chapter.save()


def add_chapter_to_set(chapter, set):
    add_to_level_order = ''
    if set.order != '':
        add_to_level_order = ','
    set.order += add_to_level_order + str(chapter.pk)
    set.chapters.add(chapter)
    set.save()