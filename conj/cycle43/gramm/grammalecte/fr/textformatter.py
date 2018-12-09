#!python3

import re


dReplTable = {
    # surnumerary_spaces
    "start_of_paragraph":          [("^[  ]+", "")],
    "end_of_paragraph":            [("[  ]+$", "")],
    "between_words":               [("  |  ", " "),  # espace + espace insécable -> espace
                                    ("  +", " "),    # espaces surnuméraires
                                    ("  +", " ")],   # espaces insécables surnuméraires
    "before_punctuation":          [(" +(?=[.,…])", "")],
    "within_parenthesis":          [("\\([  ]+", "("),
                                    ("[  ]+\\)", ")")],
    "within_square_brackets":      [("\\[[  ]+", "["),
                                    ("[  ]+\\]", "]")],
    "within_quotation_marks":      [("“[  ]+", "“"),
                                    ("[  ]”", "”")],
    ## non-breaking spaces
    # espaces insécables
    "nbsp_before_punctuation":     [("(?<=[]\\w…)»}])([:;?!])[   ]", " \\1 "),
                                    ("(?<=[]\\w…)»}])([:;?!])$", " \\1"),
                                    ("[  ]+([:;?!])", " \\1")],
    "nbsp_within_quotation_marks": [("«(?=\\w)", "« "),
                                    ("«[  ]+", "« "),
                                    ("(?<=[\\w.!?])»", " »"),
                                    ("[  ]+»", " »")],
    "nbsp_within_numbers":         [("(\\d)[  ](?=\\d)", "\\1 ")],
    # espaces insécables fines
    "nnbsp_before_punctuation":    [("(?<=[]\\w…)»}])([;?!])[   ]", " \\1 "),
                                    ("(?<=[]\\w…)»}])([;?!])$", " \\1"),
                                    ("[  ]+([;?!])", " \\1"),
                                    ("(?<=[]\\w…)»}]):", " :"),
                                    ("[  ]+:", " :")],
    "nnbsp_within_quotation_marks":[("«(?=\\w)", "« "),
                                    ("«[  ]+", "« "),
                                    ("(?<=[\\w.!?])»", " »"),
                                    ("[  ]+»", " »")],
    "nnbsp_within_numbers":        [("(\\d)[  ](\\d)", "\\1 \\2")],
    # common
    "nbsp_before_symbol":          [("(\\d) ?([%‰€$£¥˚Ω℃])", "\\1 \\2")],
    "nbsp_before_units":           [("(?<=[0-9⁰¹²³⁴⁵⁶⁷⁸⁹]) ?([kcmµn]?(?:[slgJKΩ]|m[²³]?|Wh?|Hz|dB)|[%‰]|°C)\\b", " \\1")],
    "nbsp_repair":                 [("(?<=[[(])[   ]([!?:;])", "\\1"),
                                    ("(https?|ftp)[   ]:(?=//)", "\\1:"),
                                    ("&([a-z]+)[   ];", "&\\1;"),
                                    ("&#([0-9]+|x[0-9a-fA-F]+)[   ];", "&#\\1;")],
    ## missing spaces
    "add_space_after_punctuation": [("([;!…])(?=\\w)", "\\1 "),
                                    ("[?](?=[A-ZÉÈÊÂÀÎ])", "? "),
                                    ("\\.(?=[A-ZÉÈÎ][a-zA-ZàâÂéÉèÈêÊîÎïÏôÔöÖûÛüÜùÙ])", ". "),
                                    ("\\.(?=À)", ". "),
                                    ("(?i)([,:])(?=[a-zàâäéèêëîïôöûüù])", "\\1 "),
                                    ("(?i)([a-zàâäéèêëîïôöûüù]),(?=[0-9])", "\\1, ")],
    "add_space_around_hyphens":    [(" ([-–—])(?=[a-zàâäéèêëîïôöûüù\"«“'‘])", " \\1 "),
                                    ("(?<=[a-zàâäéèêëîïôöûüù\"»”'’])([-–—]) ", " \\1 ")],
    "add_space_repair":            [("DnT, ([wA])\\b", "DnT,\\1")],
    ## erase
    "erase_non_breaking_hyphens":  [("­", "")],
    ## typographic signs
    "ts_apostrophe":          [ ("(?i)\\b([ldnjmtscç])['´‘′`](?=\\w)", "\\1’"),
                                ("(?i)(qu|jusqu|lorsqu|puisqu|quoiqu|quelqu|presqu|entr|aujourd|prud)['´‘′`]", "\\1’") ],
    "ts_ellipsis":            [ ("\\.\\.\\.", "…"),
                                ("(?<=…)[.][.]", "…"),
                                ("…[.](?![.])", "…") ],
    "ts_n_dash_middle":       [ (" [-—] ", " – "), 
                                (" [-—],", " –,") ],
    "ts_m_dash_middle":       [ (" [-–] ", " — "),
                                (" [-–],", " —,") ],
    "ts_n_dash_start":        [ ("^[-—][  ]", "– "),
                                ("^– ", "– "),
                                ("^[-–—](?=[\\w.…])", "– ") ],
    "ts_m_dash_start":        [ ("^[-–][  ]", "— "),
                                ("^— ", "— "),
                                ("^«[  ][—–-][  ]", "« — "),
                                ("^[-–—](?=[\\w.…])", "— ") ],
    "ts_quotation_marks":     [ (u'"(\\w+)"', "“$1”"),
                                ("''(\\w+)''", "“$1”"),
                                ("'(\\w+)'", "“$1”"),
                                ("^(?:\"|'')(?=\\w)", "« "),
                                (" (?:\"|'')(?=\\w)", " « "),
                                ("\\((?:\"|'')(?=\\w)", "(« "),
                                ("(?<=\\w)(?:\"|'')$", " »"),
                                ("(?<=\\w)(?:\"|'')(?=[] ,.:;?!…)])", " »"),
                                (u'(?<=[.!?…])" ', " » "),
                                (u'(?<=[.!?…])"$', " »") ],
    "ts_spell":               [ ("coeur", "cœur"), ("Coeur", "Cœur"),
                                ("coel(?=[aeio])", "cœl"), ("Coel(?=[aeio])", "Cœl"),
                                ("choeur", "chœur"), ("Choeur", "Chœur"),
                                ("foet", "fœt"), ("Foet", "Fœt"),
                                ("oeil", "œil"), ("Oeil", "Œil"),
                                ("oeno", "œno"), ("Oeno", "Œno"),
                                ("oesoph", "œsoph"), ("Oesoph", "Œsoph"),
                                ("oestro", "œstro"), ("Oestro", "Œstro"),
                                ("oeuf", "œuf"), ("Oeuf", "Œuf"),
                                ("oeuvr", "œuvr"), ("Oeuvr", "Œuvr"),
                                ("moeur", "mœur"), ("Moeur", "Mœur"),
                                ("noeu", "nœu"), ("Noeu", "Nœu"),
                                ("soeur", "sœur"), ("Soeur", "Sœur"),
                                ("voeu", "vœu"), ("Voeu", "Vœu"),
                                ("aequo", "æquo"), ("Aequo", "Æquo"),
                                ("\\bCa\\b", "Ça"), (" ca\\b", " ça"),
                                ("\\bdej[aà]\\b", "déjà"), ("\\bplutot\\b", "plutôt"),
                                ("\\bmeme\\b", "même"), ("\\bmemes\\b", "mêmes"), ("\\bMeme\\b", "Même"),
                                ("\\b([cC]e(?:ux|lles?|lui))-la\\b", "$1-là"),
                                ("\\bmalgre\\b", "malgré"), ("\\bMalgre\\b", "Malgré"),
                                ("\\betre\\b", "être"), ("\\bEtre\\b", "Être"),
                                ("\\btres\\b", "très"), ("\\bTres\\b", "Très"),
                                ("\\bEtai([ts]|ent)\\b", "Étai$1"),
                                ("\\bE(tat|cole|crit|poque|tude|ducation|glise|conomi(?:qu|)e|videmment|lysée|tienne|thiopie|cosse|gypt(?:e|ien)|rythrée|pinal|vreux)", "É$1") ],
    "ts_ligature_ffi_on":       [("ffi", "ﬃ")],
    "ts_ligature_ffl_on":       [("ffl", "ﬄ")],
    "ts_ligature_fi_on":        [("fi", "ﬁ")],
    "ts_ligature_fl_on":        [("fl", "ﬂ")],
    "ts_ligature_ff_on":        [("ff", "ﬀ")],
    "ts_ligature_ft_on":        [("ft", "ﬅ")],
    "ts_ligature_st_on":        [("st", "ﬆ")],
    "ts_ligature_fi_off":       [("ﬁ", "fi")],
    "ts_ligature_fl_off":       [("ﬂ", "fl")],
    "ts_ligature_ff_off":       [("ﬀ", "ff")],
    "ts_ligature_ffi_off":      [("ﬃ", "ffi")],
    "ts_ligature_ffl_off":      [("ﬄ", "ffl")],
    "ts_ligature_ft_off":       [("ﬅ", "ft")],
    "ts_ligature_st_off":       [("ﬆ", "st")],
    "ts_units":               [ ("\\bN\\.([ms])\\b", "N·\\1"), # N·m et N·m-1, N·s
                                ("\\bW\\.h\\b", "W·h"),
                                ("\\bPa\\.s\\b", "Pa·s"),
                                ("\\bA\\.h\\b", "A·h"),
                                ("\\bΩ\\.m\\b", "Ω·m"),
                                ("\\bS\\.m\\b", "S·m"),
                                ("\\bg\\.s(?=-1)\\b", "g·s"),
                                ("\\bm\\.s(?=-[12])\\b", "m·s"),
                                ("\\bg\\.m(?=2|-3)\\b", "g·m"),
                                ("\\bA\\.m(?=-1)\\b", "A·m"),
                                ("\\bJ\\.K(?=-1)\\b", "J·K"),
                                ("\\bW\\.m(?=-2)\\b", "W·m"),
                                ("\\bcd\\.m(?=-2)\\b", "cd·m"),
                                ("\\bC\\.kg(?=-1)\\b", "C·kg"),
                                ("\\bH\\.m(?=-1)\\b", "H·m"),
                                ("\\bJ\\.kg(?=-1)\\b", "J·kg"),
                                ("\\bJ\\.m(?=-3)\\b", "J·m"),
                                ("\\bm[2²]\\.s\\b", "m²·s"),
                                ("\\bm[3³]\\.s(?=-1)\\b", "m³·s"),
                                #("\\bJ.kg-1.K-1\\b", "J·kg-1·K-1"),
                                #("\\bW.m-1.K-1\\b", "W·m-1·K-1"),
                                #("\\bW.m-2.K-1\\b", "W·m-2·K-1"),
                                ("\\b(Y|Z|E|P|T|G|M|k|h|da|d|c|m|µ|n|p|f|a|z|y)Ω\\b", "\\1Ω") ],
    ## misc
    "ordinals_exponant":      [ ("\\b([0-9]+)(?:i?[èe]me|è|e)\\b", "\\1ᵉ"),
                                ("\\b([XVICL]+)(?:i?[èe]me|è)\\b", "\\1ᵉ"),
                                ("(?<=\\b(au|l[ea]|du) [XVICL])e\\b", "ᵉ"),
                                ("(?<=\\b[XVI])e(?= siècle)", "ᵉ"),
                                ("(?<=\\b[1I])er\\b", "ᵉʳ"),
                                ("(?<=\\b[1I])re\\b", "ʳᵉ") ],
    "ordinals_no_exponant":   [ ("\\b([0-9]+)(?:i?[èe]me|è)\\b", "\\1e"),
                                ("\\b([XVICL]+)(?:i?[èe]me|è)\\b", "\\1e"),
                                ("(?<=\\b[1I])ᵉʳ\\b", "er"),
                                ("(?<=\\b[1I])ʳᵉ\\b", "er")],
    "etc":                    [ ("etc(…|[.][.][.]?)", "etc."),
                                ("(?<!,) etc[.]", ", etc.") ],
    ## missing hyphens
    "mh_interrogatives":      [ ("[ -]t[’'](?=il\\b|elle|on\\b)", "-t-"),
                                (" t-(?=il|elle|on)", "-t-"),
                                ("[ -]t[’'-](?=ils|elles)", "-"),
                                ("(?<=[td])-t-(?=il|elle|on)", "-") ],
    "mh_numbers": [ ("dix (sept|huit|neuf)", "dix-\\1"),
                    ("quatre vingt", "quatre-vingt"),
                    ("(soixante|quatre-vingt) dix", "\\1-dix"),
                    ("(vingt|trente|quarante|cinquante|soixante(?:-dix|)|quatre-vingt(?:-dix|)) (deux|trois|quatre|cinq|six|sept|huit|neuf)\\b", "\\1-\\2")],
    "mh_frequent_words":      [ ("(?i)ce(lles?|lui|ux) (ci|là)\\b", "ce\\1-\\2"),
                                ("(?i)(?<!-)\\b(ci) (joint|desso?us|contre|devant|avant|après|incluse|g[îi]t|gisent)", "\\1-\\2"),
                                ("vis à vis", "vis-à-vis"),
                                ("Vis à vis", "Vis-à-vis"),
                                ("week end", "week-end"),
                                ("Week end", "Week-end"),
                                ("(?i)(plus|moins) value", "\\1-value") ],
    ## missing apostrophes
    "ma_word":                  [("(?i)(qu|lorsqu|puisqu|quoiqu|presqu|jusqu|aujourd|entr|quelqu|prud) ", "\\1’")],
    "ma_1letter_lowercase":     [("\\b([ldjnmtscç]) (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "\\1’")],
    "ma_1letter_uppercase":     [("\\b([LDJNMTSCÇ]) (?=[aàeéêiîoôuyhAÀEÉÊIÎOÔUYH])", "\\1’")]
}


lOptRepl = [
    ("ts_units", True),
    ("start_of_paragraph", True),
    ("end_of_paragraph", True),
    ("between_words", True),
    ("before_punctuation", True),
    ("within_parenthesis", True),
    ("within_square_brackets", True),
    ("within_quotation_marks", True),
    ("nbsp_before_punctuation", True),
    ("nbsp_within_quotation_marks", True),
    ("nbsp_within_numbers", True),
    ("nnbsp_before_punctuation", False),
    ("nnbsp_within_quotation_marks", False),
    ("nnbsp_within_numbers", False),
    ("nbsp_before_symbol", True),
    ("nbsp_before_units", True),
    ("nbsp_repair", True),
    ("add_space_after_punctuation", True),
    ("add_space_around_hyphens", True),
    ("add_space_repair", True),
    ("erase_non_breaking_hyphens", False),
    ("ts_apostrophe", True),
    ("ts_ellipsis", True),
    ("ts_n_dash_middle", True),
    ("ts_m_dash_middle", False),
    ("ts_n_dash_start", False),
    ("ts_m_dash_start", True),
    ("ts_quotation_marks", True),
    ("ts_spell", True),
    ("ts_ligature_ffi_on", False),
    ("ts_ligature_ffl_on", False),
    ("ts_ligature_fi_on", False),
    ("ts_ligature_fl_on", False),
    ("ts_ligature_ff_on", False),
    ("ts_ligature_ft_on", False),
    ("ts_ligature_st_on", False),
    ("ts_ligature_fi_off", False),
    ("ts_ligature_fl_off", False),
    ("ts_ligature_ff_off", False),
    ("ts_ligature_ffi_off", False),
    ("ts_ligature_ffl_off", False),
    ("ts_ligature_ft_off", False),
    ("ts_ligature_st_off", False),
    ("ordinals_exponant", False),
    ("ordinals_no_exponant", True),
    ("etc", True),
    ("mh_interrogatives", True),
    ("mh_numbers", True),
    ("mh_frequent_words", True),
    ("ma_word", True),
    ("ma_1letter_lowercase", False),
    ("ma_1letter_uppercase", False),
]


class TextFormatter:

    def __init__ (self):
        for sOpt, lTup in dReplTable.items():
            for i, t in enumerate(lTup):
                lTup[i] = (re.compile(t[0]), t[1])

    def formatText (self, sText, **args):
        for sOptName, bVal in lOptRepl:
            if bVal:
                for zRgx, sRep in dReplTable[sOptName]:
                    sText = zRgx.sub(sRep, sText)
        return sText
