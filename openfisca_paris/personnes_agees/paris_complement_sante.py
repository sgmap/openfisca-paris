# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore


class paris_complement_sante_pa_eligibilite(Variable):
	value_type = bool
	entity = Famille
	definition_period = MONTH
	label = u"Éligibilité au Complément Santé Paris pour les personnes âgées"
	reference = "Article II.1.2.b.3 du règlement municipal du CASVP"

	def formula(famille, period, parameters):
		
		personne_agee = famille.members('paris_personne_agee', period)
		personnes_agees = famille.any(personne_agee)

		base_ressources = famille('paris_base_ressources_couple', period.last_month)
		param_plafond = parameters(period).paris.personnes_agees.paris_complement_sante.plafond
		en_couple = famille('en_couple', period)
		plafond = where(en_couple, param_plafond.en_couple, param_plafond.personne_isolee)
		css = famille('cmu_acs_eligibilite', period)

		return personnes_agees * (base_ressources <= plafond) * not_(css)


class paris_complement_sante_pa_montant(Variable):
	value_type = float
	entity = Famille
	definition_period = MONTH
	label = u"Montant du Complément Santé Paris pour les personnes âgées"
	reference = "Articles II.1.2.a.2 & II.1.2.b.6 du règlement municipal du CASVP"

	def formula(famille, period, parameters):
		
		montant = parameters(period).paris.personnes_agees.paris_complement_sante.montant
		acs = famille('acs', period)
		cmu_c = famille('cmu_c', period)

		return not_(cmu_c) * max_(montant - acs, 0)


class paris_complement_sante_pa(Variable):
	value_type = float
	entity = Famille
	definition_period = MONTH
	label = u"Complément Santé Paris pour les personnes âgées"
	reference = "Article II.1.2 du règlement municipal du CASVP"

	def formula(famille, period, parameters):

		eligibilite = famille('paris_complement_sante_pa_eligibilite', period)
		montant = famille('paris_complement_sante_pa_montant', period)
		
		return eligibilite * montant
