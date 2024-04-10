# -------------------------------- [ groupinfo_factory ... [
# Python compatibility:
from __future__ import print_function


def groupinfo_factory(context, pretty=0, forlist=0, searchtext=0):
    """
    Factory-Funktion; als Ersatz für get_group_info_by_id, insbesondere für
    wiederholte Aufrufe.  Indirektionen etc. werden einmalig beim Erstellen der
    Funktion aufgelöst und anschließend in einer Closure vorgehalten.

    pretty -- Gruppennamen auflösen, wenn Suffix an ID und Titel
    forlist -- Minimale Rückgabe (nur ID und Titel),
               aber mit pretty kombinierbar
    """
    pg = getToolByName(context, 'portal_groups')
    get_group = pg.getGroupById
    acl = getToolByName(context, 'acl_users')
    translate = make_translator(context)
    GROUPS = acl.source_groups._groups

    def minimal_group_info(group_id):
        """
        Nur ID und Titel
        """
        group = get_group(group_id)

        dict_ = {'id': group_id}
        try:
            thegroup = GROUPS[group_id]
            dict_['group_title'] = safe_decode(thegroup['title'])
            return dict_
        except KeyError:
            return {}

    def basic_group_info(group_id):
        """
        Gib ein Dict. zurück;
        - immer vorhandene Schlüssel:
          id, group_title, group_description, group_manager, group_desktop
        - nur bei automatisch erzeugten Gruppen: role, role_translation, brain

        Argumente:
        group_id -- ein String, normalerweise mit 'group_' beginnend
        """

        group = get_group(group_id)

        dict_ = {'id': group_id}
        try:
            thegroup = GROUPS[group_id]
            dict_['group_title'] = safe_decode(thegroup['title'])
        except KeyError:
            return {}
        dict_['group_description'] = safe_decode(thegroup['description'])
        dict_['group_manager'] = thegroup.get('group_manager')
        dict_['group_desktop'] = thegroup.get('group_desktop')

        dic = split_group_id(group_id)
        if dic['role'] is not None:
            dict_.update(dic)

        dict_['role_translation'] = translate(dic['role'])
        dict_['brain'] = getbrain(context, dic['uid'])
        return dict_

    def pretty_group_info(group_id):
        """
        Ruft basic_group_info auf und fügt einen Schlüssel 'pretty_title'
        hinzu, der den Gruppentitel ohne das Rollensuffix enthält.
        """
        dic = basic_group_info(group_id)
        try:
            if 'role' not in dic:
                dic['pretty_title'] = translate(dic['group_title'])
                return dic
            liz = dic['group_title'].split()
            if liz and liz[-1] == dic['role']:
                stem = u' '.join(liz[:-1])
                mask = PRETTY_MASK[dic['role']]
                dic['pretty_title'] = translate(mask).format(group=stem)
            else:
                dic['pretty_title'] = translate(dic['group_title'])
        except KeyError as e:
            # evtl. keine Gruppe! (Aufruf durch get_mapping_group)
            print(e)
            pass
        return dic

    def minimal2_group_info(group_id):
        """
        Ruft minimal_group_info auf und modifiziert ggf. den Schlüssel
        'group_title' (entsprechend dem von pretty_group_info zurückgegebenen
        Schlüssel 'pretty_title')
        """
        dic = minimal_group_info(group_id)
        if not dic:     # Gruppe nicht (mehr) gefunden;
            return dic  # {} zurückgeben
        dic2 = split_group_id(group_id)
        if dic2['role'] is not None:
            dic.update(dic2)
        if 'role' not in dic:
            dic['group_title'] = translate(dic['group_title'])
            return dic
        liz = dic['group_title'].split()
        if liz and liz[-1] == six_text_type(dic['role']):
            stem = u' '.join(liz[:-1])
            mask = PRETTY_MASK[dic['role']]
            dic['group_title'] = translate(mask).format(group=stem)
        else:
            dic['group_title'] = translate(dic['group_title'])
        return dic

    def make_searchstring(group_info):
        """
        Arbeite direkt auf einem group_info-Dict;
        Gib kein Dict zurück, sondern einen String für Suchzwecke
        """
        try:
            group_id = group_info['id']
        except KeyError:
            raise
        try:
            res = [safe_decode(group_info['title']),
                   safe_decode(group_id)]
        except KeyError:
            print((list(group_info.items())))
            raise
            return u''
        dic2 = split_group_id(group_id)
        prettify = True
        for val in dic2.values():
            if val is None:
                prettify = False
                break  # es sind immer alle None, oder alle nicht None
            else:
                res.append(safe_decode(val))
        if prettify:
            pretty = pretty_group_title(group_id, res[0], translate)
            if pretty is not None:
                res.append(safe_decode(pretty))
        descr = group_info['description']
        if descr:
            res.append(safe_decode(descr))
        return u' '.join(res)

    if searchtext:
        return make_searchstring
    if forlist:
        if pretty:
            return minimal2_group_info
        else:
            return minimal_group_info
    if pretty:
        return pretty_group_info
    else:
        return basic_group_info
# -------------------------------- ] ... groupinfo_factory ]
