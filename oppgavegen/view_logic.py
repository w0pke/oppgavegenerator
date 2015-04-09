from oppgavegen.models import Template
from oppgavegen.models import Topic
from oppgavegen import generation
from datetime import datetime

def make_edit_context_dict(template_id):
    q = Template.objects.get(pk=template_id)
    calculation_references = q.calculation_ref
    question_text = q.question_text_latex
    solution = q.solution_latex
    answer = q.answer_latex
    choices = q.choices_latex
    conditions = q.conditions_latex
    fill_in = q.fill_in_latex
    topic = q.topic
    random_domain = q.random_domain
    unchanged_ref = q.unchanged_ref
    topics = ""
    for e in Topic.objects.all():
        topics += '§' + str(e.pk) + '§'
        topics += e.topic
    topics = topics[1:]
    context_dict = {'template_id': template_id , 'answer' : answer, 'solution' : solution,
                    'question_text' : question_text, 'calculation_references' : calculation_references,
                    'choices' : choices, 'conditions' : conditions, 'fill_in' : fill_in,
                    'topic' : topic, 'random_domain' : random_domain, 'unchanged_ref' : unchanged_ref,
                    'topics' : topics}
    return context_dict


def make_answer_context_dict(form_values):
    user_answer = form_values['user_answer']
    template_type = form_values['template_type']
    template_specific = form_values['template_specific']
    q = Template.objects.get(pk=form_values['primary_key'])
    variable_dictionary = form_values['variable_dictionary'].split('§')

    if template_type != 'blanks':
        answer = generation.replace_variables_from_array(variable_dictionary, q.answer.replace('\\\\', '\\'))
    else:
        answer = generation.get_values_from_position(template_specific, q.solution.replace('\\\\', '\\'))
        answer = generation.replace_variables_from_array(variable_dictionary, answer)
    answer = generation.parse_answer(answer)
    answer = answer.replace('`', '')
    answer = answer.split('§')
    solution = str((q.question_text).replace('\\\\', '\\')) + "\\n" + str(q.solution.replace('\\\\', '\\'))
    solution = generation.replace_variables_from_array(variable_dictionary, solution)
    solution = generation.parse_solution(solution)

    # print(solution)
    user_answer = user_answer.split(
        '§')  #if a string doesn't contain the split character it returns as a list with 1 element
    #print(user_answer)
    #We format both the user answer and the answer the same way.
    user_answer = [generation.after_equal_sign(x) for x in user_answer]
    user_answer = generation.calculate_array(user_answer)
    answer = [generation.after_equal_sign(x) for x in answer]
    answer = generation.calculate_array(answer)

    answer_text = generation.checkAnswer(user_answer, answer)
    context_dict = {'title': "Oppgavegen", 'answer': str(answer_text), 'user_answer': user_answer, 'solution': solution}
    return context_dict



def submit_template(template, user):
    if template.pk != '':
        q = Template.object.get(pk=template.pk)
        template.rating = q.rating
        template.times_failed = q.times_failed
        template.times_solved = q.times_solved
        template.creation_date = q.creation_date
        template.creator = q.creator
    else:
        template.rating = 1200
        template.times_failed = 0
        template.times_solved = 0
        template.creation_date = datetime.now()
        template.creator = user
    template.save()
    return

def change_elo(template_id, user, winner, type):
    if winner == user: #todo make this class properly.
        user.rating += 10
        template_id.rating -= 10
    else:
        user.rating -= 10
        template_id.rating += 10

    return