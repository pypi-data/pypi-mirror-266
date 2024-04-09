<%inherit file="${context['main_template'].uri}" />
<%namespace name="utils" file="/base/utils.mako" />
<%block name='mainblock'>
<div id="overview_tab">
<% business = layout.current_business_object %>
    % if business.closed:
    <div class='alert alert-success'>
        <span class="icon">
        ${api.icon('success')}
        </span>
        Cette affaire est clôturée
    </div>
    % endif

    <div class='content_vertical_padding'>
        % if not estimations:
        <p>
            <em>Aucun devis n’est associé à cette affaire</em>
        </p>
        % else:
        <h3>Devis de référence</h3>

        <div class='table_container'>
            <table>
                <thead>
                    <tr>
                        <th scope="col" class='col_text'>
                        Nom
                        </th>
                        <th scope="col" class='col_text'>
                        Statut
                        </th>
                        <th scope="col" class='col_number' title="Montant Hors Taxes" aria-label="Montant Hors Taxes">
                        H<span class="screen-reader-text">ors </span>T<span class="screen-reader-text">axes</span>
                        </th>
                        <th scope="col" class="col_actions width_two" title="Actions">
                        <span class="screen-reader-text">Actions</span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    % for estimation in estimations:
                    <tr>
                        <td class='col_text'>
                            <a
                                class="link"
                                href="${request.route_path('/estimations/{id}', id=estimation.id)}"
                                >
                                ${estimation.name} (<small>${estimation.internal_number}</small>)
                            </a>
                        </td>
                        <td class='col_text'>
                            ${api.format_status(estimation)}
                        </td>
                        <td class='col_number'>
                            ${api.format_amount(estimation.ht, precision=5) | n}&nbsp;€
                        </td>
                        <td class='col_actions width_two'>
                            <div class='btn-group'>
                                <a
                                    class='btn icon only'
                                    href="${api.task_url(estimation)}"
                                    title="Voir le devis"
                                    aria-label="Voir le devis"
                                    >
                                    ${api.icon('arrow-right')}
                                </a>
                                <a
                                    class='btn icon only'
                                    href="${api.task_url(estimation, suffix='.pdf')}"
                                    title="Télécharger le PDF du devis"
                                    aria-label="Télécharger le PDF du devis"
                                    >
                                    ${api.icon('file-pdf')}
                                </a>
                            </div>
                        </td>
                        </tr>
                    % endfor
                </tbody>
            </table>
        % endif
        % if estimation_add_link:
        ${request.layout_manager.render_panel('post_button', context=estimation_add_link)}
        % endif
    </div>
    <div class='content_vertical_padding'>
        <h3>Facturation</h3>
        <br/>
        % if switch_invoicing_mode_link:
        ${request.layout_manager.render_panel(switch_invoicing_mode_link.panel_name, context=switch_invoicing_mode_link)}
        % endif
        % for link in invoicing_links:
        ${request.layout_manager.render_panel(link.panel_name, context=link)}
        % endfor
    </div>
    % if payment_deadlines:
    <div class='separate_top content_vertical_padding'>
        <h3>Échéances de paiement</h3>
        <p>
            <em>Reste à facturer : ${api.format_amount(business.amount_to_invoice('ttc'), precision=5) | n}&nbsp;€ TTC</em>
        </p>
        <div class='table_container'>
            <table>
                <thead>
                    <tr>
                        <th scope="col" class='col_text'>
                            Échéance
                        </th>
                        <th scope="col" class='col_text'>
                            Facture
                        </th>
                        <th scope="col" class='col_number' title="Montant Toutes Taxes Comprises" aria-label="Montant Toutes Taxes Comprises" >
                            TTC
                        </th>
                        <th scope="col" class="col_actions" title="Actions">
                        <span class="screen-reader-text">Actions</span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                % for deadline in payment_deadlines:
                <% url = request.route_path(invoice_deadline_route, id=business.id, deadline_id=deadline.id) %>
                    <tr>
                        <th scope="row">
                            % if deadline.deposit:
                                Facture d’acompte ${deadline.estimation.deposit}&nbsp;%
                            % else:
                                ${deadline.payment_line.description}
                            % endif
                        </th>
                        <td class="col_text">
                            % if deadline.invoice_id:
                                <a class="icon" href="${request.route_path('/invoices/{id}', id=deadline.invoice_id)}">
                                    ${api.icon('file-invoice-euro')}
                                    ${deadline.invoice.name} (${api.format_status(deadline.invoice)})
                                </a>
                            % elif not deadline.deposit and deadline.payment_line.date:
                                Facturation prévue le ${api.format_date(deadline.payment_line.date)}
                            % else:
                                En attente de facturation
                            % endif
                        </td>
                        <td class="col_number">
                            % if deadline.deposit:
                                ${api.format_amount(deadline.estimation.deposit_amount_ttc(), precision=5) | n}&nbsp;€
                            % else:
                                ${api.format_amount(deadline.payment_line.amount, precision=5) | n}&nbsp;€
                            % endif
                        </td>
                        <td class="col_actions">
                            % if deadline.invoice_id:
                                % if not business.closed and business.invoicing_mode == 'classic':
                                    <%utils:post_action_btn url="${url}" icon="file-redo" _class="btn" title="Re-générer la facture" aria-label="Re-générer la facture">
                                        Re-générer
                                    </%utils:post_action_btn>
                                % endif
                            % else:
                                % if not business.closed:
                                    <%utils:post_action_btn url="${url}" icon="file-invoice-euro" _class="btn">
                                        Générer la facture
                                    </%utils:post_action_btn>
                                % endif
                            % endif
                        </td>
                    </tr>
                % endfor
                </tbody>
            </table>
        </div>
    </div>
    % endif

    ## Facturation à l'avnancement uniquement
    % if invoice_list:
    <div class='content_vertical_padding'>
        <h3>Factures</h3>
        <p>
            <em>Reste à facturer : ${api.format_amount(business.amount_to_invoice('ht'), precision=5) | n}&nbsp;€ HT</em>
        </p>
        <div class='table_container'>
            <table>
                <thead>
                    <tr>
                        <th scope='col' class='col_text'>
                        Nom
                        </th>
                        <th scope='col' class='col_text'>
                        Statut
                        </th>
                        <th scope='col' class='col_number' title='Montant Hors Taxes' aria-label='Montant Hors Taxes'>
                        H<span class='screen-reader-text'>ors </span>T<span class='screen-reader-text'>axes</span>
                        </th>
                        <th scope='col' class='col_actions width_two' title='Actions'>
                        <span class='screen-reader-text'>Actions</span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    % for invoice in invoice_list:
                    <tr>
                        <td class='col_text'>${invoice.name}</td>
                        <td class='col_text'>${api.format_status(invoice)}</td>
                        <td class='col_number'>${api.format_amount(invoice.ht, precision=5)}&nbsp;€</td>
                        <td class='col_actions width_two'>
                            <div class='btn-group'>
                                <a
                                    class='btn icon only'
                                    href="${api.task_url(invoice)}"
                                    title="Voir la facture"
                                    aria-label="Voir la facture"
                                    >
                                    ${api.icon('arrow-right')}
                                </a>
                                <a
                                    class='btn icon only'
                                    href="${api.task_url(invoice, suffix='.pdf')}"
                                    title="Télécharger le PDF de la facture"
                                    aria-label="Télécharger le PDF de la facture"
                                    >
                                    ${api.icon('file-pdf')}
                                </a>
                            </div>
                        </td>
                    </tr>
                    % endfor
                </tbody>
            </table>
        </div>
    </div>
    %endif

    <div class='separate_top content_vertical_padding'>
        % if file_requirements or custom_indicators:
        <h3>Indicateurs</h3>
        <div class="table_container">
            <table>
                <tbody>
                % if custom_indicators:
                    <tr>
                        <th scope="col" class="col_status" title="Statut"><span class="screen-reader-text">Statut</span></th>
                        <th scope="col" class="col_status" title="Domaine d’application de l’indicateur"><span class="screen-reader-text">Domaine d’application de l’indicateur</span></th>
                        <th scope="col" class="col_text">Libellé</th>
                        <th scope="col" class="col_actions width_two" title="Actions">
                            <span class="screen-reader-text">Actions</span>
                        </th>
                    </tr>
                </tbody>
                <tbody>
                    % for indicator in custom_indicators:
                        ${request.layout_manager.render_panel('custom_indicator', indicator=indicator)}
                    % endfor
                </tbody>
                % endif
                % if file_requirements:
                <tbody>
                    <tr>
                    <% business_file_status = business.get_file_requirements_status() %>
                        <td class="col_status" >
                            <span class='icon status ${api.indicator_status_css(business_file_status)}'>
                                ${api.icon(api.indicator_status_icon(business_file_status))}
                            </span>
                        </td>
                        <td class='col_status'>
                        </td>
                        <td class="col_text">
                            % if status == 'danger':
                            Des documents sont manquants
                            % elif status == 'warning':
                            Des documents sont recommandés
                            % else:
                            Tous les fichiers ont été fournis
                            % endif
                        </td>
                        <td class='col_actions width_two'>
                            ${request.layout_manager.render_panel(file_tab_link.panel_name, context=file_tab_link)}
                        </td>
                    </tr>
                % endif
                </tbody>
            </table>
        </div>
        % endif
    </div>
</div>
</%block>
