# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore


class paris_complement_sante_ph_eligibilite(Variable):
	value_type = bool
	entity = Famille
	definition_period = MONTH
	label = u"Éligibilité au Complément Santé Paris pour les personnes handicapées"
	reference = "Article III.1.2.b.3 du règlement municipal du CASVP"

	def formula(famille, period, parameters):
		
		personne_handicapee = famille.members('paris_personne_handicapee', period)
		personnes_handicapees = famille.any(personne_handicapee)

		base_ressources = famille('paris_base_ressources_couple', period.last_month)

		param_plafond = parameters(period).paris.personnes_handicapees.paris_complement_sante.plafond
		en_couple = famille('en_couple', period)
		plafond_1 = where(en_couple, param_plafond.en_couple, param_plafond.personne_isolee)

		param_aah = parameters(period).prestations.minima_sociaux
		plafond_2 = param_aah.aah.montant + param_aah.caah.majoration_vie_autonome

		css = famille('cmu_acs_eligibilite', period)

		return personnes_handicapees * (base_ressources <= max_(plafond_1, plafond_2)) * not_(css)


class paris_complement_sante_ph_montant(Variable):
	value_type = float
	entity = Famille
	definition_period = MONTH
	label = u"Montant du Complément Santé Paris pour les personnes handicapées"
	reference = "Articles III.1.2.a.2 & III.1.2.b.5 du règlement municipal du CASVP"

	def formula(famille, period, parameters):
		
		montant = parameters(period).paris.personnes_handicapees.paris_complement_sante.montant
		acs = famille('acs', period)
		cmu_c = famille('cmu_c', period)

		return not_(cmu_c) * max_(montant - acs, 0)


class paris_complement_sante_ph(Variable):
	value_type = float
	entity = Famille
	definition_period = MONTH
	label = u"Complément Santé Paris pour les personnes handicapées"
	reference = "Article III.1.2 du règlement municipal du CASVP"

	def formula(famille, period, parameters):

		eligibilite = famille('paris_complement_sante_ph_eligibilite', period)
		montant = famille('paris_complement_sante_ph_montant', period)
		
		return eligibilite * montant
