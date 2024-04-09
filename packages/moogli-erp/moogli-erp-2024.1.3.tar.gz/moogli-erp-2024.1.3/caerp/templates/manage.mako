<%inherit file="${context['main_template'].uri}" />

<%block name='afteractionmenu'>
<div class='row'>
    % if request.has_module('activity'):
    ${request.layout_manager.render_panel('manage_dashboard_activity_resume')}
    % endif
</div>
</%block>
<%block name="content">
<div class='layout flex dashboard'>
    <div class='columns'>

        <!-- CENTRE DE VALIDATION -->
        % if request.has_permission("manage"):
            <div class='dash_elem'>
                <h2>
                    <span class='icon'>${api.icon('check-circle')}</span>
                    <span>Centre de validation</span>
                </h2>
                <div class='panel-body'>
                    <ul class="layout flex favourites">
                        % for button in shortcuts:
                        <li>
                            <a class="btn btn-primary" title="${button.title}" href="${button.url}">
                                ${api.icon(button.icon)}
                                ${button.text}
                            </a>
                        </li>
                        % endfor
                    </ul>
                </div>
            </div>
        % endif


        <!-- DOCUMENTS EN ATTENTE DE VALIDATION -->
        % if request.has_permission("valid.estimation"):
            ${request.layout_manager.render_panel('manage_dashboard_estimations')}
        % endif
        % if request.has_permission('valid.invoice'):
            ${request.layout_manager.render_panel('manage_dashboard_invoices')}
        % endif
        % if request.has_module('supply.orders') and \
        request.has_module('supply.invoices') and \
        request.has_permission('valid.supplier_order'):
            ${request.layout_manager.render_panel('manage_dashboard_supply')}
        % endif


        <!-- RENDEZ-VOUS / ACTIVITES A VENIR -->
        % if request.has_module('accompagnement'):
            ${request.layout_manager.render_panel('manage_dashboard_activities')}
        % endif

        <!-- NOTES DE DEPENSE EN ATTENTE DE VALIDATION -->
        % if request.has_module('expenses') and request.has_permission('admin_expense'):
            ${request.layout_manager.render_panel('manage_dashboard_expenses')}
        % endif

    </div>
</div>
</%block>
