"""

makes context dictionary for submit, edit and answer view.

"""
from datetime import datetime
import json

from oppgavegen.models import Template, Tag
from oppgavegen.parsing.parenthesis_removal import *
from oppgavegen.view_logic.answer_checker import check_answer
from oppgavegen.generation_folder.calculate_parse_solution import parse_solution, parse_answer
from oppgavegen.generation_folder.fill_in import get_fillin_answers
from oppgavegen.utility.utility import after_equal_sign, replace_words, replace_variables_from_array
from oppgavegen.generation_folder.template_validation import template_validation


def make_edit_context_dict(template_id):
    """Returns context dict for use on the edit page"""
    templatetags = []
    q = Template.objects.get(pk=template_id)
    for t in q.tags.all():
        templatetags.append(t.name)
    calculation_references = q.calculation_ref
    question_text = q.question_text_latex
    solution = q.solution_latex
    answer = q.answer_latex
    choices = q.choices_latex
    conditions = q.conditions_latex
    fill_in = q.fill_in_latex
    random_domain = q.random_domain
    unchanged_ref = q.unchanged_ref
    dictionary = q.dictionary
    used_variables = q.used_variables
    tags = json.dumps(templatetags)
    difficulty_m = q.difficulty_multiple
    difficulty_b = q.difficulty_blanks
    name = q.name
    unchanged_required = q.unchanged_required
    unchanged_disallowed = q.unchanged_disallowed

    if unchanged_required == '' or unchanged_required == None:
        unchanged_required = []
    if unchanged_disallowed == '' or unchanged_disallowed == None:
        unchanged_disallowed = []

    context_dict = {'template_id': template_id, 'answer': answer, 'solution': solution,
                    'question_text': question_text, 'calculation_references': calculation_references,
                    'choices': choices, 'conditions': conditions, 'fill_in': fill_in,
                    'random_domain': random_domain, 'unchanged_ref': unchanged_ref,
                    'dictionary': dictionary, 'used_variables': used_variables,
                    'tags': tags, 'margin_of_error': q.margin_of_error, 'disallowed': q.disallowed,
                    'required': q.required, 'difficulty': q.difficulty, 'difficulty_blanks': difficulty_b,
                    'difficulty_multiple': difficulty_m, 'name': name, 'unchanged_disallowed': unchanged_disallowed,
                    'unchanged_required': unchanged_required, 'graph': q.unchanged_graph,
                    'graph_settings': q.graph_settings, 'graph_color': q.graph_color}
    return context_dict


def make_answer_context_dict(form_values):
    """Returns context dict for use on the answer page"""
    user_answer = form_values['user_answer']
    user_answer = user_answer.replace(',','.')
    user_answer = user_answer.replace('..', ',')  # A cheeky way to circumvent removal of ','
    template_type = form_values['template_type']
    template_specific = form_values['template_specific']
    q = Template.objects.get(pk=form_values['primary_key'])
    variable_dictionary = form_values['variable_dictionary'].split('§')
    replacing_words = form_values['replacing_words']
    random_domain = q.random_domain

    if template_type != 'blanks':
        answer = q.answer.replace('\\\\', '\\')
        answer = answer.replace('(', '+parenthesisleft+')  # Done to preserve original parenthesis
        answer = answer.replace(')', '+parenthesisright+')  # Done to preserve original parenthesis
        answer = replace_variables_from_array(variable_dictionary, answer)
        #answer = add_phantom_minus(answer)
    else:
        #answer = get_values_from_position(template_specific, q.solution.replace('\\\\', '\\'))
        answer = get_fillin_answers(q.fill_in.replace('\\\\', '\\'))
        answer = answer.replace('(', '+parenthesisleft+')  # Done to preserve original parenthesis
        answer = answer.replace(')', '+parenthesisright+')  # Done to preserve original parenthesis
        answer = replace_variables_from_array(variable_dictionary, answer)

    original_user_answer = user_answer.replace('§', '\\text{ og }')
    #answer = remove_pm_and_add_parenthesis(answer) # Replace with new parenthesis parsing
    answer = parse_answer(answer, random_domain)
    answer = parenthesis_removal(answer)
    answer = answer.replace('`', '')
    answer = answer.split('§')
    solution = str(q.question_text.replace('\\\\', '\\')) + "§" + str(q.solution.replace('\\\\', '\\'))
    #solution = add_phantom_minus(solution)
    solution = solution.replace('(', '+parenthesisleft+')  # Done to preserve original parenthesis
    solution = solution.replace(')', '+parenthesisright+')  # Done to preserve original parenthesis
    solution = replace_variables_from_array(variable_dictionary, solution)
    #solution = remove_pm_and_add_parenthesis(solution)
    solution = parse_solution(solution, random_domain)
    solution = parenthesis_removal(solution)
    if len(replacing_words) > 0:
        solution = replace_words(solution, replacing_words)['sentence']
    user_answer = user_answer.split('§')  # If a string doesn't contain the character it returns a list with 1 element
    # We format both the user answer and the answer the same way.
    user_answer = [after_equal_sign(x) for x in user_answer]  # Only get the values after last equal sign.
    #user_answer = calculate_array(user_answer, random_domain)
    answer = [after_equal_sign(x) for x in answer]
    #answer = calculate_array(answer, random_domain)
    answer_text = "\\text{Du har svart }" + original_user_answer + \
                      "\\text{. Det er feil. Svaret er: }" + '\\text{ og }'.join(answer)

    correct_answer = check_answer(user_answer, answer, template_type, q.margin_of_error)  # Check if the user answered correctly.

    if correct_answer:
        answer_text = "\\text{Du har svart riktig!}"

    answer_text = latex_exceptions(answer_text)

    graph = q.graph
    if graph:
        graph = json.loads(graph)

    for x in range(0, len(graph)):
            graph[x] = replace_variables_from_array(variable_dictionary, graph[x])
            graph[x] = parse_solution(graph[x], q.random_domain)

    if graph != None and graph != '':  # to prevent error if none
        graph = json.dumps(graph)
    context_dict = {'title': "Oppgavegen", 'answer': str(answer_text),
                    'solution': solution, 'user_won': correct_answer, 'graph': graph,
                    'graph_color' : q.graph_color, 'graph_settings': q.graph_settings}
    return context_dict


def submit_template(template, user, update, newtags=None):
    """Submits or updates a template to the database (depending on if update is true or not)"""
    # taglist = validate_tags(template.tags)
    if update:
        q = Template.objects.get(pk=template.pk)
        template.rating = q.rating
        template.choice_rating = q.choice_rating
        template.fill_rating = q.fill_rating
        template.times_failed = q.times_failed
        template.times_solved = q.times_solved
        template.creation_date = q.creation_date
        template.creator = q.creator
        template.editor = user
        template.copy = False  # An updated template is no longer marked as a copy
        if template.name == '':
            template.name = q.name
        if template.difficulty != q.difficulty:
            template.rating = calculate_start_rating(template.difficulty)
        if template.difficulty_blanks != q.difficulty_blanks:
            template.fill_rating = calculate_start_rating(template.difficulty_blanks)
        if template.difficulty_multiple != q.difficulty_multiple:
            template.choice_rating = calculate_start_rating(template.difficulty_multiple)
    else:
        template.rating = calculate_start_rating(template.difficulty)
        template.fill_rating = calculate_start_rating(template.difficulty_blanks)
        template.choice_rating = calculate_start_rating(template.difficulty_multiple)
        template.multifill_rating = 1200
        template.times_failed = 0
        template.times_solved = 0
        template.creation_date = datetime.now()
        template.creator = user
        template.editor = user
        template.copy = False
    if len(template.fill_in) > 1:
        template.fill_in_support = True
    if len(template.choices) > 1:
        template.multiple_support = True
    template.save()
    template.tags.clear()
    template.tags = newtags
    message = template_validation(template.pk)
    return message


def calculate_start_rating(difficulty):
    return 950 + (difficulty*50)


def cheat_check(user_answer, disallowed, variables):
    """Checks whether the user has used symbols/functions that are not allowed"""
    standard_disallowed = ['int', 'test', "'", '@', '?']
    for x in disallowed:
        replaced_x = replace_variables_from_array(variables, x)
        standard_disallowed.append(parse_solution(replaced_x, ''))

    for s in standard_disallowed:
        if str(s).replace(' ', '') in str(user_answer):
            return True
    return False


def required_check(user_answer, required, variables):
    """Checks if the user answer meets the requirements set by the teacher"""
    return_value = False
    for x in range(0, len(required)):
        required[x] = replace_variables_from_array(variables, required[x])
    for s in required:
        try:
            t_s = parse_solution(s, '')
            t_s = parenthesis_removal(t_s)
            if str(t_s).replace(' ', '') in str(user_answer):
                break
            #elif parse_using_sympy(latex_to_sympy(t_s) + '+0' + '==' + latex_to_sympy(user_answer) + '+0'):
            #    break
            return_value = True

        except Exception as e:
            print('in exception ')
            print(e)
            if str(s) not in str(user_answer):
                return_value = True
                break
    return return_value


def latex_exceptions(string):
    """Replaces wrong latex with the proper one"""
    string = string.replace('\\tilde', '\\sim')
    return string


def validate_tags(tags):
    # template = Template.objects.get(pk=template_id)
    taglist = []
    for e in tags:
        if e in Tag.objects.all():
            taglist.append(e)
        else:
            tag = Tag.objects.new(name=e)
            taglist.append(tag)
    return taglist
