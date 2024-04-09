<%doc>
BPF datas list.
This is displayed if and only if there are datas for several years
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="table_btn"/>
<%block name='mainblock'>
    ${request.layout_manager.render_panel(
    'help_message_panel',
    parent_tmpl_dict=context.kwargs
    )}
    <div class='content_vertical_padding'>

    </div>
    <div class='content_vertical_padding'>
        <h3>${title}</h3>
        <div>
            <p>
                Lorsqu’une formation est à cheval sur plusieurs années, il faut
                renseigner des données BPF pour chacune des années.
            </p>
            <p>
                ${new_bpfdata_menu.render(request)|n}
            </p>
            <table class='hover_table'>
                <tr>
                    <th scope="col" class="col_number">Année</th>
                    <th scope="col" class="col_text">Document cible</th>
                    <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                </tr>
                % for bpf_data, form_link, delete_link in bpf_datas_links:
                    <tr>
                        <td class="col_number">
                            BPF ${bpf_data.financial_year}
                        </td>
                        <td class="col_text">
                            Cerfa ${bpf_data.cerfa_version}
                        </td>
                        <td class="col_actions width_two">
                        	<ul>
                        		<li>
		                            ${table_btn(form_link, "Voir/éditer", "Voir / Éditer les données BPF", icon='pen')}
                        		</li>
                        		<li>
		                            ${table_btn(delete_link, "Supprimer", "Supprimer les données pour cette année", icon="trash-alt", css_class="negative", method='post')}
                        		</li>
                        	</ul>
                        </td>
                    </tr>
                % endfor
            </table>
        </div>
    </div>
</%block>
