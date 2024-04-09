<%inherit file="${context['main_template'].uri}" />

<%block name="mainblock">
<% task=request.context %>
<div id="documents">
<div class="separate_block limited_width width60 content_padding task_view tab_preview" tabindex="0">
    ${request.layout_manager.render_panel('task_html', context=task)}
</div>
</div>
</%block>