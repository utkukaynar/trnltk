import logging
from trnltk.parser import formatter
from trnltk.phonetics.phonetics import Phonetics
from trnltk.parser.token import SuffixFormApplication
from trnltk.suffixgraph.suffixgraphmodel import State

logger = logging.getLogger('suffixapplier')

def try_suffix(token, suffix, to_state, word):

    if not transition_allowed_for_suffix(token, suffix):
        return None

    new_candidates = []

    logger.debug('    Gonna try %d suffix forms : "%s"', len(suffix.suffix_forms), suffix.suffix_forms)
    for suffix_form in suffix.suffix_forms:
        logger.debug('     Gonna try suffix form "%s".', suffix_form)

        new_token = try_suffix_form(token, suffix_form, to_state, word)
        if new_token:
            new_candidates.append(new_token)

    return new_candidates

def transition_allowed_for_suffix(token, suffix):
    if suffix.group and suffix.group in token.get_suffix_groups_since_last_derivation():
        logger.debug('    Another suffix is already added on the same group(%s) since last derivation, skipping suffix.', suffix.group)
        logger.debug('    Groups since last derivation are : %s', token.get_suffix_groups_since_last_derivation())
        return False

    if not suffix.allow_repetition and token.get_last_derivation_suffix() and token.get_last_derivation_suffix()==suffix:
        logger.debug('    The last derivation suffix is same with the suffix, skipping.')
        return False

    return True

def try_suffix_form(token, suffix_form, to_state, word):
    state_before_suffix_form_application = token.get_last_state()

    if not transition_allowed_for_suffix_form(token, suffix_form):
        return None

    so_far = token.get_so_far()
    token_root_attributes = token.get_attributes()

    token_phonetic_attributes = token.get_phonetic_attributes()

    modified_word, applied_suffix_form = Phonetics.apply(so_far, token_phonetic_attributes, suffix_form.form, token_root_attributes)
    applied_str =  modified_word + applied_suffix_form
    if Phonetics.application_matches(word, applied_str, to_state.name!='VERB_ROOT'):
        actual_suffix_form_str = word[len(so_far):len(applied_str)]
        fitting_suffix_form = applied_suffix_form
        logger.debug('      Word "%s" starts with applied str "%s" (%s), adding to current token', word, applied_str, actual_suffix_form_str)
        clone = token.clone()
        clone.add_transition(SuffixFormApplication(suffix_form, actual_suffix_form_str, fitting_suffix_form), to_state)

        if token.has_transitions() and token.get_last_transition().suffix_form_application.suffix_form.postcondition and not token.get_last_transition().suffix_form_application.suffix_form.postcondition.is_satisfied_by(clone):
            logger.debug('      Suffix does not satisfy the postcondition "%s" of last transition suffix form "%s", skipping.', token.get_last_transition().suffix_form_application.suffix_form.postcondition, formatter.format_transition(clone.get_last_transition()))
            return None

        if token.has_transitions() and state_before_suffix_form_application.type==State.DERIV:
            logger.debug('      Suffix is derivative, checking the post derivation conditions of suffixes from previous derivation.')
            for transition in token.get_transitions_from_derivation_suffix():
                application_suffix_form = transition.suffix_form_application.suffix_form
                if application_suffix_form.post_derivation_condition:
                    matches = application_suffix_form.post_derivation_condition.is_satisfied_by(clone)
                    if not matches:
                        logger.debug('      Post derivation condition "%s" of suffix "%s" is not satisfied, skipping.', application_suffix_form.post_derivation_condition, application_suffix_form.suffix)
                        return None

        return clone

    else:
        logger.debug('      Word "%s" does not start with applied str "%s" (%s), skipping', word, applied_str, applied_str)
        return None

def transition_allowed_for_suffix_form(token, suffix_form):
    if suffix_form.precondition and not suffix_form.precondition.is_satisfied_by(token):
        logger.debug('      Precondition "%s" of suffix form "%s" is not satisfied with transitions %s, skipping.', suffix_form.form, suffix_form.precondition, token)
        return False

    if suffix_form.form and not Phonetics.expectations_satisfied(token.get_phonetic_expectations(), suffix_form.form):
        logger.debug('      Suffix form "%s" does not satisfy phonetic expectations %s, skipping.', suffix_form.form, token.get_phonetic_expectations())
        return False

    if not Phonetics.is_suffix_form_applicable(token.get_so_far(), suffix_form.form):
        logger.debug('      Suffix form "%s" is not phonetically applicable to "%s", skipping.', suffix_form.form, token.get_so_far())
        return False

    return True