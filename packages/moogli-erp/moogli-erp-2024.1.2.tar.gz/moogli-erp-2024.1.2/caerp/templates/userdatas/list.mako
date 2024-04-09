<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/searchformlayout.mako" import="searchform"/>

<%block name='actionmenucontent'>
<div class='layout flex main_actions'>
    <div role='group'>
        <a class='btn btn-primary' href="${request.route_path('/userdatas', _query=dict(action='add'))}" title="Nouvelle entrée gestion sociale">
            ${api.icon("plus")} 
            Nouvelle entrée
        </a>
        % if request.has_module('csv_import') and api.has_permission('admin'):
            <a class='btn icon_only_mobile' href="${request.route_path('import_step1')}" title="Importer des données">
            	${api.icon("file-import")}
            	Importer
            </a>
        % endif
    </div>
    <div role='group'>
        <%
        args = request.GET
        url_xls = request.route_path('/userdatas.xls', _query=args)
        url_ods = request.route_path('/userdatas.ods', _query=args)
        url_csv = request.route_path('/userdatas.csv', _query=args)
        %>
        <a class='btn icon_only_mobile' href='javascript:void(0);' onclick="window.openPopup('${url_xls}');" title="Exporter les éléments de la liste au format Excel (xls) dans une nouvelle fenêtre" aria-label="Exporter les éléments de la liste au format Excel (xls) dans une nouvelle fenêtre">
            ${api.icon("file-excel")}
            Excel
        </a>
        <a class='btn icon_only_mobile' href='javascript:void(0);' onclick="window.openPopup('${url_ods}');" title="Exporter les éléments de la liste au format Open Document (ods) dans une nouvelle fenêtre" aria-label="Exporter les éléments de la liste au format Open Document (ods) dans une nouvelle fenêtre">
            ${api.icon("file-spreadsheet")}
            ODS
        </a>
        <a class='btn icon_only_mobile' href='javascript:void(0);' onclick="window.openPopup('${url_csv}');" title="Exporter les éléments de la liste au format csv dans une nouvelle fenêtre" aria-label="Exporter les éléments de la liste au format csv dans une nouvelle fenêtre">
            ${api.icon("file-csv")}
            CSV
        </a>
    </div>
</div>
</%block>

<%block name="content">

${searchform()}

<div>
    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
        <table class="hover_table">
            <thead>
                <tr>
                    <th scope="col" class="col_text">${sortable("Nom", "lastname")}</th>
                    <th scope="col" class="col_text">Situation CAE</th>
                    <th scope="col" class="col_text">Accompagnateur</th>
                    <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
                </tr>
            </thead>
            <tbody>
                % for userdata in records:
                    <% url = request.route_path('/users/{id}/userdatas/edit', id=userdata.user_id) %>
                    <% onclick = "document.location='{url}'".format(url=url) %>
                    <% tooltip_title = "Cliquer pour voir ou modifier" %>
                    <tr class='white_tr'>
                        <td class="col_text" onclick="${onclick}" title="${tooltip_title}">${api.format_account(userdata)}</td>
                        <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                            % if userdata.situation_situation:
                                ${userdata.situation_situation.label}
                            % endif
                        </td>
                        <td class="col_text" onclick="${onclick}" title="${tooltip_title}">${api.format_account(userdata.situation_follower)}</td>
                        ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(userdata))}
                    </tr>
                % endfor
            </tbody>
        </table>
    </div>
    ${pager(records)}
</div>
</%block>
