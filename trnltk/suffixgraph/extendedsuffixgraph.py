# coding=utf-8
from trnltk.suffixgraph.suffixconditions import comes_after
from trnltk.suffixgraph.suffixgraph import SuffixGraph
from trnltk.suffixgraph.suffixgraphmodel import *

class ExtendedSuffixGraph(SuffixGraph):

    def __init__(self):
        SuffixGraph.__init__(self)

        self._add_states()
        self._add_suffixes()
        self._register_suffixes()

    def _add_states(self):
        SuffixGraph._add_states(self)

        self.NOUN_COPULA = State("NOUN_COPULA", 'Noun', State.DERIV)
        self.ADJECTIVE_COPULA = State("ADJECTIVE_COPULA", 'Noun', State.DERIV)
        self.ADVERB_COPULA = State("ADVERB_COPULA", 'Noun', State.DERIV)
        self.PRONOUN_COPULA = State("PRONOUN_COPULA", 'Noun', State.DERIV)

        self.VERB_COPULA_WITHOUT_TENSE = State("VERB_COPULA_WITHOUT_TENSE", 'Verb', State.TRANSFER)
        self.VERB_COPULA_WITH_TENSE = State("VERB_COPULA_WITH_TENSE", 'Verb', State.TRANSFER)

        self.ALL_STATES |= {
            self.NOUN_COPULA, self.ADJECTIVE_COPULA, self.ADVERB_COPULA, self.PRONOUN_COPULA,
            self.VERB_COPULA_WITHOUT_TENSE, self.VERB_COPULA_WITH_TENSE
        }

    def _add_suffixes(self):
        SuffixGraph._add_suffixes(self)

        FreeTransitionSuffix("Noun_Cop_Free_Transition",         self.NOUN_TERMINAL_TRANSFER,      self.NOUN_COPULA)
        FreeTransitionSuffix("Adjective_Cop_Free_Transition",    self.ADJECTIVE_TERMINAL_TRANSFER, self.ADJECTIVE_COPULA)
        FreeTransitionSuffix("Adverb_Cop_Free_Transition",       self.ADVERB_TERMINAL_TRANSFER,    self.ADVERB_COPULA)
        FreeTransitionSuffix("Pronoun_Cop_Free_Transition",      self.PRONOUN_TERMINAL_TRANSFER,   self.PRONOUN_COPULA)

        ZeroTransitionSuffix("Noun_Copula_Zero_Transition",      self.NOUN_COPULA,        self.VERB_COPULA_WITHOUT_TENSE)
        ZeroTransitionSuffix("Adjective_Copula_Zero_Transition", self.ADJECTIVE_COPULA,   self.VERB_COPULA_WITHOUT_TENSE)
        ZeroTransitionSuffix("Adverb_Copula_Zero_Transition",    self.ADVERB_COPULA,      self.VERB_COPULA_WITHOUT_TENSE)
        ZeroTransitionSuffix("Pronoun_Copula_Zero_Transition",   self.PRONOUN_COPULA,     self.VERB_COPULA_WITHOUT_TENSE)

        ############# Copula tenses
        self.Pres_Cop = Suffix("Pres_Cop", pretty_name="Pres")
        self.Narr_Cop = Suffix("Narr_Cop", pretty_name="Narr")
        self.Past_Cop = Suffix("Past_Cop", pretty_name="Past")
        self.Cond_Cop = Suffix("Cond_Cop", pretty_name="Cond")

        ############# Copula agreements
        self.Copula_Agreements_Group = SuffixGroup('Copula_Agreements_Group')
        self.A1Sg_Cop = Suffix("A1Sg_Cop", self.Copula_Agreements_Group, "A1sg")
        self.A2Sg_Cop = Suffix("A2Sg_Cop", self.Copula_Agreements_Group, "A2sg")
        self.A3Sg_Cop = Suffix("A3Sg_Cop", self.Copula_Agreements_Group, "A3sg")
        self.A1Pl_Cop = Suffix("A1Pl_Cop", self.Copula_Agreements_Group, "A1pl")
        self.A2Pl_Cop = Suffix("A2Pl_Cop", self.Copula_Agreements_Group, "A2pl")
        self.A3Pl_Cop = Suffix("A3Pl_Cop", self.Copula_Agreements_Group, "A3pl")

    def _register_suffixes(self):
        SuffixGraph._register_suffixes(self)

        self._register_copula_tenses()
        self._register_copula_agreements()


    def _register_copula_tenses(self):
        self.VERB_COPULA_WITHOUT_TENSE.add_out_suffix(self.Pres_Cop, self.VERB_COPULA_WITH_TENSE)
        self.Pres_Cop.add_suffix_form(u"")

        self.VERB_COPULA_WITHOUT_TENSE.add_out_suffix(self.Narr_Cop, self.VERB_COPULA_WITH_TENSE)
        self.Narr_Cop.add_suffix_form(u"+ymIş")

        self.VERB_COPULA_WITHOUT_TENSE.add_out_suffix(self.Past_Cop, self.VERB_COPULA_WITH_TENSE)
        self.Past_Cop.add_suffix_form(u"+ydI")

        self.VERB_COPULA_WITHOUT_TENSE.add_out_suffix(self.Cond_Cop, self.VERB_COPULA_WITH_TENSE)
        self.Cond_Cop.add_suffix_form(u"+ysA")

    def _register_copula_agreements(self):
        comes_after_cond_or_past = comes_after(self.Cond_Cop) | comes_after(self.Past_Cop)

        self.VERB_COPULA_WITH_TENSE.add_out_suffix(self.A1Sg_Cop, self.VERB_TERMINAL_TRANSFER)
        self.A1Sg_Cop.add_suffix_form("+yIm")                          # (ben) elma-yim, (ben) armud-um, elma-ymis-im
        self.A1Sg_Cop.add_suffix_form("m", comes_after_cond_or_past)   # elma-ydi-m, elma-ysa-m

        self.VERB_COPULA_WITH_TENSE.add_out_suffix(self.A2Sg_Cop, self.VERB_TERMINAL_TRANSFER)
        self.A2Sg_Cop.add_suffix_form("sIn")                           # (sen) elma-sin, (sen) armutsun, elma-ymis-sin
        self.A2Sg_Cop.add_suffix_form("n", comes_after_cond_or_past)   # elma-ydi-n, elma-ysa-n

        self.VERB_COPULA_WITH_TENSE.add_out_suffix(self.A3Sg_Cop, self.VERB_TERMINAL_TRANSFER)
        self.A3Sg_Cop.add_suffix_form("")                              # (o) elma(dir), (o) armut(tur), elma-ymis, elma-ysa, elma-ydi

        self.VERB_COPULA_WITH_TENSE.add_out_suffix(self.A1Pl_Cop, self.VERB_TERMINAL_TRANSFER)
        self.A1Pl_Cop.add_suffix_form("+yIz")                          # (biz) elma-yiz, (biz) armud-uz, elma-ymis-iz
        self.A1Pl_Cop.add_suffix_form("k", comes_after_cond_or_past)   # elma-ydi-k, elma-ysa-k

        self.VERB_COPULA_WITH_TENSE.add_out_suffix(self.A2Pl_Cop, self.VERB_TERMINAL_TRANSFER)
        self.A2Pl_Cop.add_suffix_form("sInIz")                         # (siz) elma-siniz, (siz) armut-sunuz, elma-ymis-siniz
        self.A2Pl_Cop.add_suffix_form("nIz", comes_after_cond_or_past) # elma-ydi-niz, elma-ysa-niz

        self.VERB_COPULA_WITH_TENSE.add_out_suffix(self.A3Pl_Cop, self.VERB_TERMINAL_TRANSFER)
        self.A3Pl_Cop.add_suffix_form("lAr")    # (onlar) elma-lar(dir), (onlar) armut-lar(dir), elma-ymis-lar, elma-ydi-lar, elma-ysa-lar
