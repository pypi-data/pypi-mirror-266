<%inherit file="/layouts/default.mako" />
<%block name='actionmenucontent'>
% if layout.close_button:
<div class='layout flex main_actions'>
	<div role="group">
		${request.layout_manager.render_panel(layout.close_button.panel_name, context=layout.close_button)}
	</div>
</div>
% endif
</%block>

<%block name="headtitle">
<h1>
    ${layout.current_business_object.business_type.label}  : ${layout.current_business_object.name}
</h1>
</%block>

<%block name='content'>
<% business = layout.current_business_object %>
<div class="totals grand-total">
	<div class="layout flex">
		<div>
			<p>
				<strong>Nom :</strong> 
				${business.name}
				% if request.has_permission("edit.business", business):
				<a
					class='btn icon only unstyled'
					href="${layout.edit_url}"
					title="Modifier le nom de cette affaire"
					aria-label="Modifier le nom de cette affaire"
				>
                    ${api.icon('pen')}
				</a>
				% endif
			</p>
		% if layout.current_business_object.closed:
			<p>
				<span class="icon status closed">
					${api.icon('lock')}
				</span>
				Cette affaire est clôturée
			</p>
		% endif
			<p 
				title="${api.format_indicator_status(business.status)}"
				aria-label="${api.format_indicator_status(business.status)}"
				>
				<span class='icon status ${api.indicator_status_css(business.status)}'>
                    ${api.icon(api.indicator_status_icon(business.status))}
				</span>
				% if business.status == 'success':
					Cette affaire est complète
				% else:
					Des éléménts sont manquants dans cette affaire
				% endif
			</p>
		</div>
		<div>
			<h4 class="content_vertical_padding">Totaux</h4>
            ${request.layout_manager.render_panel('business_metrics_totals', instance=business, tva_on_margin=business.business_type.tva_on_margin)}
		</div>
	</div>
</div>
<div>
    <div class='tabs'>
		<%block name='rightblock'>
			${request.layout_manager.render_panel('tabs', layout.businessmenu)}
		</%block>
    </div>
    <div class='tab-content'>
		<%block name='mainblock'>
			Main
		</%block>
   </div>
</div>
</%block>
