def is_direct_member__factory(context, userid):
    """
    Erzeuge eine Funktion, die prüft, ob der *beim Erzeugen angegebene* Nutzer
    in der bei jedem Aufruf anzugebenden Gruppe direkt enthalten ist.
    """
    acl = getToolByName(context, 'acl_users')
    gpm = acl.source_groups._group_principal_map

    def is_direct_member_of(group_id):
        return userid in gpm[group_id]

    return is_direct_member_of


def is_member_of__factory(context, userid):
    """
    Erzeuge eine Funktion, die die *direkte oder indirekte* Mitgliedschaft
    des übergebenen Users in der jeweils zu übergebenden Gruppe überprüft.
    """
    acl = getToolByName(context, 'acl_users')
    gpm = acl.source_groups._group_principal_map

    groups = build_groups_set(gpm, userid)

    def is_member_of(groupid):
        return groupid in groups

    return is_member_of


def is_member_of_any(context, group_ids, user_id=None, default=False):
    """
    Is the given or active user member of one of the given groups?

    - For anonymous execution, raises Unauthorized
      (might become changable by keyword-only argument)
    - The normal usage is without specification of the user_id,
      i.e. checking for the logged-in user
    - if the group_ids sequence is empty, the default is used

    """
    pm = getToolByName(context, 'portal_membership')
    if pm.isAnonymousUser():
        raise Unauthorized
    if user_id is not None:
        # wer darf sowas fragen? Manager, Gruppenmanager, ...?
        # TODO: Hier entsprechende Überprüfung!
        pass

    if not group_ids:
        return default
    if user_id is None:
        member = pm.getAuthenticatedMember()
        user_id = member.getId()

    return user_id in get_all_members(context, group_ids)


def get_all_members(context, group_ids, **kwargs):  # --- [[
    """
    Return all members of the given groups

    Liefere alle Mitglieder der übergebenen Gruppe(n).

    Schlüsselwortargumente für .utils.recursive_members und
    groupinfo_factory dürfen angegeben werden;
    letztere werden aber ignoriert, wenn die vorgabegemäße Filterung
    groups_only=True übersteuert wird. In diesem Fall (potentiell sowohl
    Benutzer als auch Gruppen, oder nur Benutzer) werden nur IDs
    zurückgegeben.

    Rückgabe:
    - Sequenz von Gruppeninformationen, mit groups_only=True (Vorgabe);
    - ansonsten nur eine Sequenz der IDs (je nach Aufrufargumenten nur
      Benutzer-IDs, oder gemischt)
    """
    acl = getToolByName(context, 'acl_users')
    gpm = acl.source_groups._group_principal_map
    filter_args = {}
    for key in ('groups_only', 'users_only',
		'containers',
		'default_to_all'):
	try:
	    filter_args[key] = kwargs.pop(key)
	except KeyError:
	    pass
    members = recursive_members(list_of_strings(group_ids),
				gpm, **filter_args)
    groups_only = filter_args.get('groups_only', False)
    if groups_only:
	format_args = {'pretty': False,
		       'forlist': True,
		       }
	format_args.update(kwargs)
	ggibi = groupinfo_factory(context, **format_args)
	res = []
	for gid in members:
	    res.append(ggibi(gid))
	return res
    elif kwargs and debug_active:
	pp('ignoriere:', kwargs)

    return members
