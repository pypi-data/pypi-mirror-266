<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/utils.mako" import="company_list_badges"/>

% if records:
<table class="hover_table">
    <thead>
        <tr>
            <th scope="col" class="col_status col_text"></th>
            <th scope="col" class="col_text">${sortable("N° de pièce", "official_number")}</th>
            % if is_admin_view:
                <th scope="col" class="col_text">${sortable("Enseigne", "company_id")}</th>
            % endif
            <th scope="col" class="col_date">${sortable("Date", "date")}</th>
            <th scope="col" class="col_text">
                ${sortable("N° de facture du fournisseur", "remote_invoice_number")}
            </th>
            % if not is_supplier_view:
                <th scope="col" class="col_text">${sortable("Fournisseur", "supplier")}</th>
            % endif
            <th scope="col" class="col_number">${sortable("HT", "total_ht")}</th>
            <th scope="col" class="col_number">${sortable("TVA", "total_tva")}</th>
            <th scope="col" class="col_number">${sortable("TTC", "total")}</th>
            <th scope="col" class="col_number" title="Part réglée par la CAE">Part CAE</th>
            <th scope="col" class="col_actions" title="Actions"><span class="screen-reader-text">Actions</span></th>
        </tr>
    </thead>
    <tbody>
        <tr class="row_recap">
            <th scope='row' colspan='${ "6" if is_admin_view else "5" }' class='col_text'>Total</td>
            <td class='col_number'>${api.format_amount(totalht)}&nbsp;€</td>
            <td class='col_number'>${api.format_amount(totaltva)}&nbsp;€</td>
            <td class='col_number'>${api.format_amount(totalttc)}&nbsp;€</td>
            <td colspan='3'></td>
        </tr>
        % for supplier_invoice in records:
            <tr class='tableelement' id="${supplier_invoice.id}">
                <% url = request.route_path("/supplier_invoices/{id}", id=supplier_invoice.id) %>
                <% onclick = "document.location='{url}'".format(url=url) %>
                <% tooltip_title = "Cliquer pour voir ou modifier la facture « " + supplier_invoice.remote_invoice_number + " »" %>
                <td class="col_status" onclick="${onclick}" title="${api.format_status(supplier_invoice)} - ${tooltip_title}">
                    <span class="icon status ${supplier_invoice.global_status}">${api.icon(api.status_icon(supplier_invoice))}</span>
                </td>
                <td class="col_text document_number" onclick="${onclick}" title="${tooltip_title}">${supplier_invoice.official_number}</td>
                % if is_admin_view:
                    <td class="col_text" onclick="${onclick}" title="${tooltip_title}">
                        <% company_url = request.route_path('/companies/{id}', id=supplier_invoice.company.id) %>
                        % if request.has_permission('view.company', supplier_invoice.company):
                            <a href="${company_url}">${supplier_invoice.company.full_label | n}</a>
                            % if request.has_permission('admin_company', supplier_invoice.company):
                                ${company_list_badges(supplier_invoice.company)}
                            % endif
                        % else:
                            ${supplier_invoice.company.full_label | n}
                        % endif
                    </td>
                % endif
                <td class="col_date" onclick="${onclick}" title="${tooltip_title}">${api.format_date(supplier_invoice.date)}</td>
                <td class="col_text">
                    <a href="${url}" title="${tooltip_title}" aria-label="${tooltip_title}">
                        ${supplier_invoice.remote_invoice_number}
                    </a>
                </td>
                % if not is_supplier_view:
                <td class="col_text" onclick="${onclick}" title="${tooltip_title}">${supplier_invoice.supplier_label}</td>
                % endif
                <td class="col_number" onclick="${onclick}" title="${tooltip_title}">${api.format_amount(supplier_invoice.total_ht)}</td>
                <td class="col_number" onclick="${onclick}" title="${tooltip_title}">${api.format_amount(supplier_invoice.total_tva)}</td>
                <td class="col_number" onclick="${onclick}" title="${tooltip_title}">${api.format_amount(supplier_invoice.total)}</td>
                <td class="col_number" onclick="${onclick}" title="${tooltip_title}">${supplier_invoice.cae_percentage} %</td>
                ${request.layout_manager.render_panel('action_buttons_td', links=stream_actions(supplier_invoice))}
            </tr>
        % endfor
% else:
<table>
    <tbody>
        <tr>
            <td class='col_text'>
                <em>
                % if is_search_filter_active:
                    Aucune facture fournisseur correspondant à ces critères.
                % else:
                    Aucune facture fournisseur pour linstant.
                % endif
                </em>
            </td>
        </tr>
% endif
    % if records:
        <tfoot>
            <tr class="row_recap">
                <th scope='row' colspan='${ "6" if is_admin_view else "5" }' class='col_text'>Total</td>
                <td class='col_number'>${api.format_amount(totalht)}&nbsp;€</td>
                <td class='col_number'>${api.format_amount(totaltva)}&nbsp;€</td>
                <td class='col_number'>${api.format_amount(totalttc)}&nbsp;€</td>
                <td colspan='3'></td>
            </tr>
        </tfoot>
    % endif
    </tbody>
</table>
