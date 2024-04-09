<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='actionmenucontent'>
% if request.has_permission("edit.project", layout.current_project_object):
<div class='layout flex main_actions'>
    <div role='group'>
        <a class='btn btn-primary icon' href="${layout.edit_url}">
        	${api.icon('pen')}
            Modifier le dossier
        </a>
    </div>
</div>
% endif
</%block>

<%block name='mainblock'>
<div>
	<div class='content_vertical_padding separate_bottom_dashed'>
		<a class='btn btn-primary' href='${add_url}'>
			${api.icon('calculator')}
			Créer une étude de prix
		</a>
    </div>

    ${searchform()}

    <div>
    	${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
		<table class="hover_table">
			% if records:
			<thead>
				<tr>
					<th scope="col" class="col_date">${sortable("Créé le", "created_at")}</th>
					<th scope="col" class="col_text">${sortable("Nom", "name")}</th>
					<th scope="col" class="col_text">Devis</th>
					<th scope="col" class="col_number">Total HT</th>
					<th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
				</tr>
			</thead>
			% endif
			<tbody>
				% if records:
					% for id, price_study in records:
					<% url = request.route_path('/price_studies/{id}', id=price_study.id) %>
					<% onclick = "document.location='{url}'".format(url=url) %>
					<% tooltip_title = "Cliquer pour voir l’étude de prix « " + price_study.name + " »" %>
						<tr class='tableelement'>
							<td class="col_date" onclick="${onclick}" title="${tooltip_title}">${api.format_date(price_study.created_at)}</td>
							<td class="col_text" onclick="${onclick}" title="${tooltip_title}">${price_study.name}</td>
							<td class="col_text" onclick="${onclick}" title="${tooltip_title}">
								<ul>
									% for estimation in price_study.estimations:
										<li>Devis : ${estimation.name}</li>
									% endfor
								</ul>
							</td>
							<td class="col_number" onclick="${onclick}" title="${tooltip_title}">
								${api.format_amount(price_study.ht, precision=5)|n}&nbsp;€
							</td>
							<td class='col_actions width_one'>
<!-- pour un seul bouton, ne pas mettre de dropdown mais le bouton Voir/Modifier (icône seule) directement. Ce serait bien aussi de mettre la même action Voir/Modifier au clic sur la ligne <tr> -->
								${request.layout_manager.render_panel('menu_dropdown', label="Actions", links=stream_actions(price_study))}
							</td>
						</tr>
					% endfor
				% else:
					<tr>
						<td colspan='7' class="col_text"><em>Aucune étude de prix n’a été initiée pour l’instant</em></td>
					</tr>
				% endif
			</tbody>
		</table>
    </div>
    ${pager(records)}
</div>
</%block>

<%block name='footerjs'>
$(function(){
    $('input[name=search]').focus();
});
</%block>
