# -*- coding: utf-8 -*-

# Import from openfisca-core the common python objects used to code the legislation in OpenFisca
from openfisca_core.model_api import *
# Import the entities specifically defined for this tax and benefit system
from openfisca_aotearoa.entities import Titled_Property, Person, Family
from numpy import clip, floor

class social_security__received_income_tested_benefit(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = u'Boolean for if a Person is classified as receiving an income tested benefit'
    reference = "http://www.legislation.govt.nz/act/public/2007/0097/latest/whole.html#DLM1518484"

class veterans_support__received_parents_allowance(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = u'Boolean for if a Person is classified as receiving a parents allowance'
    reference = "http://www.legislation.govt.nz/act/public/2007/0097/latest/whole.html#DLM1518484"

class veterans_support__received_childrens_pension(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = u'Boolean for if a Person is classified as receiving a parents allowance'
    reference = "http://www.legislation.govt.nz/act/public/2007/0097/latest/whole.html#DLM1518484"

class income_tax__resident(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = u'Boolean for if a Person is classified as meeting residence requirements'
    reference = "http://www.legislation.govt.nz/act/public/2007/0097/latest/DLM1518482.html"
    # This should really be a forumla based variable covering the full residency criteria.


class income_tax__dependant(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = u'Boolean for if a Person is classified as financially dependant'
    reference = "http://www.legislation.govt.nz/act/public/2007/0097/latest/whole.html#DLM1520883"

    def formula(person, period, parameters):
        age = person('age', period)
        return age <= 18 
        # TODO - It's not this simple, this needs to be tweaked to include the edge criteria.

class income_tax__income(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        label = u'The annual income for a Person in a Family.'
        reference = "" # TODO Add


class income_tax__eligible_for_working_for_families(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = u'Boolean for if a Person is classified as eligible for working for families tax credits'    
    reference = "http://www.legislation.govt.nz/act/public/2007/0097/latest/DLM1518477.html"

    def formula(person, period, parameters):
        received_tested_benefit     = person('social_security__received_income_tested_benefit', period)
        received_parents_allowance  = person('veterans_support__received_parents_allowance', period)
        received_childrens_pension  = person('veterans_support__received_childrens_pension', period)     

        return not_(received_tested_benefit) * not_(received_parents_allowance) * not_(received_childrens_pension)
        # TODO - Add remaining eligibility criteria as per legislation.

class income_tax__eligible_for_best_start_tax_credit(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = u'Boolean for if a Person is classified as eligible for best start tax credit'
    reference = "http://legislation.govt.nz/bill/government/2017/0004/15.0/DLM7512349.html"

    def formula(person, period, parameters):
        
        return True 
        # TODO - Base eligibility of ages of children as per legislation.


class income_tax__entitlement_for_best_start_tax_credit(Variable):
    value_type = float
    entity = Family
    definition_period = MONTH
    label = u'Value of a Families entitlement for best start tax credit'
    reference = "http://legislation.govt.nz/bill/government/2017/0004/15.0/DLM7512349.html"

    def formula(family, period, parameters):

                # sum up families income
                family_income   = family.sum(family.members('income_tax__income', period.this_year))

                # calculate income over the threshold
                income_over_threshold = where((family_income - 79000) < 0, 0, family_income - 79000)

                # work out the ages for each family member
                ages = family.members('age', period)

                # work out if each dependant child is eligible for full best start tax credit
                dependant_eligible_full = ages == 0

                # work out if each dependant child is eligible for abated best start tax credit
                dependant_eligible_abated_1 = ages == 1
                dependant_eligible_abated_2 = ages == 2

                # sum up the entitlement for each child
                bstc_entitlement = family.sum(dependant_eligible_full * 3120  
                + dependant_eligible_abated_1 * (3120 - (income_over_threshold * .21))
                + dependant_eligible_abated_2 * (3120 - (income_over_threshold * .21)))

                return bstc_entitlement
                # TODO - Replace hardcoded values with parameters already created.