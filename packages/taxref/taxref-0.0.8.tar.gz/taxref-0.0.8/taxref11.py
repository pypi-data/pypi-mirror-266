"""Taxref 11 specific module"""

from collections import namedtuple
from enum import Enum, auto

from pandas.core.indexing import _LocIndexer


class Taxref11(Enum):
    """
    Taxref 11 specification.
    """
    REGNE = auto()
    PHYLUM = auto()
    CLASSE = auto()
    ORDRE = auto()
    FAMILLE = auto()
    SOUS_FAMILLE = auto()
    TRIBU = auto()
    GROUP1_INPN = auto()
    GROUP2_INPN = auto()
    CD_NOM = auto()
    CD_TAXSUP = auto()
    CD_SUP = auto()
    CD_REF = auto()
    RANG = auto()
    LB_NOM = auto()
    LB_AUTEUR = auto()
    NOM_COMPLET = auto()
    NOM_COMPLET_HTML = auto()
    NOM_VALIDE = auto()
    NOM_VERN = auto()
    NOM_VERN_ENG = auto()
    HABITAT = auto()
    FR = auto()
    GF = auto()
    MAR = auto()
    GUA = auto()
    SM = auto()
    SB = auto()
    SPM = auto()
    MAY = auto()
    EPA = auto()
    REU = auto()
    SA = auto()
    TA = auto()
    TAAF = auto()
    PF = auto()
    NC = auto()
    WF = auto()
    CLI = auto()
    URL = auto()


Taxref11_tuple = namedtuple('Taxref11_tuple', [v.name.lower() for v in Taxref11])


def to_taxref11_tuple(single: _LocIndexer) -> Taxref11_tuple:
    """
    Builds a namedtuple from a panda row.
    """
    return Taxref11_tuple(regne=single[Taxref11.REGNE.name],
                          phylum=single[Taxref11.PHYLUM.name],
                          classe=single[Taxref11.CLASSE.name],
                          ordre=single[Taxref11.ORDRE.name],
                          famille=single[Taxref11.FAMILLE.name],
                          sous_famille=single[Taxref11.SOUS_FAMILLE.name],
                          tribu=single[Taxref11.TRIBU.name],
                          group1_inpn=single[Taxref11.GROUP1_INPN.name],
                          group2_inpn=single[Taxref11.GROUP2_INPN.name],
                          cd_nom=single.name,
                          cd_taxsup=single[Taxref11.CD_TAXSUP.name],
                          cd_sup=single[Taxref11.CD_SUP.name],
                          cd_ref=single[Taxref11.CD_REF.name],
                          rang=single[Taxref11.RANG.name],
                          lb_nom=single[Taxref11.LB_NOM.name],
                          lb_auteur=single[Taxref11.LB_AUTEUR.name],
                          nom_complet=single[Taxref11.NOM_COMPLET.name],
                          nom_complet_html=single[Taxref11.NOM_COMPLET_HTML.name],
                          nom_valide=single[Taxref11.NOM_VALIDE.name],
                          nom_vern=single[Taxref11.NOM_VERN.name],
                          nom_vern_eng=single[Taxref11.NOM_VERN_ENG.name],
                          habitat=single[Taxref11.HABITAT.name],
                          fr=single[Taxref11.FR.name],
                          gf=single[Taxref11.GF.name],
                          mar=single[Taxref11.MAR.name],
                          gua=single[Taxref11.GUA.name],
                          sm=single[Taxref11.SM.name],
                          sb=single[Taxref11.SB.name],
                          spm=single[Taxref11.SPM.name],
                          may=single[Taxref11.MAY.name],
                          epa=single[Taxref11.EPA.name],
                          reu=single[Taxref11.REU.name],
                          sa=single[Taxref11.SA.name],
                          ta=single[Taxref11.TA.name],
                          taaf=single[Taxref11.TAAF.name],
                          pf=single[Taxref11.PF.name],
                          nc=single[Taxref11.NC.name],
                          wf=single[Taxref11.WF.name],
                          cli=single[Taxref11.CLI.name],
                          url=single[Taxref11.URL.name]
                          )
