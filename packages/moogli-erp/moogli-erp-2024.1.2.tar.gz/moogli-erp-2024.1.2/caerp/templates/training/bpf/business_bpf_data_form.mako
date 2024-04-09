<%doc>
    BPF edition for a given business and fiscal year
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/utils.mako" name="utils" />
<%block name='mainblock'>
        ${request.layout_manager.render_panel(
        'help_message_panel',
        parent_tmpl_dict=context.kwargs
    )}
<div class="separate_bottom content_vertical_padding">
	<h2>${title}</h2>
</div>
<div>
	<p>
		Ces données seront agrégées avec celles des autres formations de la même année pour produire le bilan pédagogique de formation.
	</p>
    ${form|n}
</div>
% if not is_creation_form:
<div class="separate_top content_vertical_padding">
	<h2>Autres années</h2>
</div>
<div>
% if len(other_bpf_datas) > 0:
	<p>
		Cette formation a des données BPF sur d’autres années :
		% for bpf_data, link in other_bpf_datas:
			<a href="${link}">${bpf_data.financial_year}</a>
		% endfor
		<br />
		${new_bpfdata_menu.render(request)|n}
	</p>
% else:
	<p>
		Si votre formation s’étend sur plusieurs années fiscales, il faut
		renseigner une fiche BPF par année.
		<br />
		${new_bpfdata_menu.render(request)|n}
	</p>
% endif
</div>
<div class="separate_top content_vertical_padding">
	<%utils:post_action_btn url="${delete_link}" icon="trash-alt"
	  _class="btn negative">
		Supprimer les données
		${context_model.financial_year}
	</%utils:post_action_btn>
</div>
% endif

</%block>
<%block name='footerjs'>
    new SubContractFields(
      "[name='has_subcontract']",
      [
        "[name='has_subcontract_amount']",
        "[name='has_subcontract_hours']",
        "[name='has_subcontract_headcount']",
      ]
    )
    new TraineeTypeFields(
      "[name=trainee_type_id]",
      [
        ".item-trainee_types [name=total_hours]",
        ".item-trainee_types [name=headcount]",
      ]
    )

    new SubContractTotalsLink(
      "[name='has_subcontract']",
      [
		{
		  src: "[name=headcount]",
		  target: "[name=has_subcontract_headcount]",
		},
		{
		  src: "[name=total_hours]",
		  target: "[name=has_subcontract_hours]",
		},
      ]
    )

</%block>
