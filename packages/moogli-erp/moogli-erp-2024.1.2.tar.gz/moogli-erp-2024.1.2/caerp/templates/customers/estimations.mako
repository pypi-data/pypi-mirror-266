<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/utils.mako" import="format_text" />
<%namespace file="/base/searchformlayout.mako" import="searchform"/>


<%block name='mainblock'>
<div>
    ${searchform()}

    <div>
        ${records.item_count} Résultat(s)
    </div>
    <div class='table_container'>
        <% columns = 8 %>
        <table class="top_align_table hover_table">
            % if records:
            <thead>
                <th scope="col" class="col_status" title="Statut"><span class="screen-reader-text">Statut</span></th>
                % if is_admin:
                    <% columns += 1 %>
                    <th scope="col" class="col_text">${sortable("Entrepreneur", 'company')}</th>
                % endif
                <th scope="col" class="col_date">${sortable("Émis le", 'date')}</th>
                <th scope="col" class="col_text">Description</th>
                <th scope="col" class="col_text">${sortable("Client", 'customer')}</th>
                <th scope="col" class="col_number"><span class="screen-reader-text">Montant </span>HT</th>
                <th scope="col" class="col_number">TVA</th>
                <th scope="col" class="col_number">TTC</th>
                <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
            </thead>
            % endif
            <tbody>
                % if records:
                    <tr class="row_recap">
                        <th scope='row' colspan='${columns - 4}' class='col_text'>Total</td>
                        <td class='col_number'>${api.format_amount(totalht, precision=5)}&nbsp;€</td>
                        <td class='col_number'>${api.format_amount(totaltva, precision=5)}&nbsp;€</td>
                        <td class='col_number'>${api.format_amount(totalttc, precision=5)}&nbsp;€</td>
                        <td></td>
                    </tr>
                    % for id_, document in records:
                        <% name = document.name %>
                        <% internal_number = document.internal_number %>
                        <% status = document.global_status %>
                        <% signed_status = document.signed_status %>
                        <% date = document.date %>
                        <% geninv = document.geninv %>
                        <% description = document.description %>
                        <% ht = document.ht %>
                        <% tva = document.tva %>
                        <% ttc = document.ttc %>
                        <% customer_id = document.customer_id %>
                        <% customer_label = document.customer.name %>
                        <% company_id = document.company_id %>
                        <% company_name = document.company.full_label %>
                        <% business_type = document.business_type %>
                        <% url = api.task_url(document, suffix='/general') %>
                        <% onclick = "document.location='{url}'".format(url=url) %>
                        <% tooltip_title = "Cliquer pour voir le devis « " + document.name + " »" %>

                        <tr class="status status-${status} signed-status-${signed_status} geninv-${geninv}">
                            <td class="col_status" title="${api.format_estimation_status(document)} - ${tooltip_title}" aria-label="${api.format_estimation_status(document)}" onclick="${onclick}">
                                <span class="icon status ${status}">
                                    ${api.icon(api.status_icon(document))}
                                </span>
                            </td>
                            % if is_admin:
                                <td class="col_text invoice_company_name" onclick="${onclick}" title="${tooltip_title}">${company_name}</td>
                            % endif
                            <td class="col_date" onclick="${onclick}" title="${tooltip_title}">${api.format_date(date)}</td>
                            <td class="col_text">
                                <a href="${url}" title="${tooltip_title}" aria-label="${tooltip_title}">${name} (<small>${internal_number}</small>)</a>
                                ${request.layout_manager.render_panel('business_type_label', business_type)}
                                % if document.auto_validated:
                                    <span class="icon tag positive">                        		
                                        ${api.icon("user-check")}
                                        Auto-validé
                                    </span>
                                % endif
                                <small class="description">${format_text(description)}</small>
                            </td>
                            <td class="col_text"><a href="${request.route_path("customer", id=customer_id)}" title="Cliquer pour voir le client « ${customer_label} »" aria-label="Cliquer pour voir le client « ${customer_label} »">${customer_label}</a></td>
                            <td class="col_number" onclick="${onclick}" title="${tooltip_title}"><strong>${api.format_amount(ht, precision=5) | n}&nbsp;€</strong></td>
                            <td class="col_number" onclick="${onclick}" title="${tooltip_title}">${api.format_amount(tva, precision=5) | n}&nbsp;€</td>
                            <td class="col_number" onclick="${onclick}" title="${tooltip_title}">${api.format_amount(ttc, precision=5) | n}&nbsp;€</td>
                            <td class="col_actions width_one">
                                <a class='btn icon only' href="${request.route_path('/estimations/{id}.pdf', id=id_)}" title="Télécharger le devis au format PDF" aria-label="Télécharger le devis au format PDF">
                                    ${api.icon('file-pdf')}
                                </a>
                            </td>
                        </tr>
                    % endfor
                    <tr class="row_recap">
                        <th scope='row' colspan='${columns - 4}' class='col_text'>Total</td>
                        <td class='col_number'>${api.format_amount(totalht, precision=5)}&nbsp;€</td>
                        <td class='col_number'>${api.format_amount(totaltva, precision=5)}&nbsp;€</td>
                        <td class='col_number'>${api.format_amount(totalttc, precision=5)}&nbsp;€</td>
                        <td></td>
                    </tr>
                % else:
                    <tr><td class='col_text' colspan='7'><em>Aucun devis n’a été créé</em></td></tr>
                % endif
            </tbody>
        </table>
    </div>
    ${pager(records)}
</div>
</%block>
