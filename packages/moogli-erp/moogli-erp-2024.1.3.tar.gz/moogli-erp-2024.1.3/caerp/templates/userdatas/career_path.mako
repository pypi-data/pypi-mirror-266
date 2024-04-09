<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" name="utils"/>
<%block name="mainblock">
% if api.has_permission('edit.userdatas'):
	<% add_url = request.current_route_path(_query={'action': 'add_stage'}) %>
	<div class="content_vertical_padding">
		<a class='btn btn-primary' href="${add_url}">
			${api.icon('plus')}
			Ajouter une étape de parcours
		</a>
	</div>
% endif
<div class="table_container">
    % if career_path:
    <table class='hover_table'>
        <thead><tr>
            <th scope="col" class="col_date">Date</th>
            <th scope="col" class="col_date">&Eacute;chéance</th>
            <th scope="col" class="col_text">&Eacute;tape</th>
            <th scope="col" class="col_text">Nouvelle situation</th>
            <th scope="col" class="col_text">Fichiers rattachés</th>
            <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
        </tr></thead>
        <tbody>
    % else:
    <table>
        <tbody>
            <tr>
            	<td class="col_text">
                    <em>Le parcours de cet entrepreneur est vierge</em>
                </td>
            </tr>
    % endif
                % for stage in career_path:
                    <% edit_url = request.route_path('/career_paths/{id}', id=stage.id, _query=dict(action='edit')) %>
                    <% del_url = request.route_path('/career_paths/{id}', id=stage.id, _query=dict(action='delete')) %>
                    <% onclick = "document.location='{edit_url}'".format(edit_url=edit_url) %>
                    % if stage.career_stage is not None:
	                    <% tooltip_title = "Cliquer pour modifier l’étape « " + stage.career_stage.name + " »" %>
                    % else:
	                    <% tooltip_title = "Cliquer pour modifier l’étape" %>
                    % endif
                    <tr>
                        <td class="col_date" onclick="${onclick}" title="${tooltip_title}" >${api.format_date(stage.start_date)}</td>
                        <td class="col_date" onclick="${onclick}" title="${tooltip_title}" >${api.format_date(stage.end_date)}</td>
                        <td class="col_text" onclick="${onclick}" title="${tooltip_title}" >
                            % if stage.career_stage is not None:
                                ${stage.career_stage.name}
                            % endif
                        </td>
                        <td class="col_text" onclick="${onclick}" title="${tooltip_title}" >
                            % if stage.cae_situation is not None:
                                <strong>${stage.cae_situation.label}</strong>
                            % endif
                        </td>
                        <td class='col_text'>
                            % if stage.files:
                            % for child in stage.files:
                            % if loop.first:
                                <ul class="file_list">
                            % endif
                                <li>
                                <% file_dl_url = request.route_path('/files/{id}', id=child.id, _query=dict(action='download')) %>
                                    <a href="#!" onclick="window.openPopup('${file_dl_url}');" title="Télécharger ce fichier dans une nouvelle fenêtre" aria-label="Télécharger ce fichier dans une nouvelle fenêtre">
                                        ${child.label}
                                    </a>
                                </li>
                            % if loop.last:
                                </ul>
                            % endif
                            % endfor
                            % endif
                        </td>
                        <td class="col_actions width_two">
                            <ul>
								<li><a class="btn icon only" href="${edit_url}" title="Modifier cette étape" aria-label="Modifier cette étape">
									${api.icon('pen')}
									</a></li>
								<li>
                                    <%utils:post_action_btn url="${del_url}" icon="trash-alt"
                                      _class="btn icon only negative"
                                      onclick="return confirm('Êtes vous sûr de vouloir supprimer cette étape de parcours ?')"
                                      title="Supprimer cette étape"
                                      aria_label="Supprimer cette étape"
                                    >
                                    </%utils:post_action_btn>
							    </li>
							</ul>
                        </td>
                    </tr>
                % endfor
        </tbody>
    </table>
</%block>
